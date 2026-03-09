"""YAML config wiring for ingestion pipeline."""

from __future__ import annotations

from pathlib import Path
from typing import Any, Mapping

import pandas as pd
import yaml

from .align import align_station_and_ftir
from .loaders import load_source_frame
from .types import SourceConfig


def source_from_dict(payload: Mapping[str, Any], label: str) -> SourceConfig:
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

    station_cfg = source_from_dict(config["station"], "station")
    ftir_cfg = source_from_dict(config["ftir"], "ftir")
    tolerance_s = float(config.get("align", {}).get("tolerance_s", 0.6))

    station_df = load_source_frame(station_cfg)
    ftir_df = load_source_frame(ftir_cfg)
    aligned = align_station_and_ftir(station_df, ftir_df, tolerance_s=tolerance_s)
    return station_df, ftir_df, aligned
