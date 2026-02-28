"""Bayesian calibration scaffolding for FTIR model-data alignment."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable

import numpy as np
import pandas as pd


@dataclass(frozen=True)
class InferenceConfig:
    """MCMC settings for species-wise calibration."""

    num_warmup: int = 700
    num_samples: int = 1200
    num_chains: int = 1
    random_seed: int = 7
    time_tolerance_s: float = 0.6


def align_predicted_and_observed(
    predicted_df: pd.DataFrame,
    observed_df: pd.DataFrame,
    species: Iterable[str],
    predicted_location: str,
    observed_location: str = "FTIR",
    tolerance_s: float = 0.6,
) -> pd.DataFrame:
    """Nearest-time alignment between model prediction and FTIR observations."""

    species = list(species)
    need_cols = {"time_s", "location", *species}
    for name, frame in (("predicted_df", predicted_df), ("observed_df", observed_df)):
        missing = need_cols - set(frame.columns)
        if missing:
            raise ValueError(f"{name} is missing columns: {sorted(missing)}")

    pred_slice = predicted_df[predicted_df["location"] == predicted_location].copy()
    obs_slice = observed_df[observed_df["location"] == observed_location].copy()

    pred_cols = ["time_s", *species]
    obs_cols = ["time_s", *species]
    aligned = pd.merge_asof(
        obs_slice.sort_values("time_s")[obs_cols],
        pred_slice.sort_values("time_s")[pred_cols],
        on="time_s",
        direction="nearest",
        tolerance=tolerance_s,
        suffixes=("_obs", "_pred"),
    )
    return aligned.dropna().reset_index(drop=True)


def run_specieswise_nuts(
    aligned_df: pd.DataFrame,
    species: Iterable[str],
    config: InferenceConfig | None = None,
) -> dict[str, np.ndarray]:
    """Infer per-species scale/bias/noise/discrepancy parameters."""

    species = list(species)
    config = config or InferenceConfig()

    try:
        import jax.numpy as jnp
        from jax import random
        import numpyro
        import numpyro.distributions as dist
        from numpyro.infer import MCMC, NUTS
    except ImportError as exc:
        raise ImportError(
            "run_specieswise_nuts requires jax and numpyro. Install extras with: pip install '.[inference]'"
        ) from exc

    y_obs = aligned_df[[f"{sp}_obs" for sp in species]].to_numpy(dtype=float)
    y_pred = aligned_df[[f"{sp}_pred" for sp in species]].to_numpy(dtype=float)

    def model(pred: jnp.ndarray, obs: jnp.ndarray | None = None) -> None:
        n_species = pred.shape[1]
        scale = numpyro.sample("scale", dist.LogNormal(jnp.zeros(n_species), 0.30))
        bias = numpyro.sample("bias", dist.Normal(jnp.zeros(n_species), 0.02))
        sigma = numpyro.sample("sigma", dist.HalfNormal(0.02).expand([n_species]).to_event(1))
        discrepancy = numpyro.sample("discrepancy", dist.HalfNormal(0.02).expand([n_species]).to_event(1))

        mean = pred * scale + bias
        total_sigma = jnp.sqrt(sigma**2 + discrepancy**2)
        numpyro.sample("obs", dist.Normal(mean, total_sigma).to_event(2), obs=obs)

    kernel = NUTS(model)
    mcmc = MCMC(
        kernel,
        num_warmup=config.num_warmup,
        num_samples=config.num_samples,
        num_chains=config.num_chains,
        progress_bar=False,
    )
    key = random.PRNGKey(config.random_seed)
    mcmc.run(key, pred=y_pred, obs=y_obs)

    samples = mcmc.get_samples()
    as_numpy = {name: np.asarray(value) for name, value in samples.items()}
    return as_numpy


def posterior_summary_table(samples: dict[str, np.ndarray], species: Iterable[str]) -> pd.DataFrame:
    """Create percentile summary table from NUTS samples."""

    species = list(species)
    rows: list[dict[str, float | str]] = []

    for param, arr in samples.items():
        if arr.ndim == 1:
            arr = arr[:, None]
        for idx, sp in enumerate(species):
            col = arr[:, idx] if idx < arr.shape[1] else arr[:, 0]
            rows.append(
                {
                    "parameter": param,
                    "species": sp,
                    "mean": float(np.mean(col)),
                    "p05": float(np.percentile(col, 5.0)),
                    "p50": float(np.percentile(col, 50.0)),
                    "p95": float(np.percentile(col, 95.0)),
                }
            )

    return pd.DataFrame(rows)
