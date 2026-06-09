"""Posterior diagnostics: convergence checks and trace plots.

Requires the ``inference`` optional extras (``pip install '.[inference]'``),
which includes ArviZ.
"""

from __future__ import annotations

from pathlib import Path
from typing import Iterable

import numpy as np
import pandas as pd


def posterior_diagnostics(
    samples: dict[str, np.ndarray],
    species: Iterable[str],
) -> pd.DataFrame:
    """Compute per-parameter, per-species Rhat and ESS from NUTS samples.

    Parameters
    ----------
    samples:
        Dict returned by :func:`run_specieswise_nuts`.  Arrays have shape
        ``(num_samples, n_species)`` for single-chain runs or
        ``(num_chains * num_samples, n_species)`` after flattening.
    species:
        Ordered list of species names matching the second axis of each array.

    Returns
    -------
    DataFrame with columns ``parameter``, ``species``, ``rhat``,
    ``ess_bulk``, ``ess_tail``.  Rhat > 1.01 or ESS < 400 signals poor
    convergence.
    """
    try:
        import arviz as az
    except ImportError as exc:
        raise ImportError(
            "posterior_diagnostics requires arviz. "
            "Install extras with: pip install '.[inference]'"
        ) from exc

    species = list(species)

    # Build per-parameter InferenceData dicts.  ArviZ expects arrays with
    # a leading chain dimension; single-chain samples get a size-1 axis added.
    posterior_dict: dict[str, np.ndarray] = {}
    for param, arr in samples.items():
        if arr.ndim == 1:
            arr = arr[:, None]
        # arr: (n_samples, n_species) → expand to (1, n_samples, n_species)
        posterior_dict[param] = arr[None, ...]

    idata = az.from_dict(posterior=posterior_dict)

    rows: list[dict] = []
    for param, arr in samples.items():
        if arr.ndim == 1:
            arr = arr[:, None]
        for idx, sp in enumerate(species):
            col = arr[:, idx] if idx < arr.shape[1] else arr[:, 0]
            # Reshape for ArviZ: (1 chain, n_samples)
            chain_arr = col[None, :]
            rhat = float(az.rhat(az.from_dict(posterior={param: chain_arr}))[param].values)
            ess = az.ess(az.from_dict(posterior={param: chain_arr}))
            rows.append(
                {
                    "parameter": param,
                    "species": sp,
                    "rhat": rhat,
                    "ess_bulk": float(ess[param].values),
                    "ess_tail": float(
                        az.ess(az.from_dict(posterior={param: chain_arr}), method="tail")[param].values
                    ),
                }
            )

    return pd.DataFrame(rows)


def plot_posterior_traces(
    samples: dict[str, np.ndarray],
    species: Iterable[str],
    output_dir: Path,
) -> list[Path]:
    """Save per-parameter trace + density plots using ArviZ.

    One PNG is written per parameter, with one subplot column per species.

    Parameters
    ----------
    samples:
        Dict returned by :func:`run_specieswise_nuts`.
    species:
        Ordered list of species names.
    output_dir:
        Directory for output PNGs; created if it does not exist.

    Returns
    -------
    List of paths to written files.
    """
    try:
        import arviz as az
        import matplotlib
        matplotlib.use("Agg")
        import matplotlib.pyplot as plt
    except ImportError as exc:
        raise ImportError(
            "plot_posterior_traces requires arviz and matplotlib. "
            "Install extras with: pip install '.[inference]'"
        ) from exc

    species = list(species)
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    written: list[Path] = []

    for param, arr in samples.items():
        if arr.ndim == 1:
            arr = arr[:, None]
        # Build InferenceData with one named variable per species so ArviZ
        # renders each as a separate panel.
        posterior_dict = {
            f"{param}_{sp}": arr[None, :, idx] if idx < arr.shape[1] else arr[None, :, 0]
            for idx, sp in enumerate(species)
        }
        idata = az.from_dict(posterior=posterior_dict)
        axes = az.plot_trace(idata, figsize=(10, 3 * len(species)))
        fig = axes.ravel()[0].get_figure()
        fig.suptitle(f"Posterior traces — {param}", y=1.01)
        fig.tight_layout()
        out_path = output_dir / f"trace_{param}.png"
        fig.savefig(out_path, dpi=120, bbox_inches="tight")
        plt.close(fig)
        written.append(out_path)

    return written
