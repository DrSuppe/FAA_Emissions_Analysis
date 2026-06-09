from __future__ import annotations

import warnings

import numpy as np
import pandas as pd
import pytest

from faa_emissions_analysis.inference import align_predicted_and_observed, posterior_summary_table
from faa_emissions_analysis.inference.config import load_inference_config
from faa_emissions_analysis.inference.types import InferenceConfig, PriorConfig


# ---------------------------------------------------------------------------
# Alignment tests
# ---------------------------------------------------------------------------

def _make_pred_obs():
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
    return pred, obs


def test_align_predicted_and_observed() -> None:
    pred, obs = _make_pred_obs()
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


def test_align_warns_on_dropped_rows() -> None:
    """When tolerance is tight enough to drop rows, a warning must be emitted."""
    pred, obs = _make_pred_obs()
    with warnings.catch_warnings(record=True) as caught:
        warnings.simplefilter("always")
        out = align_predicted_and_observed(
            predicted_df=pred,
            observed_df=obs,
            species=["CO2", "CO"],
            predicted_location="FTIR_MODEL",
            observed_location="FTIR",
            tolerance_s=0.05,  # too tight — all rows should be dropped
        )
    assert len(out) == 0
    assert any("dropped" in str(w.message).lower() for w in caught), (
        "Expected a UserWarning about dropped rows"
    )


def test_align_no_warning_when_no_rows_dropped() -> None:
    """No warning when all rows survive alignment."""
    pred, obs = _make_pred_obs()
    with warnings.catch_warnings(record=True) as caught:
        warnings.simplefilter("always")
        align_predicted_and_observed(
            predicted_df=pred,
            observed_df=obs,
            species=["CO2", "CO"],
            predicted_location="FTIR_MODEL",
            observed_location="FTIR",
            tolerance_s=0.25,
        )
    drop_warnings = [w for w in caught if "dropped" in str(w.message).lower()]
    assert len(drop_warnings) == 0


# ---------------------------------------------------------------------------
# Posterior summary tests
# ---------------------------------------------------------------------------

def test_posterior_summary_table() -> None:
    samples = {
        "scale": np.array([[1.0, 0.9], [1.1, 1.0], [0.95, 1.05]]),
        "sigma": np.array([[0.01, 0.02], [0.02, 0.03], [0.015, 0.025]]),
    }
    summary = posterior_summary_table(samples, species=["CO2", "CO"])
    assert len(summary) == 4
    assert (summary["p95"] >= summary["p05"]).all()


# ---------------------------------------------------------------------------
# InferenceConfig / PriorConfig tests
# ---------------------------------------------------------------------------

def test_inference_config_defaults() -> None:
    cfg = InferenceConfig()
    assert cfg.num_warmup == 700
    assert cfg.num_samples == 1200
    assert isinstance(cfg.priors, PriorConfig)
    assert cfg.priors.scale_log_std == 0.30


def test_prior_config_custom() -> None:
    p = PriorConfig(scale_log_std=0.5, bias_ref_fraction=0.10)
    assert p.scale_log_std == 0.5
    assert p.bias_ref_fraction == 0.10
    # unspecified fields keep defaults
    assert p.sigma_ref_fraction == 0.05


# ---------------------------------------------------------------------------
# YAML config loading tests
# ---------------------------------------------------------------------------

def test_load_inference_config_roundtrip(tmp_path) -> None:
    yaml_text = """
inference:
  num_warmup: 200
  num_samples: 400
  num_chains: 1
  random_seed: 99
  time_tolerance_s: 1.0
  priors:
    scale_log_std: 0.50
    bias_ref_fraction: 0.08
    sigma_ref_fraction: 0.03
    discrepancy_ref_fraction: 0.15
comparison:
  predicted_location: probe_internal
  observed_location: FTIR
  species:
    - CO
    - NO
"""
    cfg_file = tmp_path / "test_inf.yaml"
    cfg_file.write_text(yaml_text)

    config, comparison = load_inference_config(cfg_file)

    assert config.num_warmup == 200
    assert config.num_samples == 400
    assert config.random_seed == 99
    assert config.priors.scale_log_std == 0.50
    assert config.priors.bias_ref_fraction == 0.08
    assert comparison["predicted_location"] == "probe_internal"
    assert comparison["species"] == ["CO", "NO"]


def test_load_inference_config_defaults_when_priors_omitted(tmp_path) -> None:
    yaml_text = """
inference:
  num_warmup: 100
  num_samples: 200
comparison:
  predicted_location: stage_out
  species: [CO2]
"""
    cfg_file = tmp_path / "test_inf_no_priors.yaml"
    cfg_file.write_text(yaml_text)

    config, _ = load_inference_config(cfg_file)
    # Should fall back to PriorConfig defaults.
    assert config.priors.scale_log_std == 0.30
    assert config.priors.bias_ref_fraction == 0.05
