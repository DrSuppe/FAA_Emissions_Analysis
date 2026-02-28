#!/usr/bin/env python3
"""Run species-wise Bayesian calibration against FTIR observations."""

from __future__ import annotations

import argparse
from pathlib import Path
import sys

import pandas as pd

try:
    from faa_emissions_analysis.inference import (
        InferenceConfig,
        align_predicted_and_observed,
        posterior_summary_table,
        run_specieswise_nuts,
    )
except ModuleNotFoundError:
    repo_root = Path(__file__).resolve().parents[1]
    sys.path.insert(0, str(repo_root / "src"))
    from faa_emissions_analysis.inference import (
        InferenceConfig,
        align_predicted_and_observed,
        posterior_summary_table,
        run_specieswise_nuts,
    )


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Bayesian calibration from forward model to FTIR data.")
    parser.add_argument("--predicted-csv", type=Path, required=True, help="Forward model output CSV.")
    parser.add_argument("--observed-csv", type=Path, required=True, help="Harmonized FTIR CSV.")
    parser.add_argument("--predicted-location", type=str, required=True, help="Model location label to compare with FTIR.")
    parser.add_argument("--observed-location", type=str, default="FTIR", help="FTIR location label in observed CSV.")
    parser.add_argument("--species", nargs="+", required=True, help="Species to include in inference.")
    parser.add_argument("--num-warmup", type=int, default=700)
    parser.add_argument("--num-samples", type=int, default=1200)
    parser.add_argument("--num-chains", type=int, default=1)
    parser.add_argument("--seed", type=int, default=7)
    parser.add_argument("--tolerance-s", type=float, default=0.6)
    parser.add_argument(
        "--out-summary-csv",
        type=Path,
        default=Path("reports/posterior_summary.csv"),
        help="Output CSV for posterior summary statistics.",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    pred = pd.read_csv(args.predicted_csv)
    obs = pd.read_csv(args.observed_csv)

    aligned = align_predicted_and_observed(
        predicted_df=pred,
        observed_df=obs,
        species=args.species,
        predicted_location=args.predicted_location,
        observed_location=args.observed_location,
        tolerance_s=args.tolerance_s,
    )
    config = InferenceConfig(
        num_warmup=args.num_warmup,
        num_samples=args.num_samples,
        num_chains=args.num_chains,
        random_seed=args.seed,
        time_tolerance_s=args.tolerance_s,
    )
    samples = run_specieswise_nuts(aligned, species=args.species, config=config)
    summary = posterior_summary_table(samples, species=args.species)

    args.out_summary_csv.parent.mkdir(parents=True, exist_ok=True)
    summary.to_csv(args.out_summary_csv, index=False)
    print(f"Wrote posterior summary with {len(summary)} rows to {args.out_summary_csv}")


if __name__ == "__main__":
    main()
