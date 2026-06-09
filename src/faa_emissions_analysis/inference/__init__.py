"""Bayesian calibration package for model-vs-FTIR alignment."""

from .alignment import align_predicted_and_observed
from .config import load_inference_config
from .diagnostics import plot_posterior_traces, posterior_diagnostics
from .nuts import run_specieswise_nuts
from .summary import posterior_summary_table
from .types import InferenceConfig, PriorConfig

__all__ = [
    "InferenceConfig",
    "PriorConfig",
    "align_predicted_and_observed",
    "load_inference_config",
    "plot_posterior_traces",
    "posterior_diagnostics",
    "posterior_summary_table",
    "run_specieswise_nuts",
]
