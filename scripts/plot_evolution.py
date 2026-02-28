#!/usr/bin/env python3
"""Generate default spatiotemporal plots from a simulation CSV."""

from __future__ import annotations

import argparse
from pathlib import Path

import pandas as pd

from faa_emissions_analysis.plotting import generate_default_figure_pack


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Generate injector-to-FTIR evolution plots.")
    parser.add_argument("--input-csv", type=Path, required=True, help="Path to harmonized simulation CSV.")
    parser.add_argument(
        "--species",
        nargs="+",
        default=["CO2", "CO", "NO", "NO2", "UHC"],
        help="Species columns to plot.",
    )
    parser.add_argument(
        "--snapshot-times-s",
        nargs="+",
        type=float,
        default=[0.0, 5.0, 10.0, 20.0, 40.0],
        help="Times (s) for distance profile snapshots.",
    )
    parser.add_argument(
        "--out-dir",
        type=Path,
        default=Path("reports/figures"),
        help="Output directory for figure pack.",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    df = pd.read_csv(args.input_csv)
    created = generate_default_figure_pack(
        df=df,
        species=args.species,
        out_dir=args.out_dir,
        snapshot_times_s=args.snapshot_times_s,
    )
    print(f"Created {len(created)} figure(s):")
    for path in created:
        print(path)


if __name__ == "__main__":
    main()
