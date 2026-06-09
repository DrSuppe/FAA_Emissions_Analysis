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
        load_inference_config,
        plot_posterior_traces,
        posterior_diagnostics,
        posterior_summary_table,
        run_specieswise_nuts,
    )
except ModuleNotFoundError:
    repo_root = Path(__file__).resolve().parents[1]
    sys.path.insert(0, str(repo_root / "src"))
    from faa_emissions_analysis.inference import (
        InferenceConfig,
        align_predicted_and_observed,
        load_inference_config,
        plot_posterior_traces,
        posterior_diagnostics,
        posterior_summary_table,
        run_specieswise_nuts,
    )


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Bayesian calibration from forward model to FTIR data.")
    parser.add_argument(
        "--config",
        type=Path,
        default=None,
        help="Optional YAML inference config (inference: + comparison: blocks). "
             "CLI flags override any matching values from the file.",
    )
    parser.add_argument("--predicted-csv", type=Path, required=True, help="Forward model output CSV.")
    parser.add_argument("--observed-csv", type=Path, required=True, help="Harmonized FTIR CSV.")
    parser.add_argument("--predicted-location", type=str, default=None, help="Model location label to compare with FTIR.")
    parser.add_argument("--observed-location", type=str, default=None, help="FTIR location label in observed CSV.")
    parser.add_argument("--species", nargs="+", default=None, help="Species to include in inference.")
    parser.add_argument("--num-warmup", type=int, default=None)
    parser.add_argument("--num-samples", type=int, default=None)
    parser.add_argument("--num-chains", type=int, default=None)
    parser.add_argument("--seed", type=int, default=None)
    parser.add_argument("--tolerance-s", type=float, default=None)
    parser.add_argument(
        "--out-summary-csv",
        type=Path,
        default=Path("reports/posterior_summary.csv"),
        help="Output CSV for posterior summary statistics.",
    )
    parser.add_argument(
        "--out-diagnostics-csv",
        type=Path,
        default=Path("reports/posterior_diagnostics.csv"),
        help="Output CSV for Rhat and ESS convergence diagnostics.",
    )
    parser.add_argument(
        "--out-traces-dir",
        type=Path,
        default=None,
        help="If set, write posterior trace PNGs to this directory.",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()

    # --- Load base config from YAML (if provided) then apply CLI overrides ---
    if args.config is not None:
        file_config, comparison = load_inference_config(args.config)
    else:
        file_config, comparison = InferenceConfig(), {}

    # CLI args override file values when explicitly supplied.
    num_warmup = args.num_warmup if args.num_warmup is not None else file_config.num_warmup
    num_samples = args.num_samples if args.num_samples is not None else file_config.num_samples
    num_chains = args.num_chains if args.num_chains is not None else file_config.num_chains
    random_seed = args.seed if args.seed is not None else file_config.random_seed
    tolerance_s = args.tolerance_s if args.tolerance_s is not None else file_config.time_tolerance_s

    predicted_location = args.predicted_location or comparison.get("predicted_location")
    observed_location = args.observed_location or comparison.get("observed_location", "FTIR")
    species = args.species or comparison.get("species")

    if predicted_location is None:
        raise SystemExit("--predicted-location is required (or set comparison.predicted_location in config YAML)")
    if not species:
        raise SystemExit("--species is required (or set comparison.species in config YAML)")

    config = InferenceConfig(
        num_warmup=num_warmup,
        num_samples=num_samples,
        num_chains=num_chains,
        random_seed=random_seed,
        time_tolerance_s=tolerance_s,
        priors=file_config.priors,
    )

    pred = pd.read_csv(args.predicted_csv)
    obs = pd.read_csv(args.observed_csv)

    aligned = align_predicted_and_observed(
        predicted_df=pred,
        observed_df=obs,
        species=species,
        predicted_location=predicted_location,
        observed_location=observed_location,
        tolerance_s=tolerance_s,
    )

    if len(aligned) == 0:
        raise SystemExit("No aligned rows remain after time-matching. Check locations and tolerance_s.")

    samples = run_specieswise_nuts(aligned, species=species, config=config)
    summary = posterior_summary_table(samples, species=species)

    args.out_summary_csv.parent.mkdir(parents=True, exist_ok=True)
    summary.to_csv(args.out_summary_csv, index=False)
    print(f"Posterior summary  → {args.out_summary_csv}  ({len(summary)} rows)")

    # --- Diagnostics ---
    try:
        diag = posterior_diagnostics(samples, species=species)
        args.out_diagnostics_csv.parent.mkdir(parents=True, exist_ok=True)
        diag.to_csv(args.out_diagnostics_csv, index=False)
        print(f"Convergence diags  → {args.out_diagnostics_csv}  ({len(diag)} rows)")

        # Flag any problematic parameters.
        bad_rhat = diag[diag["rhat"] > 1.01]
        low_ess = diag[diag["ess_bulk"] < 400]
        if not bad_rhat.empty:
            print(f"WARNING: {len(bad_rhat)} parameter(s) have Rhat > 1.01 — chains may not have converged.")
            print(bad_rhat[["parameter", "species", "rhat"]].to_string(index=False))
        if not low_ess.empty:
            print(f"WARNING: {len(low_ess)} parameter(s) have ESS_bulk < 400 — consider more samples.")

        if args.out_traces_dir is not None:
            paths = plot_posterior_traces(samples, species=species, output_dir=args.out_traces_dir)
            print(f"Trace plots        → {args.out_traces_dir}  ({len(paths)} files)")

    except ImportError as exc:
        print(f"Skipping diagnostics (ArviZ not available): {exc}")


if __name__ == "__main__":
    main()
