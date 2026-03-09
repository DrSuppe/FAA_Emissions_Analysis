"""Shared helpers for plotting routines."""

from __future__ import annotations

from pathlib import Path
from typing import Sequence

import pandas as pd


def check_columns(df: pd.DataFrame, columns: Sequence[str]) -> None:
    missing = [col for col in columns if col not in df.columns]
    if missing:
        msg = f"Dataframe is missing required columns: {missing}"
        raise ValueError(msg)


def ensure_outdir(path: Path) -> None:
    path.mkdir(parents=True, exist_ok=True)
