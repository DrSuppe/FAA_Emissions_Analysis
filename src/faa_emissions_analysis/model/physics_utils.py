"""Core physics helper functions for the forward model."""

from __future__ import annotations

from typing import Any, Iterable, Mapping

import numpy as np
import pandas as pd


def normalize_composition(comp: Mapping[str, float]) -> dict[str, float]:
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


def mix_compositions(
    base: Mapping[str, float],
    added: Mapping[str, float] | None,
    mix_fraction: float,
) -> dict[str, float]:
    if not added or mix_fraction <= 0.0:
        return normalize_composition(base)

    x = float(np.clip(mix_fraction, 0.0, 0.999))
    merged: dict[str, float] = {}
    keys = set(base.keys()) | set(added.keys())
    for key in keys:
        merged[key] = (1.0 - x) * float(base.get(key, 0.0)) + x * float(added.get(key, 0.0))
    return normalize_composition(merged)


def state_from_row(
    row: pd.Series,
    species: Iterable[str],
    fallback: Mapping[str, float],
) -> dict[str, Any]:
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
        "composition": normalize_composition(composition),
    }
