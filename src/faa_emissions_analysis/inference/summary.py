"""Posterior sample summarization utilities."""

from __future__ import annotations

from typing import Iterable

import numpy as np
import pandas as pd


def posterior_summary_table(samples: dict[str, np.ndarray], species: Iterable[str]) -> pd.DataFrame:
    """Create percentile summary table from NUTS samples."""

    species = list(species)
    rows: list[dict[str, float | str]] = []

    for param, arr in samples.items():
        if arr.ndim == 1:
            arr = arr[:, None]
        for idx, sp in enumerate(species):
            col = arr[:, idx] if idx < arr.shape[1] else arr[:, 0]
            rows.append(
                {
                    "parameter": param,
                    "species": sp,
                    "mean": float(np.mean(col)),
                    "p05": float(np.percentile(col, 5.0)),
                    "p50": float(np.percentile(col, 50.0)),
                    "p95": float(np.percentile(col, 95.0)),
                }
            )

    return pd.DataFrame(rows)
