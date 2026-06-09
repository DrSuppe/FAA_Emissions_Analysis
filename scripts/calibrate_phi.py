#!/usr/bin/env python3
"""Calibrate the combustor equivalence ratio (phi) against station data.

The station CSV (PROBE_INLET, ~0.60 m) is the VALIDATION TARGET for the reacting
forward model. This script sweeps/solves phi so the predicted post-main-zone
composition (O2, CO2, H2O, CO mole fractions) best matches the station target,
then reports residuals and an INDEPENDENT predicted-vs-measured temperature check
(temperature emerges from combustion + wall heat loss, it is not calibrated).

Mechanism: HyChem A2 Jet-A (POSF10325) + NOx skeletal — mechanisms/MECHANISM_PROVENANCE.md.
Saggese et al., Combust. Flame 212 (2020) 270-278; Glarborg et al., PECS 67 (2018) 31-68.

EPISTEMIC NOTE: the station data here is SYNTHETIC. It need not be exactly
reproducible by this fuel+mechanism+geometry; the script reports the actual fit
quality (residuals) and does not force a match.
"""

from __future__ import annotations

import argparse
import dataclasses
from pathlib import Path
import sys

import numpy as np
import pandas as pd

try:
    from faa_emissions_analysis.model import CanteraPathModel, load_forward_model_config
except ModuleNotFoundError:
    sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
    from faa_emissions_analysis.model import CanteraPathModel, load_forward_model_config

# Species used to define the calibration objective.
_FIT_SPECIES = ("O2", "CO2", "H2O", "CO")


def _predict_at(config, inlet_df: pd.DataFrame, location: str) -> dict[str, float]:
    """Run the reacting model and return the prediction at ``location``."""
    model = CanteraPathModel(config)
    out = model.simulate_timeseries(inlet_df.head(1))
    row = out[out["location"] == location].iloc[0]
    rec = {sp: float(row[sp]) for sp in _FIT_SPECIES}
    rec["temperature_k"] = float(row["temperature_k"])
    rec["NO"] = float(row["NO"])
    rec["NO2"] = float(row["NO2"])
    return rec


def _ssr(pred: dict[str, float], target: dict[str, float]) -> float:
    """Relative sum-of-squared residuals over the fit species."""
    return float(sum(((pred[s] - target[s]) / max(target[s], 1e-4)) ** 2 for s in _FIT_SPECIES))


def calibrate(
    config,
    inlet_df: pd.DataFrame,
    location: str = "main_zone",
    phi_grid: np.ndarray | None = None,
) -> tuple[float, float, dict[str, float]]:
    """Return (best_phi, best_ssr, best_prediction) over a phi grid."""
    if phi_grid is None:
        phi_grid = np.arange(0.30, 0.95, 0.01)
    best = None
    for phi in phi_grid:
        cfg = dataclasses.replace(config, equivalence_ratio=float(phi))
        pred = _predict_at(cfg, inlet_df, location)
        ssr = _ssr(pred, _target_from(inlet_df))
        if best is None or ssr < best[1]:
            best = (float(phi), ssr, pred)
    return best


def _target_from(inlet_df: pd.DataFrame) -> dict[str, float]:
    return {s: float(inlet_df[s].mean()) for s in _FIT_SPECIES}


def main() -> None:
    parser = argparse.ArgumentParser(description="Calibrate phi against station data.")
    parser.add_argument("--station-csv", type=Path, default=Path("data/raw/station_example.csv"))
    parser.add_argument("--model-config", type=Path, default=Path("configs/example_model_config.yaml"))
    parser.add_argument("--fit-location", default="main_zone", help="Stage used for the composition fit.")
    parser.add_argument("--probe-location", default="probe_internal", help="Stage reported as probe prediction.")
    args = parser.parse_args()

    station = pd.read_csv(args.station_csv)
    station["time_s"] = range(len(station))
    target = _target_from(station)
    target_T = float(station["temperature_k"].mean())

    cfg = load_forward_model_config(args.model_config)
    best_phi, best_ssr, _ = calibrate(cfg, station, location=args.fit_location)

    cfg_best = dataclasses.replace(cfg, equivalence_ratio=best_phi)
    probe = _predict_at(cfg_best, station, args.probe_location)

    print(f"Best-fit phi = {best_phi:.3f}  (relative SSR = {best_ssr:.4f}, fit at '{args.fit_location}')")
    print(f"Inlet preheat assumption: T_inlet_air = {cfg.t_inlet_air_k:.0f} K (documented compressor-discharge value)")
    print()
    print(f"{'quantity':<10}{'predicted':>12}{'measured':>12}{'residual':>12}")
    for s in _FIT_SPECIES:
        print(f"{s:<10}{probe[s]:>12.4f}{target[s]:>12.4f}{probe[s]-target[s]:>+12.4f}")
    print(f"{'T [K]':<10}{probe['temperature_k']:>12.1f}{target_T:>12.1f}{probe['temperature_k']-target_T:>+12.1f}")
    print()
    print(f"Predicted NO  at probe: {probe['NO']*1e6:.1f} ppm")
    print(f"Predicted NO2 at probe: {probe['NO2']*1e6:.3f} ppm")
    print()
    print(f"Stoichiometric note: target H2O/CO2 = {target['H2O']/target['CO2']:.2f}; "
          f"fuel C11H22 yields ~1.0 at complete combustion (H2O cannot exceed ~CO2 for this fuel).")


if __name__ == "__main__":
    main()
