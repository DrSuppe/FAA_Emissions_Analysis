"""Alignment helpers for predicted and observed FTIR trajectories."""

from __future__ import annotations

from typing import Iterable

import pandas as pd


def align_predicted_and_observed(
    predicted_df: pd.DataFrame,
    observed_df: pd.DataFrame,
    species: Iterable[str],
    predicted_location: str,
    observed_location: str = "FTIR",
    tolerance_s: float = 0.6,
) -> pd.DataFrame:
    """Nearest-time alignment between model prediction and FTIR observations."""

    species = list(species)
    need_cols = {"time_s", "location", *species}
    for name, frame in (("predicted_df", predicted_df), ("observed_df", observed_df)):
        missing = need_cols - set(frame.columns)
        if missing:
            raise ValueError(f"{name} is missing columns: {sorted(missing)}")

    pred_slice = predicted_df[predicted_df["location"] == predicted_location].copy()
    obs_slice = observed_df[observed_df["location"] == observed_location].copy()

    pred_cols = ["time_s", *species]
    obs_cols = ["time_s", *species]
    aligned = pd.merge_asof(
        obs_slice.sort_values("time_s")[obs_cols],
        pred_slice.sort_values("time_s")[pred_cols],
        on="time_s",
        direction="nearest",
        tolerance=tolerance_s,
        suffixes=("_obs", "_pred"),
    )
    return aligned.dropna().reset_index(drop=True)
