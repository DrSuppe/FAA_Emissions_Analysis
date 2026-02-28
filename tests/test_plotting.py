from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd

from faa_emissions_analysis.plotting import generate_default_figure_pack


def test_generate_default_figure_pack(tmp_path: Path) -> None:
    times = np.array([0.0, 1.0, 2.0, 3.0])
    distances = np.array([0.0, 0.5, 1.0])
    rows = []
    for t in times:
        for d in distances:
            rows.append(
                {
                    "time_s": t,
                    "distance_m": d,
                    "location": f"S{int(d * 10)}",
                    "temperature_k": 900.0 + 10.0 * t - 50.0 * d,
                    "pressure_pa": 200_000.0 - 2_000.0 * d,
                    "CO2": 0.07 + 0.001 * t,
                    "CO": 0.005 + 0.0005 * d,
                }
            )
    df = pd.DataFrame(rows)

    out_dir = tmp_path / "figs"
    created = generate_default_figure_pack(
        df=df,
        species=["CO2", "CO"],
        out_dir=out_dir,
        snapshot_times_s=[0.0, 2.0, 3.0],
    )

    assert created
    assert all(path.exists() for path in created)
