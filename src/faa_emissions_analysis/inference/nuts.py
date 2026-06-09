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
    """Infer per-species scale/bias/noise/discrepancy parameters via NUTS.

    Prior design
    ------------
    Priors are expressed as fractions of the per-species predicted-signal
    median (``pred_ref``).  This keeps them well-scaled for both major
    constituents (CO2 ≈ 10 %) and trace species (NO ≈ sub-100 ppm) without
    requiring manual per-species tuning.

    Parameters
    ----------
    aligned_df:
        Output of :func:`align_predicted_and_observed`; must contain columns
        ``{sp}_obs`` and ``{sp}_pred`` for each species.
    species:
        Ordered list of species names.
    config:
        MCMC and prior settings.  Defaults to :class:`InferenceConfig`.

    Returns
    -------
    Dict mapping parameter names to sample arrays of shape
    ``(num_samples, n_species)``.
    """

    species = list(species)
    config = config or InferenceConfig()
    p = config.priors

    try:
        import jax.numpy as jnp
        from jax import random
        import numpyro
        import numpyro.distributions as dist
        from numpyro.infer import MCMC, NUTS
    except ImportError as exc:
        raise ImportError(
            "run_specieswise_nuts requires jax and numpyro. "
            "Install extras with: pip install '.[inference]'"
        ) from exc

    y_obs = aligned_df[[f"{sp}_obs" for sp in species]].to_numpy(dtype=float)
    y_pred = aligned_df[[f"{sp}_pred" for sp in species]].to_numpy(dtype=float)

    # Per-species reference scale: median of |predicted|.  Used to convert
    # fractional prior hyperparameters to absolute units matching the data.
    pred_ref = np.median(np.abs(y_pred), axis=0).clip(min=1e-30)  # shape (n_species,)

    def model(pred: jnp.ndarray, obs: jnp.ndarray | None = None) -> None:
        n_species = pred.shape[1]
        ref = jnp.array(pred_ref)  # (n_species,)

        # Multiplicative sensitivity calibration — scale-free, same prior for all species.
        scale = numpyro.sample(
            "scale",
            dist.LogNormal(jnp.zeros(n_species), p.scale_log_std),
        )

        # Additive zero-offset bias in absolute units, with std = fraction × ref.
        bias = numpyro.sample(
            "bias",
            dist.Normal(jnp.zeros(n_species), p.bias_ref_fraction * ref),
        )

        # Observation noise (FTIR measurement uncertainty).
        sigma = numpyro.sample(
            "sigma",
            dist.HalfNormal(p.sigma_ref_fraction * ref).expand([n_species]).to_event(1),
        )

        # Structural model discrepancy (forward-model error not captured by scale/bias).
        discrepancy = numpyro.sample(
            "discrepancy",
            dist.HalfNormal(p.discrepancy_ref_fraction * ref).expand([n_species]).to_event(1),
        )

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
    mcmc.run(key, pred=jnp.array(y_pred), obs=jnp.array(y_obs))

    samples = mcmc.get_samples()
    return {name: np.asarray(value) for name, value in samples.items()}
