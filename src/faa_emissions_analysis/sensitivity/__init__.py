"""Sensitivity screening package (Morris elementary-effects method)."""

from .morris import make_model_fn, morris_screening
from .perturbation import perturb_config
from .types import MorrisConfig, ParameterSpec

__all__ = [
    "MorrisConfig",
    "ParameterSpec",
    "make_model_fn",
    "morris_screening",
    "perturb_config",
]
