"""Type definitions for ingestion configuration."""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Mapping


STANDARD_COLUMNS = (
    "timestamp",
    "time_s",
    "location",
    "distance_m",
    "temperature_k",
    "pressure_pa",
    "mass_flow_kg_s",
)


@dataclass(frozen=True)
class SourceConfig:
    """Configuration for one tabular source."""

    path: Path
    time_column: str
    sheet_name: str | int | None = None
    column_map: Mapping[str, str] = field(default_factory=dict)
    species_map: Mapping[str, str] = field(default_factory=dict)
    default_location: str | None = None
    default_distance_m: float | None = None
    dataset_label: str = "source"
