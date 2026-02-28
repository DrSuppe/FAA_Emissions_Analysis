#!/usr/bin/env python3
"""Load raw station and FTIR files and write harmonized/aligned CSV outputs."""

from __future__ import annotations

import argparse
from pathlib import Path
import sys

try:
    from faa_emissions_analysis.ingestion import load_and_align_inputs
except ModuleNotFoundError:
    repo_root = Path(__file__).resolve().parents[1]
    sys.path.insert(0, str(repo_root / "src"))
    from faa_emissions_analysis.ingestion import load_and_align_inputs


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Prepare harmonized station/FTIR datasets.")
    parser.add_argument("--config", type=Path, required=True, help="YAML config describing sources and alignment.")
    parser.add_argument(
        "--out-dir",
        type=Path,
        default=Path("data/processed"),
        help="Destination directory for output CSVs.",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    args.out_dir.mkdir(parents=True, exist_ok=True)

    station, ftir, aligned = load_and_align_inputs(args.config)
    station_out = args.out_dir / "station_harmonized.csv"
    ftir_out = args.out_dir / "ftir_harmonized.csv"
    aligned_out = args.out_dir / "aligned_station_ftir.csv"

    station.to_csv(station_out, index=False)
    ftir.to_csv(ftir_out, index=False)
    aligned.to_csv(aligned_out, index=False)

    print("Wrote:")
    print(station_out)
    print(ftir_out)
    print(aligned_out)


if __name__ == "__main__":
    main()
