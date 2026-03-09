"""Heatmap-based spatiotemporal plots."""

from __future__ import annotations

from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd

from .utils import check_columns


def plot_spatiotemporal_heatmap(
    df: pd.DataFrame,
    value_col: str,
    out_file: Path,
    title: str | None = None,
    cmap: str = "viridis",
) -> None:
    """Create a distance-vs-time heatmap for a scalar state variable."""

    check_columns(df, ["time_s", "distance_m", value_col])
    pivot = (
        df.pivot_table(index="distance_m", columns="time_s", values=value_col, aggfunc="mean")
        .sort_index(axis=0)
        .sort_index(axis=1)
    )

    fig, ax = plt.subplots(figsize=(9, 4.5))
    mesh = ax.pcolormesh(
        pivot.columns.to_numpy(),
        pivot.index.to_numpy(),
        pivot.to_numpy(),
        shading="auto",
        cmap=cmap,
    )
    ax.set_xlabel("Time [s]")
    ax.set_ylabel("Distance from injector [m]")
    ax.set_title(title or f"{value_col} evolution")
    cbar = fig.colorbar(mesh, ax=ax)
    cbar.set_label(value_col)
    fig.tight_layout()
    fig.savefig(out_file, dpi=180)
    plt.close(fig)
