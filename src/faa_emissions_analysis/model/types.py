"""Dataclasses for forward-model configuration."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Iterable, Mapping


@dataclass(frozen=True)
class RestrictionConfig:
    """Compressible restriction used for probe ports and venturi."""

    area_m2: float
    discharge_coeff: float = 0.85
    gamma: float | None = None  # None → computed from gas cp/cv at runtime (recommended)
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
