"""Default report plot-pack generation."""

from __future__ import annotations

from pathlib import Path
from typing import Sequence

import pandas as pd

from .heatmaps import plot_spatiotemporal_heatmap
from .species_profiles import plot_species_distance_snapshots, plot_species_time_traces
from .utils import ensure_outdir


def generate_default_figure_pack(
    df: pd.DataFrame,
    species: Sequence[str],
    out_dir: Path,
    snapshot_times_s: Sequence[float],
) -> list[Path]:
    """Generate default report figures for thermo + species trajectories."""

    ensure_outdir(out_dir)
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
