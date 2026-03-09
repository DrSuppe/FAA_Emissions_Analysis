"""NumPyro NUTS calibration routines."""

from __future__ import annotations

from typing import Iterable

import numpy as np
import pandas as pd

from .types import InferenceConfig


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
