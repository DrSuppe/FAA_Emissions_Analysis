"""Core data structures for combustor-to-FTIR simulation records."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, List

import pandas as pd


@dataclass(frozen=True)
class MeasurementPoint:
    """Single station reading or inferred state."""

    timestamp: pd.Timestamp
    location: str
    distance_m: float
    temperature_k: float
    pressure_pa: float
    mass_flow_kg_s: float
    species_mole_fraction: Dict[str, float]


@dataclass(frozen=True)
class SimulationFrame:
    """Container for trajectory data in tabular form."""

    dataframe: pd.DataFrame

    required_columns: List[str] = (
        "timestamp",
        "time_s",
        "location",
        "distance_m",
        "temperature_k",
        "pressure_pa",
        "mass_flow_kg_s",
    )

    def validate(self) -> None:
        missing = [col for col in self.required_columns if col not in self.dataframe.columns]
        if missing:
            msg = f"Missing required columns: {missing}"
            raise ValueError(msg)
