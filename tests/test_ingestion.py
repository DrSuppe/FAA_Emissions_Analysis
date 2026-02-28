from __future__ import annotations

from pathlib import Path

import pandas as pd

from faa_emissions_analysis.ingestion import SourceConfig, align_station_and_ftir, load_source_frame


def test_load_source_frame_csv(tmp_path: Path) -> None:
    src = tmp_path / "station.csv"
    pd.DataFrame(
        {
            "timestamp": ["2026-01-01T00:00:00", "2026-01-01T00:00:01"],
            "loc": ["A", "A"],
            "distance": [0.5, 0.5],
            "T": [900.0, 905.0],
            "P": [200000.0, 199500.0],
            "mdot": [0.10, 0.11],
            "CO2_raw": [0.07, 0.071],
        }
    ).to_csv(src, index=False)

    cfg = SourceConfig(
        path=src,
        time_column="timestamp",
        column_map={
            "location": "loc",
            "distance_m": "distance",
            "temperature_k": "T",
            "pressure_pa": "P",
            "mass_flow_kg_s": "mdot",
        },
        species_map={"CO2": "CO2_raw"},
        dataset_label="station",
    )
    out = load_source_frame(cfg)
    assert {"timestamp", "time_s", "temperature_k", "CO2"}.issubset(out.columns)
    assert out["time_s"].iloc[0] == 0.0
    assert out["CO2"].iloc[1] > out["CO2"].iloc[0]


def test_align_station_and_ftir_nearest() -> None:
    station = pd.DataFrame({"time_s": [0.0, 1.0, 2.0], "temperature_k": [100.0, 200.0, 300.0]})
    ftir = pd.DataFrame({"time_s": [0.2, 1.6], "CO2": [0.1, 0.2]})

    aligned = align_station_and_ftir(station, ftir, tolerance_s=0.6)
    assert len(aligned) == 2
    assert aligned["temperature_k"].tolist() == [100.0, 300.0]
