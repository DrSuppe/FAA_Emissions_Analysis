"""Alignment operations for station and FTIR time series."""

from __future__ import annotations

import pandas as pd


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
