"""Type definitions for Bayesian inference settings."""

from __future__ import annotations

from dataclasses import dataclass, field


@dataclass(frozen=True)
class PriorConfig:
    """Hyperparameters for the species-wise calibration model.

    All ``*_ref_fraction`` values are dimensionless fractions of the per-species
    predicted-signal median.  Using fractional priors keeps the inference
    well-scaled regardless of whether a species is a major constituent (CO2 at
    ~10 %) or a trace component (NO at sub-100 ppm).
    """

    #: Std-dev of LogNormal prior on multiplicative sensor-sensitivity scale.
    #: LogNormal(0, 0.30) spans roughly ×0.5 – ×2 (95 % credible interval).
    scale_log_std: float = 0.30

    #: Normal std for additive bias, expressed as fraction of the species
    #: predicted-signal median.  0.05 → ±5 % absolute bias at 1σ.
    bias_ref_fraction: float = 0.05

    #: HalfNormal scale for observation noise, as fraction of signal median.
    sigma_ref_fraction: float = 0.05

    #: HalfNormal scale for structural model discrepancy, as fraction of
    #: signal median.  Intentionally wider than sigma to allow for systematic
    #: model error.
    discrepancy_ref_fraction: float = 0.10


@dataclass(frozen=True)
class InferenceConfig:
    """MCMC settings for species-wise calibration."""

    num_warmup: int = 700
    num_samples: int = 1200
    num_chains: int = 1
    random_seed: int = 7
    time_tolerance_s: float = 0.6
    priors: PriorConfig = field(default_factory=PriorConfig)
