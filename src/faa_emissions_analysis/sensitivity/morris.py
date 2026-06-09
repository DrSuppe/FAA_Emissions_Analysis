"""Morris elementary-effects sensitivity screening.

Reference: Morris (1991), "Factorial sampling plans for preliminary
computational experiments", Technometrics 33(2), 161-174.

The method answers the question: *which input parameters matter most for
a given output?*  It is low-cost (r × (k+1) model runs for r trajectories
and k parameters) and does not assume linearity or additivity.

Summary statistics
------------------
μ* (mu_star)
    Mean of absolute elementary effects — measures overall influence.
σ (sigma)
    Std-dev of elementary effects — measures non-linearity / interactions.

A parameter with high μ* and low σ has a large, nearly-linear effect.
A parameter with high μ* and high σ is either non-linear or interacts
strongly with other parameters.
"""

from __future__ import annotations

from typing import Callable, Sequence

import numpy as np
import pandas as pd

from .types import MorrisConfig, ParameterSpec


def _morris_trajectories(
    k: int,
    p: int,
    r: int,
    rng: np.random.Generator,
) -> np.ndarray:
    """Generate r Morris trajectories in the unit hypercube.

    Each trajectory has k+1 rows (base point + k one-at-a-time steps).
    The step size is Δ = p / (2*(p-1)).

    Returns
    -------
    Array of shape (r, k+1, k) — trajectories × (k+1 points) × k parameters,
    with values in [0, 1].
    """
    delta = p / (2.0 * (p - 1.0))
    # Grid levels: 0, 1/(p-1), 2/(p-1), ..., 1
    levels = np.linspace(0.0, 1.0, p)

    trajectories = np.empty((r, k + 1, k))
    for i in range(r):
        # Random starting point on the grid, such that x + delta stays in [0,1].
        # Starting values drawn from the lower p/2 grid levels.
        x0 = rng.choice(levels[: p // 2], size=k)
        x = x0.copy()
        trajectories[i, 0] = x.copy()
        # Random order to perturb parameters.
        order = rng.permutation(k)
        for j, param_idx in enumerate(order):
            x = x.copy()
            sign = rng.choice([-1.0, 1.0])
            x[param_idx] = np.clip(x[param_idx] + sign * delta, 0.0, 1.0)
            trajectories[i, j + 1] = x.copy()

    return trajectories


def _scale_point(unit_point: np.ndarray, specs: Sequence[ParameterSpec]) -> dict[str, float]:
    """Map a unit-hypercube point to physical parameter values."""
    return {
        spec.path: float(spec.low + unit_point[i] * (spec.high - spec.low))
        for i, spec in enumerate(specs)
    }


def morris_screening(
    model_fn: Callable[[dict[str, float]], np.ndarray],
    specs: Sequence[ParameterSpec],
    config: MorrisConfig | None = None,
    progress: bool = True,
) -> pd.DataFrame:
    """Run Morris elementary-effects screening.

    Parameters
    ----------
    model_fn:
        Callable that accepts a ``{path: value}`` dict of parameter overrides
        and returns a 1-D numpy array of scalar outputs (one per species /
        quantity of interest).  This is the function being screened.
    specs:
        Ordered list of :class:`ParameterSpec` objects defining the
        parameter search space.
    config:
        Morris hyper-parameters.  Defaults to :class:`MorrisConfig`.
    progress:
        Print progress to stdout during trajectory evaluation.

    Returns
    -------
    DataFrame with columns:

    ``parameter``, ``output_index``, ``mu_star``, ``sigma``, ``mu``

    One row per (parameter, output) combination.
    """
    config = config or MorrisConfig()
    k = len(specs)
    rng = np.random.default_rng(config.random_seed)

    trajectories = _morris_trajectories(k=k, p=config.n_levels, r=config.n_trajectories, rng=rng)
    # trajectories: (r, k+1, k)

    total_runs = config.n_trajectories * (k + 1)
    if progress:
        print(f"Morris screening: {config.n_trajectories} trajectories × {k+1} points = {total_runs} runs")

    # Evaluate model at every point.
    outputs: list[np.ndarray] = []
    for traj_idx in range(config.n_trajectories):
        traj_outputs = []
        for pt_idx in range(k + 1):
            params = _scale_point(trajectories[traj_idx, pt_idx], specs)
            y = model_fn(params)
            traj_outputs.append(np.asarray(y, dtype=float))
            if progress:
                run_no = traj_idx * (k + 1) + pt_idx + 1
                print(f"  run {run_no}/{total_runs}", end="\r")
        outputs.append(np.stack(traj_outputs))  # (k+1, n_outputs)
    if progress:
        print()

    # outputs: list of r arrays, each (k+1, n_outputs)
    n_outputs = outputs[0].shape[1] if outputs[0].ndim > 1 else 1

    # Compute elementary effects for each trajectory.
    # For each consecutive pair in the trajectory, the step perturbed exactly
    # one parameter; we find which one from the unit coordinates.
    ee = np.zeros((config.n_trajectories, k, n_outputs))  # (r, k, n_out)
    delta = config.n_levels / (2.0 * (config.n_levels - 1.0))

    for i in range(config.n_trajectories):
        traj = trajectories[i]       # (k+1, k)
        traj_out = outputs[i]        # (k+1, n_out)
        for j in range(k):
            diff_x = traj[j + 1] - traj[j]   # (k,) — one element non-zero
            param_idx = int(np.argmax(np.abs(diff_x)))
            step = diff_x[param_idx]           # ±delta in unit space
            # Physical step size.
            phys_delta = step * (specs[param_idx].high - specs[param_idx].low)
            if abs(phys_delta) < 1e-30:
                continue  # degenerate step — skip
            diff_y = traj_out[j + 1] - traj_out[j]   # (n_out,)
            ee[i, param_idx] = diff_y / phys_delta

    # Aggregate: μ* and σ over trajectories.
    mu_star = np.mean(np.abs(ee), axis=0)   # (k, n_out)
    sigma = np.std(ee, axis=0)              # (k, n_out)
    mu = np.mean(ee, axis=0)               # (k, n_out)

    rows = []
    for pi, spec in enumerate(specs):
        for oi in range(n_outputs):
            rows.append(
                {
                    "parameter": spec.path,
                    "output_index": oi,
                    "mu_star": float(mu_star[pi, oi]),
                    "sigma": float(sigma[pi, oi]),
                    "mu": float(mu[pi, oi]),
                }
            )

    return pd.DataFrame(rows)


def make_model_fn(
    base_config,
    inlet_df,
    specs: Sequence[ParameterSpec],
    output_species: Sequence[str],
    output_location: str,
    output_statistic: str = "mean",
) -> Callable[[dict[str, float]], np.ndarray]:
    """Build a ``model_fn`` compatible with :func:`morris_screening`.

    The returned callable perturbs the base config, runs
    :meth:`CanteraPathModel.simulate_timeseries`, and extracts a scalar
    summary per species at ``output_location``.

    Parameters
    ----------
    base_config:
        :class:`ForwardModelConfig` template.
    inlet_df:
        Inlet conditions DataFrame (same format as
        :meth:`CanteraPathModel.simulate_timeseries`).
    specs:
        Parameter specifications (used for perturbation).
    output_species:
        Which species to include in the output vector.
    output_location:
        Stage name to extract from the simulation output.
    output_statistic:
        ``"mean"`` or ``"final"`` — how to reduce the time-series per species.
    """
    from faa_emissions_analysis.model.stages import CanteraPathModel
    from .perturbation import perturb_config

    def _fn(parameter_values: dict[str, float]) -> np.ndarray:
        cfg = perturb_config(base_config, parameter_values)
        model = CanteraPathModel(cfg)
        result = model.simulate_timeseries(inlet_df)
        loc = result[result["location"] == output_location]
        if loc.empty:
            return np.zeros(len(output_species))
        vals = []
        for sp in output_species:
            col = loc[sp] if sp in loc.columns else loc.get(sp, None)
            if col is None:
                vals.append(0.0)
            elif output_statistic == "final":
                vals.append(float(col.iloc[-1]))
            else:
                vals.append(float(col.mean()))
        return np.array(vals)

    return _fn
