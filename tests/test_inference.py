from __future__ import annotations

import numpy as np
import pandas as pd

from faa_emissions_analysis.inference import align_predicted_and_observed, posterior_summary_table


def test_align_predicted_and_observed() -> None:
    pred = pd.DataFrame(
        {
            "time_s": [0.0, 1.0, 2.0],
            "location": ["FTIR_MODEL"] * 3,
            "CO2": [0.1, 0.11, 0.12],
            "CO": [0.01, 0.011, 0.012],
        }
    )
    obs = pd.DataFrame(
        {
            "time_s": [0.1, 1.1, 1.9],
            "location": ["FTIR"] * 3,
            "CO2": [0.09, 0.10, 0.11],
            "CO": [0.009, 0.010, 0.011],
        }
    )
    out = align_predicted_and_observed(
        predicted_df=pred,
        observed_df=obs,
        species=["CO2", "CO"],
        predicted_location="FTIR_MODEL",
        observed_location="FTIR",
        tolerance_s=0.25,
    )
    assert len(out) == 3
    assert {"CO2_obs", "CO2_pred", "CO_obs", "CO_pred"}.issubset(out.columns)


def test_posterior_summary_table() -> None:
    samples = {
        "scale": np.array([[1.0, 0.9], [1.1, 1.0], [0.95, 1.05]]),
        "sigma": np.array([[0.01, 0.02], [0.02, 0.03], [0.015, 0.025]]),
    }
    summary = posterior_summary_table(samples, species=["CO2", "CO"])
    assert len(summary) == 4
    assert (summary["p95"] >= summary["p05"]).all()
