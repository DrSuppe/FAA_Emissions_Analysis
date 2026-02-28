"""Data ingestion and timestamp alignment utilities."""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Mapping

import pandas as pd
import yaml


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


def _read_table(path: Path, sheet_name: str | int | None = None) -> pd.DataFrame:
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


def _parse_time_column(values: pd.Series) -> tuple[pd.Series, pd.Series]:
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


def _resolve_field(
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

    df = _read_table(config.path, config.sheet_name).copy()

    if config.time_column not in df.columns:
        raise ValueError(f"Time column '{config.time_column}' not found in {config.path}")

    timestamp, time_s = _parse_time_column(df[config.time_column])
    out = pd.DataFrame({"timestamp": timestamp, "time_s": time_s})

    for standard_col in ("location", "distance_m", "temperature_k", "pressure_pa", "mass_flow_kg_s"):
        raw_col = config.column_map.get(standard_col)
        default_value: Any = None
        if standard_col == "location":
            default_value = config.default_location or config.dataset_label
        if standard_col == "distance_m":
            default_value = config.default_distance_m
        out[standard_col] = _resolve_field(df, raw_col, default_value, len(df))

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


def align_station_and_ftir(
    station_df: pd.DataFrame,
    ftir_df: pd.DataFrame,
    tolerance_s: float = 0.6,
) -> pd.DataFrame:
    """Nearest-neighbor time alignment from FTIR timestamps to station state."""

    if "time_s" not in station_df.columns or "time_s" not in ftir_df.columns:
        raise ValueError("Both station_df and ftir_df must include 'time_s'.")

    left = ftir_df.sort_values("time_s").copy()
    right = station_df.sort_values("time_s").copy()

    aligned = pd.merge_asof(
        left,
        right,
        on="time_s",
        direction="nearest",
        tolerance=tolerance_s,
        suffixes=("_ftir", "_station"),
    )
    return aligned


def _source_from_dict(payload: Mapping[str, Any], label: str) -> SourceConfig:
    return SourceConfig(
        path=Path(payload["path"]),
        time_column=payload["time_column"],
        sheet_name=payload.get("sheet_name"),
        column_map=payload.get("column_map", {}),
        species_map=payload.get("species_map", {}),
        default_location=payload.get("default_location"),
        default_distance_m=payload.get("default_distance_m"),
        dataset_label=label,
    )


def load_and_align_inputs(config_path: Path) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    """Load station + FTIR sources using YAML config and return aligned dataframes."""

    with config_path.open("r", encoding="utf-8") as handle:
        config = yaml.safe_load(handle)

    station_cfg = _source_from_dict(config["station"], "station")
    ftir_cfg = _source_from_dict(config["ftir"], "ftir")
    tolerance_s = float(config.get("align", {}).get("tolerance_s", 0.6))

    station_df = load_source_frame(station_cfg)
    ftir_df = load_source_frame(ftir_cfg)
    aligned = align_station_and_ftir(station_df, ftir_df, tolerance_s=tolerance_s)
    return station_df, ftir_df, aligned
