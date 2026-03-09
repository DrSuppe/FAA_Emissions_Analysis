"""File readers and table normalizers for ingestion."""

from __future__ import annotations

from pathlib import Path
from typing import Any

import pandas as pd

from .types import SourceConfig


def read_table(path: Path, sheet_name: str | int | None = None) -> pd.DataFrame:
    if not path.exists():
        raise FileNotFoundError(f"Input file does not exist: {path}")

    suffix = path.suffix.lower()
    if suffix in {".xlsx", ".xls"}:
        try:
            return pd.read_excel(path, sheet_name=sheet_name)
        except ImportError as exc:
            raise ImportError(
                "Excel support requires 'openpyxl'. Install with: pip install openpyxl"
            ) from exc
    return pd.read_csv(path)


def parse_time_column(values: pd.Series) -> tuple[pd.Series, pd.Series]:
    if pd.api.types.is_numeric_dtype(values):
        time_s = pd.to_numeric(values, errors="coerce")
        timestamp = pd.to_datetime(time_s, unit="s", origin="unix", utc=True).dt.tz_localize(None)
        return timestamp, time_s

    timestamp = pd.to_datetime(values, errors="coerce")
    if timestamp.isna().all():
        raise ValueError("Failed to parse any timestamps in time column.")
    ref = timestamp.dropna().iloc[0]
    time_s = (timestamp - ref).dt.total_seconds()
    return timestamp, time_s


def resolve_field(
    df: pd.DataFrame,
    raw_col: str | None,
    default_value: Any,
    length: int,
) -> pd.Series:
    if raw_col and raw_col in df.columns:
        return df[raw_col]
    return pd.Series([default_value] * length)


def load_source_frame(config: SourceConfig) -> pd.DataFrame:
    """Load a source table and standardize core columns."""

    df = read_table(config.path, config.sheet_name).copy()

    if config.time_column not in df.columns:
        raise ValueError(f"Time column '{config.time_column}' not found in {config.path}")

    timestamp, time_s = parse_time_column(df[config.time_column])
    out = pd.DataFrame({"timestamp": timestamp, "time_s": time_s})

    for standard_col in ("location", "distance_m", "temperature_k", "pressure_pa", "mass_flow_kg_s"):
        raw_col = config.column_map.get(standard_col)
        default_value: Any = None
        if standard_col == "location":
            default_value = config.default_location or config.dataset_label
        if standard_col == "distance_m":
            default_value = config.default_distance_m
        out[standard_col] = resolve_field(df, raw_col, default_value, len(df))

    species_payload: dict[str, pd.Series] = {}
    for std_name, raw_name in config.species_map.items():
        if raw_name not in df.columns:
            raise ValueError(f"Species column '{raw_name}' was not found in {config.path}")
        species_payload[std_name] = pd.to_numeric(df[raw_name], errors="coerce")

    if species_payload:
        out = pd.concat([out, pd.DataFrame(species_payload)], axis=1)

    out["dataset"] = config.dataset_label
    out = out.sort_values("time_s").reset_index(drop=True)
    return out
