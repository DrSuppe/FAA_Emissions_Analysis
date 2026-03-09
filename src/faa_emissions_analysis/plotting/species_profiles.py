"""Species trajectory and distance-profile plots."""

from __future__ import annotations

from pathlib import Path
from typing import Iterable, Sequence

import matplotlib.pyplot as plt
import pandas as pd

from .utils import check_columns


def plot_species_time_traces(
    df: pd.DataFrame,
    species: Iterable[str],
    out_file: Path,
    location_col: str = "location",
    time_col: str = "time_s",
) -> None:
    """Plot species trajectories over time, grouped by station."""

    species = list(species)
    required_cols = [time_col, location_col, *species]
    check_columns(df, required_cols)

    grouped = (
        df.groupby([time_col, location_col], as_index=False)[species]
        .mean()
        .sort_values([location_col, time_col])
    )
    stations = grouped[location_col].unique().tolist()

    fig, axes = plt.subplots(len(species), 1, figsize=(11, 3.0 * len(species)), sharex=True)
    if len(species) == 1:
        axes = [axes]

    for ax, sp in zip(axes, species, strict=True):
        for station in stations:
            sub = grouped[grouped[location_col] == station]
            ax.plot(sub[time_col], sub[sp], label=station, linewidth=1.2)
        ax.set_ylabel(f"X({sp})")
        ax.grid(alpha=0.2)

    axes[-1].set_xlabel("Time [s]")
    axes[0].legend(loc="upper right", ncol=min(4, len(stations)))
    axes[0].set_title("Species evolution at stations")
    fig.tight_layout()
    fig.savefig(out_file, dpi=180)
    plt.close(fig)


def plot_species_distance_snapshots(
    df: pd.DataFrame,
    species: str,
    snapshot_times_s: Sequence[float],
    out_file: Path,
    time_col: str = "time_s",
    distance_col: str = "distance_m",
) -> None:
    """Plot species profile versus distance at selected times."""

    check_columns(df, [time_col, distance_col, species])
    if not snapshot_times_s:
        msg = "snapshot_times_s must not be empty"
        raise ValueError(msg)

    fig, ax = plt.subplots(figsize=(9, 4.5))
    for t in snapshot_times_s:
        nearest = df.iloc[(df[time_col] - t).abs().argsort()[:1]][time_col].iloc[0]
        sub = (
            df[df[time_col] == nearest]
            .groupby(distance_col, as_index=False)[species]
            .mean()
            .sort_values(distance_col)
        )
        ax.plot(sub[distance_col], sub[species], linewidth=1.4, label=f"t={nearest:.1f} s")

    ax.set_xlabel("Distance from injector [m]")
    ax.set_ylabel(f"X({species})")
    ax.set_title(f"{species} profiles along injector-to-FTIR path")
    ax.grid(alpha=0.2)
    ax.legend()
    fig.tight_layout()
    fig.savefig(out_file, dpi=180)
    plt.close(fig)
