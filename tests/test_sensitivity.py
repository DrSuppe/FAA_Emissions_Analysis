"""Tests for the Morris sensitivity screening module."""

from __future__ import annotations

import numpy as np
import pytest

from faa_emissions_analysis.sensitivity import (
    MorrisConfig,
    ParameterSpec,
    morris_screening,
    perturb_config,
)
from faa_emissions_analysis.sensitivity.types import ParameterSpec as PS


# ---------------------------------------------------------------------------
# ParameterSpec validation
# ---------------------------------------------------------------------------

def test_parameter_spec_requires_dot_in_path() -> None:
    with pytest.raises(ValueError, match="must be '<stage>.<field>'"):
        ParameterSpec(path="no_dot_here", low=0.0, high=1.0)


def test_parameter_spec_requires_low_lt_high() -> None:
    with pytest.raises(ValueError, match="must be <"):
        ParameterSpec(path="stage.field", low=1.0, high=0.5)


def test_parameter_spec_stage_and_field() -> None:
    s = ParameterSpec(path="pilot_primary.residence_time_s", low=0.001, high=0.010)
    assert s.stage_name == "pilot_primary"
    assert s.field_name == "residence_time_s"


# ---------------------------------------------------------------------------
# perturb_config
# ---------------------------------------------------------------------------

def _make_base_config():
    from faa_emissions_analysis.model.types import ForwardModelConfig, StageConfig
    stage = StageConfig(
        name="stage_a",
        distance_m=0.1,
        residence_time_s=0.005,
        pressure_drop_pa=500.0,
        wall_temperature_k=1200.0,
        ua_w_m2_k=10.0,
        mix_fraction=0.02,
    )
    return ForwardModelConfig(
        mechanism="gri30.yaml",
        tracked_species=("O2", "N2"),
        inlet_composition={"O2": 0.21, "N2": 0.79},
        stages=(stage,),
    )


def test_perturb_config_changes_field() -> None:
    base = _make_base_config()
    perturbed = perturb_config(base, {"stage_a.residence_time_s": 0.999})
    assert perturbed.stages[0].residence_time_s == pytest.approx(0.999)
    # Other fields unchanged.
    assert perturbed.stages[0].pressure_drop_pa == 500.0


def test_perturb_config_multiple_fields() -> None:
    base = _make_base_config()
    perturbed = perturb_config(base, {
        "stage_a.residence_time_s": 0.001,
        "stage_a.ua_w_m2_k": 99.0,
    })
    assert perturbed.stages[0].residence_time_s == pytest.approx(0.001)
    assert perturbed.stages[0].ua_w_m2_k == pytest.approx(99.0)


def test_perturb_config_rejects_immutable_field() -> None:
    base = _make_base_config()
    with pytest.raises(ValueError, match="not in the set of mutable fields"):
        perturb_config(base, {"stage_a.name": "oops"})


# ---------------------------------------------------------------------------
# Morris screening with a synthetic model function
# ---------------------------------------------------------------------------

def _linear_model_fn(params: dict[str, float]) -> np.ndarray:
    """y = [2*x1 + x2, x1 - 0.5*x2]  (in physical units directly)."""
    x1 = params.get("stage_a.residence_time_s", 0.005)
    x2 = params.get("stage_a.ua_w_m2_k", 10.0)
    return np.array([2.0 * x1 + x2, x1 - 0.5 * x2])


_SPECS = [
    ParameterSpec("stage_a.residence_time_s", low=0.001, high=0.010),
    ParameterSpec("stage_a.ua_w_m2_k",        low=5.0,   high=50.0),
]

_MORRIS_CFG = MorrisConfig(n_trajectories=8, n_levels=4, random_seed=0)


def test_morris_output_shape() -> None:
    results = morris_screening(_linear_model_fn, _SPECS, config=_MORRIS_CFG, progress=False)
    # k=2 parameters × 2 outputs = 4 rows.
    assert len(results) == 4
    assert set(results.columns) >= {"parameter", "output_index", "mu_star", "sigma", "mu"}


def test_morris_mu_star_nonnegative() -> None:
    results = morris_screening(_linear_model_fn, _SPECS, config=_MORRIS_CFG, progress=False)
    assert (results["mu_star"] >= 0).all()


def test_morris_parameter_ranking_linear_model() -> None:
    """For the linear model, x1 (residence_time) dominates output_0.

    The elementary effect EE_i = ∂y/∂x_i in physical units.  For
    ``y[0] = 2*x1 + x2``:
      EE_x1 = 2,  EE_x2 = 1  →  μ*(x1) > μ*(x2) for output 0.
    """
    results = morris_screening(_linear_model_fn, _SPECS, config=_MORRIS_CFG, progress=False)
    out0 = results[results["output_index"] == 0].set_index("parameter")["mu_star"]
    assert out0["stage_a.residence_time_s"] > out0["stage_a.ua_w_m2_k"]
