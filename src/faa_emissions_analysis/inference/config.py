"""YAML loading for inference configuration."""

from __future__ import annotations

from pathlib import Path
from typing import Any, Mapping

from faa_emissions_analysis._yaml import load_yaml

from .types import InferenceConfig, PriorConfig


def _parse_priors(payload: Mapping[str, Any]) -> PriorConfig:
    return PriorConfig(
        scale_log_std=float(payload.get("scale_log_std", 0.30)),
        bias_ref_fraction=float(payload.get("bias_ref_fraction", 0.05)),
        sigma_ref_fraction=float(payload.get("sigma_ref_fraction", 0.05)),
        discrepancy_ref_fraction=float(payload.get("discrepancy_ref_fraction", 0.10)),
    )


def load_inference_config(path: Path) -> tuple[InferenceConfig, dict[str, Any]]:
    """Load InferenceConfig and comparison settings from a YAML file.

    Returns
    -------
    config:
        Parsed :class:`InferenceConfig`.
    comparison:
        Dict with keys ``predicted_location``, ``observed_location``, and
        ``species`` sourced from the ``comparison:`` block of the YAML.
    """
    payload = load_yaml(path)

    inf = dict(payload.get("inference", {}))  # copy so pop is safe
    priors_raw = inf.pop("priors", {})

    config = InferenceConfig(
        num_warmup=int(inf.get("num_warmup", 700)),
        num_samples=int(inf.get("num_samples", 1200)),
        num_chains=int(inf.get("num_chains", 1)),
        random_seed=int(inf.get("random_seed", 7)),
        time_tolerance_s=float(inf.get("time_tolerance_s", 0.6)),
        priors=_parse_priors(priors_raw),
    )

    comparison: dict[str, Any] = payload.get("comparison", {})
    return config, comparison
