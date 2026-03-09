"""Type definitions for Bayesian inference settings."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class InferenceConfig:
    """MCMC settings for species-wise calibration."""

    num_warmup: int = 700
    num_samples: int = 1200
    num_chains: int = 1
    random_seed: int = 7
    time_tolerance_s: float = 0.6
