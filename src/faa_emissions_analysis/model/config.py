"""YAML loading/parsing for forward-model configuration."""

from __future__ import annotations

from pathlib import Path
from typing import Any, Mapping

from faa_emissions_analysis._yaml import load_yaml

from .types import ForwardModelConfig, RestrictionConfig, StageConfig


def parse_stage(payload: Mapping[str, Any]) -> StageConfig:
    restriction = payload.get("restriction")
    restriction_cfg = None
    if restriction:
        restriction_cfg = RestrictionConfig(
            area_m2=float(restriction["area_m2"]),
            discharge_coeff=float(restriction.get("discharge_coeff", 0.85)),
            gamma=float(restriction["gamma"]) if restriction.get("gamma") is not None else None,
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
    payload = load_yaml(path)

    stages = tuple(parse_stage(stage) for stage in payload["stages"])
    raw_species = payload.get("tracked_species", ("O2", "N2", "CO2", "H2O", "CO", "NO", "NO2"))
    return ForwardModelConfig(
        mechanism=payload.get("mechanism", "gri30.yaml"),
        tracked_species=tuple(raw_species),
        inlet_composition=payload.get("inlet_composition", {"O2": 0.21, "N2": 0.79}),
        stages=stages,
    )
