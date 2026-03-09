"""Stage-wise Cantera path model implementation."""

from __future__ import annotations

from typing import Any

import numpy as np
import pandas as pd

from .physics_utils import compressible_orifice_mdot, mix_compositions, state_from_row
from .types import ForwardModelConfig, StageConfig


class CanteraPathModel:
    """Sequential quasi-steady path model with Cantera reactors per stage."""

    def __init__(self, config: ForwardModelConfig):
        self.config = config
        try:
            import cantera as ct  # type: ignore
        except ImportError as exc:
            raise ImportError(
                "Cantera is required for CanteraPathModel. Install with: pip install cantera"
            ) from exc
        self.ct = ct

    def _advance_stage(self, state: dict[str, Any], stage: StageConfig) -> dict[str, Any]:
        ct = self.ct
        gas = ct.Solution(self.config.mechanism)
        mixed = mix_compositions(state["composition"], stage.mix_stream, stage.mix_fraction)
        gas.TPX = state["temperature_k"], state["pressure_pa"], mixed

        reactor = ct.IdealGasConstPressureReactor(gas, energy="on")

        if stage.wall_temperature_k is not None and stage.ua_w_m2_k > 0.0:
            env = ct.Solution(self.config.mechanism)
            env.TPX = stage.wall_temperature_k, max(state["pressure_pa"], 1.0), "N2:1.0"
            env_res = ct.Reservoir(env)
            ct.Wall(reactor, env_res, A=max(stage.area_m2, 1e-6), U=max(stage.ua_w_m2_k, 0.0))

        net = ct.ReactorNet([reactor])
        net.advance(max(stage.residence_time_s, 0.0))

        pressure_out = max(state["pressure_pa"] - stage.pressure_drop_pa, 1_000.0)
        gas_out = ct.Solution(self.config.mechanism)
        gas_out.TPX = reactor.T, pressure_out, reactor.thermo.X

        out_state = {
            "temperature_k": float(gas_out.T),
            "pressure_pa": float(gas_out.P),
            "mass_flow_kg_s": float(state["mass_flow_kg_s"]),
            "composition": {sp: float(gas_out[sp].X[0]) for sp in self.config.tracked_species if sp in gas_out.species_names},
            "restriction_choked": False,
            "restriction_mdot_cap_kg_s": np.nan,
        }

        if stage.restriction is not None:
            r_spec = ct.gas_constant / max(gas_out.mean_molecular_weight, 1e-12)
            p_down = stage.restriction.downstream_pressure_pa or max(gas_out.P - 100.0, 1.0)
            mdot_cap, choked = compressible_orifice_mdot(
                p_up_pa=float(gas_out.P),
                p_down_pa=float(p_down),
                temperature_k=float(gas_out.T),
                area_m2=float(stage.restriction.area_m2),
                discharge_coeff=float(stage.restriction.discharge_coeff),
                gamma=float(stage.restriction.gamma),
                gas_constant_j_kgk=float(r_spec),
            )
            out_state["restriction_choked"] = choked
            out_state["restriction_mdot_cap_kg_s"] = mdot_cap
            out_state["mass_flow_kg_s"] = float(min(out_state["mass_flow_kg_s"], mdot_cap))

        return out_state

    def simulate_timeseries(self, inlet_df: pd.DataFrame) -> pd.DataFrame:
        """Simulate every timestamp and emit stage-wise trajectories."""

        required = {"timestamp", "time_s", "temperature_k", "pressure_pa", "mass_flow_kg_s"}
        missing = required - set(inlet_df.columns)
        if missing:
            raise ValueError(f"inlet_df is missing required columns: {sorted(missing)}")

        rows: list[dict[str, Any]] = []
        tracked = list(self.config.tracked_species)

        for _, row in inlet_df.sort_values("time_s").iterrows():
            state = state_from_row(row, tracked, self.config.inlet_composition)
            for stage in self.config.stages:
                state = self._advance_stage(state, stage)
                rec: dict[str, Any] = {
                    "timestamp": row["timestamp"],
                    "time_s": float(row["time_s"]),
                    "location": stage.name,
                    "distance_m": stage.distance_m,
                    "temperature_k": state["temperature_k"],
                    "pressure_pa": state["pressure_pa"],
                    "mass_flow_kg_s": state["mass_flow_kg_s"],
                    "restriction_choked": state["restriction_choked"],
                    "restriction_mdot_cap_kg_s": state["restriction_mdot_cap_kg_s"],
                }
                for sp in tracked:
                    rec[sp] = float(state["composition"].get(sp, 0.0))
                rows.append(rec)

        return pd.DataFrame(rows)
