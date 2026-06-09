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

    def flame_inlet_state(self) -> dict[str, Any]:
        """Build the reacting combustor inlet (fresh fuel/air at phi).

        Uses the HyChem A2 Jet-A + NOx mechanism (see MECHANISM_PROVENANCE.md).
        The inlet is a fresh, UNBURNED fuel/air mixture set by equivalence ratio
        via ``ct.Solution.set_equivalence_ratio`` at the configured air-preheat
        temperature and inlet pressure. The reacting stages then ignite and burn
        this mixture (energy='on'), so combustion products — including NO/NO2 —
        are genuine predictions rather than pass-through of already-burned gas.
        """
        ct = self.ct
        cfg = self.config
        if cfg.fuel_composition is None or cfg.equivalence_ratio is None:
            raise ValueError(
                "flame_inlet_state requires fuel_composition and equivalence_ratio "
                "to be set in the ForwardModelConfig."
            )
        gas = ct.Solution(cfg.mechanism)
        gas.set_equivalence_ratio(
            float(cfg.equivalence_ratio),
            dict(cfg.fuel_composition),
            dict(cfg.oxidizer_composition),
        )
        gas.TP = float(cfg.t_inlet_air_k), float(cfg.inlet_pressure_pa)
        # Mass flow seeds from the validation target (station mdot ~0.18 kg/s);
        # it is overwritten per-row in simulate_timeseries when available.
        return {
            "temperature_k": float(gas.T),
            "pressure_pa": float(gas.P),
            "mass_flow_kg_s": 0.18,
            "composition": {
                sp: float(gas.X[i]) for i, sp in enumerate(gas.species_names) if gas.X[i] > 0.0
            },
        }

    def _advance_stage(self, state: dict[str, Any], stage: StageConfig) -> dict[str, Any]:
        ct = self.ct

        # Prescribe outlet pressure before reactor init so kinetics run at the correct
        # operating pressure (matches physical station measurements when available).
        pressure_out = max(state["pressure_pa"] - stage.pressure_drop_pa, 1_000.0)

        gas = ct.Solution(self.config.mechanism)
        mixed = mix_compositions(state["composition"], stage.mix_stream, stage.mix_fraction)

        # Flame anchoring (pilot ignition). The HyChem A2 mechanism is HIGH-TEMPERATURE
        # only: a fresh fuel/air premix at ~700 K compressor-discharge temperature does
        # NOT autoignite within the few-ms stage residence time (ignition delay > 0.1 s
        # at 700 K; ~3 ms only above ~1100 K). A real pilot does not rely on autoignition
        # of cold premix — it is stabilized on a hot recirculation zone. We represent that
        # by starting the reactor of an UNBURNED fuel-bearing stage at the stage wall
        # (recirculation-zone) temperature when it is hotter than the incoming gas. This
        # ties ignition to an EXISTING config value (pilot wall T = 1400 K), not a new
        # free knob. See MECHANISM_PROVENANCE.md (validity range) and model/README.md.
        start_temp = state["temperature_k"]
        fuel_keys = set(self.config.fuel_composition or {})
        unburned_fuel = any(float(mixed.get(fk, 0.0)) > 1e-8 for fk in fuel_keys)
        if (
            unburned_fuel
            and stage.wall_temperature_k is not None
            and stage.wall_temperature_k > start_temp
        ):
            start_temp = float(stage.wall_temperature_k)

        gas.TPX = start_temp, pressure_out, mixed

        reactor = ct.IdealGasConstPressureReactor(gas, energy="on", clone=False)

        if stage.wall_temperature_k is not None and stage.ua_w_m2_k > 0.0:
            env = ct.Solution(self.config.mechanism)
            env.TPX = stage.wall_temperature_k, max(pressure_out, 1.0), "N2:1.0"
            env_res = ct.Reservoir(env)
            ct.Wall(reactor, env_res, A=max(stage.area_m2, 1e-6), U=max(stage.ua_w_m2_k, 0.0))

        net = ct.ReactorNet([reactor])
        net.advance(max(stage.residence_time_s, 0.0))

        gas_out = ct.Solution(self.config.mechanism)
        gas_out.TPX = reactor.T, pressure_out, reactor.phase.X

        out_state = {
            "temperature_k": float(gas_out.T),
            "pressure_pa": float(gas_out.P),
            "mass_flow_kg_s": float(state["mass_flow_kg_s"]),
            "composition": {
                sp: float(gas_out.X[gas_out.species_index(sp)])
                for sp in self.config.tracked_species
                if sp in gas_out.species_names
            },
            "restriction_choked": False,
            "restriction_mdot_cap_kg_s": np.nan,
        }

        if stage.restriction is not None:
            r_spec = ct.gas_constant / max(gas_out.mean_molecular_weight, 1e-12)
            # Use composition-derived gamma when not overridden in config.
            gamma = (
                float(stage.restriction.gamma)
                if stage.restriction.gamma is not None
                else float(gas_out.cp_mass / gas_out.cv_mass)
            )
            p_down = stage.restriction.downstream_pressure_pa or max(gas_out.P - 100.0, 1.0)
            mdot_cap, choked = compressible_orifice_mdot(
                p_up_pa=float(gas_out.P),
                p_down_pa=float(p_down),
                temperature_k=float(gas_out.T),
                area_m2=float(stage.restriction.area_m2),
                discharge_coeff=float(stage.restriction.discharge_coeff),
                gamma=gamma,
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

        # When a reacting fuel/air inlet is configured, every trajectory is
        # seeded with the SAME fresh fuel/air mixture (set by phi). The station
        # CSV is then the VALIDATION TARGET downstream, not the inlet — it only
        # supplies timestamp/time_s and the measured mass flow for transport.
        reacting = (
            self.config.fuel_composition is not None
            and self.config.equivalence_ratio is not None
        )
        flame_inlet = self.flame_inlet_state() if reacting else None

        for _, row in inlet_df.sort_values("time_s").iterrows():
            if reacting:
                state = {
                    "temperature_k": flame_inlet["temperature_k"],
                    "pressure_pa": flame_inlet["pressure_pa"],
                    "mass_flow_kg_s": float(row["mass_flow_kg_s"]),
                    "composition": dict(flame_inlet["composition"]),
                }
            else:
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
