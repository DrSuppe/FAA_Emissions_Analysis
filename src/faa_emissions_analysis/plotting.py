"""Plot utilities for spatiotemporal emissions trajectories."""

from __future__ import annotations

from pathlib import Path
from typing import Iterable, Sequence

import matplotlib.pyplot as plt
import pandas as pd


def _check_columns(df: pd.DataFrame, columns: Sequence[str]) -> None:
    missing = [col for col in columns if col not in df.columns]
    if missing:
        msg = f"Dataframe is missing required columns: {missing}"
        raise ValueError(msg)


def _ensure_outdir(path: Path) -> None:
    path.mkdir(parents=True, exist_ok=True)


def plot_spatiotemporal_heatmap(
    df: pd.DataFrame,
    value_col: str,
    out_file: Path,
    title: str | None = None,
    cmap: str = "viridis",
) -> None:
    """Create a distance-vs-time heatmap for a scalar state variable."""

    _check_columns(df, ["time_s", "distance_m", value_col])
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
    _check_columns(df, required_cols)

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

    _check_columns(df, [time_col, distance_col, species])
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


def generate_default_figure_pack(
    df: pd.DataFrame,
    species: Sequence[str],
    out_dir: Path,
    snapshot_times_s: Sequence[float],
) -> list[Path]:
    """Generate default report figures for thermo + species trajectories."""

    _ensure_outdir(out_dir)
    created: list[Path] = []

    thermo_cols = [
        ("temperature_k", "Temperature evolution", "inferno"),
        ("pressure_pa", "Pressure evolution", "cividis"),
    ]
    for col, title, cmap in thermo_cols:
        if col in df.columns:
            out_file = out_dir / f"heatmap_{col}.png"
            plot_spatiotemporal_heatmap(df=df, value_col=col, out_file=out_file, title=title, cmap=cmap)
            created.append(out_file)

    if species:
        out_traces = out_dir / "species_time_traces.png"
        available = [sp for sp in species if sp in df.columns]
        if available and "location" in df.columns:
            plot_species_time_traces(df=df, species=available, out_file=out_traces)
            created.append(out_traces)

        for sp in available:
            out_snap = out_dir / f"distance_snapshots_{sp}.png"
            plot_species_distance_snapshots(
                df=df,
                species=sp,
                snapshot_times_s=snapshot_times_s,
                out_file=out_snap,
            )
            created.append(out_snap)

            out_heat = out_dir / f"heatmap_{sp}.png"
            plot_spatiotemporal_heatmap(
                df=df,
                value_col=sp,
                out_file=out_heat,
                title=f"{sp} evolution",
            )
            created.append(out_heat)

    return created
