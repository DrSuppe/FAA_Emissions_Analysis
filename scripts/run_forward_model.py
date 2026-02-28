#!/usr/bin/env python3
"""Run Cantera forward model across an inlet timeseries CSV."""

from __future__ import annotations

import argparse
from pathlib import Path
import sys

import pandas as pd

try:
    from faa_emissions_analysis.model import CanteraPathModel, load_forward_model_config
except ModuleNotFoundError:
    repo_root = Path(__file__).resolve().parents[1]
    sys.path.insert(0, str(repo_root / "src"))
    from faa_emissions_analysis.model import CanteraPathModel, load_forward_model_config


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run combustor-to-FTIR forward model.")
    parser.add_argument("--inlet-csv", type=Path, required=True, help="Harmonized inlet timeseries CSV.")
    parser.add_argument("--model-config", type=Path, required=True, help="Forward-model YAML configuration.")
    parser.add_argument(
        "--out-csv",
        type=Path,
        default=Path("data/processed/forward_simulation.csv"),
        help="Output path for stage trajectory table.",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    inlet_df = pd.read_csv(args.inlet_csv)
    cfg = load_forward_model_config(args.model_config)
    model = CanteraPathModel(cfg)
    simulated = model.simulate_timeseries(inlet_df)

    args.out_csv.parent.mkdir(parents=True, exist_ok=True)
    simulated.to_csv(args.out_csv, index=False)
    print(f"Wrote {len(simulated)} rows to {args.out_csv}")


if __name__ == "__main__":
    main()
