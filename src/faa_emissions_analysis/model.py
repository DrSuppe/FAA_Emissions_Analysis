"""Cantera forward-model skeleton for injector-to-FTIR path simulation."""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Iterable, Mapping

import numpy as np
import pandas as pd
import yaml


@dataclass(frozen=True)
class RestrictionConfig:
    """Compressible restriction used for probe ports and venturi."""

    area_m2: float
    discharge_coeff: float = 0.85
    gamma: float = 1.33
    downstream_pressure_pa: float | None = None


@dataclass(frozen=True)
class StageConfig:
    """One sequential stage in the reactor/line path."""

    name: str
    distance_m: float
    residence_time_s: float
    pressure_drop_pa: float = 0.0
    wall_temperature_k: float | None = None
    ua_w_m2_k: float = 0.0
    area_m2: float = 1.0
    mix_stream: Mapping[str, float] | None = None
    mix_fraction: float = 0.0
    restriction: RestrictionConfig | None = None


@dataclass(frozen=True)
class ForwardModelConfig:
    """Model settings for Cantera simulation."""

    mechanism: str = "gri30.yaml"
    tracked_species: Iterable[str] = field(default_factory=lambda: ("O2", "N2", "H2O", "CO2", "CO", "NO", "NO2"))
    inlet_composition: Mapping[str, float] = field(default_factory=lambda: {"O2": 0.21, "N2": 0.79})
    stages: tuple[StageConfig, ...] = field(default_factory=tuple)


def _normalize_composition(comp: Mapping[str, float]) -> dict[str, float]:
    values = {k: max(float(v), 0.0) for k, v in comp.items() if float(v) > 0.0}
    if not values:
        raise ValueError("Composition map is empty or non-positive.")
    total = sum(values.values())
    return {k: v / total for k, v in values.items()}


def critical_pressure_ratio(gamma: float) -> float:
    return (2.0 / (gamma + 1.0)) ** (gamma / (gamma - 1.0))


def compressible_orifice_mdot(
    p_up_pa: float,
    p_down_pa: float,
    temperature_k: float,
    area_m2: float,
    discharge_coeff: float,
    gamma: float,
    gas_constant_j_kgk: float,
) -> tuple[float, bool]:
    """Return mass flow rate and choking status for an idealized restriction."""

    p_up = max(p_up_pa, 1.0)
    p_down = max(min(p_down_pa, p_up), 1.0)
    t_up = max(temperature_k, 1.0)
    pr = p_down / p_up
    crit = critical_pressure_ratio(gamma)

    if pr <= crit:
        mdot = (
            discharge_coeff
            * area_m2
            * p_up
            * np.sqrt(gamma / (gas_constant_j_kgk * t_up))
            * (2.0 / (gamma + 1.0)) ** ((gamma + 1.0) / (2.0 * (gamma - 1.0)))
        )
        return float(mdot), True

    bracket = (pr ** (2.0 / gamma)) - (pr ** ((gamma + 1.0) / gamma))
    mdot = (
        discharge_coeff
        * area_m2
        * p_up
        * np.sqrt(2.0 * gamma / (gas_constant_j_kgk * t_up * (gamma - 1.0)) * max(bracket, 0.0))
    )
    return float(mdot), False


def _mix_compositions(
    base: Mapping[str, float],
    added: Mapping[str, float] | None,
    mix_fraction: float,
) -> dict[str, float]:
    if not added or mix_fraction <= 0.0:
        return _normalize_composition(base)

    x = float(np.clip(mix_fraction, 0.0, 0.999))
    merged: dict[str, float] = {}
    keys = set(base.keys()) | set(added.keys())
    for key in keys:
        merged[key] = (1.0 - x) * float(base.get(key, 0.0)) + x * float(added.get(key, 0.0))
    return _normalize_composition(merged)


def _state_from_row(row: pd.Series, species: Iterable[str], fallback: Mapping[str, float]) -> dict[str, Any]:
    composition = {}
    for sp in species:
        if sp in row.index and pd.notna(row[sp]):
            composition[sp] = float(row[sp])
    if not composition:
        composition = dict(fallback)

    return {
        "temperature_k": float(row["temperature_k"]),
        "pressure_pa": float(row["pressure_pa"]),
        "mass_flow_kg_s": float(row["mass_flow_kg_s"]),
        "composition": _normalize_composition(composition),
    }


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
        mixed = _mix_compositions(state["composition"], stage.mix_stream, stage.mix_fraction)
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
            state = _state_from_row(row, tracked, self.config.inlet_composition)
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


def _parse_stage(payload: Mapping[str, Any]) -> StageConfig:
    restriction = payload.get("restriction")
    restriction_cfg = None
    if restriction:
        restriction_cfg = RestrictionConfig(
            area_m2=float(restriction["area_m2"]),
            discharge_coeff=float(restriction.get("discharge_coeff", 0.85)),
            gamma=float(restriction.get("gamma", 1.33)),
            downstream_pressure_pa=(
                float(restriction["downstream_pressure_pa"])
                if restriction.get("downstream_pressure_pa") is not None
                else None
            ),
        )

    return StageConfig(
        name=str(payload["name"]),
        distance_m=float(payload["distance_m"]),
        residence_time_s=float(payload["residence_time_s"]),
        pressure_drop_pa=float(payload.get("pressure_drop_pa", 0.0)),
        wall_temperature_k=(
            float(payload["wall_temperature_k"]) if payload.get("wall_temperature_k") is not None else None
        ),
        ua_w_m2_k=float(payload.get("ua_w_m2_k", 0.0)),
        area_m2=float(payload.get("area_m2", 1.0)),
        mix_stream=payload.get("mix_stream"),
        mix_fraction=float(payload.get("mix_fraction", 0.0)),
        restriction=restriction_cfg,
    )


def load_forward_model_config(path: Path) -> ForwardModelConfig:
    with path.open("r", encoding="utf-8") as handle:
        payload = yaml.safe_load(handle)

    stages = tuple(_parse_stage(stage) for stage in payload["stages"])
    return ForwardModelConfig(
        mechanism=payload.get("mechanism", "gri30.yaml"),
        tracked_species=tuple(payload.get("tracked_species", ("O2", "N2", "CO2", "H2O", "CO", "NO", "NO2"))),
        inlet_composition=payload.get("inlet_composition", {"O2": 0.21, "N2": 0.79}),
        stages=stages,
    )
