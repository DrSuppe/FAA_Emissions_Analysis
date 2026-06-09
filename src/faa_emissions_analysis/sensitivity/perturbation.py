"""Helpers for creating perturbed ForwardModelConfig instances."""

from __future__ import annotations

import dataclasses

from faa_emissions_analysis.model.types import ForwardModelConfig, StageConfig

# Stage fields that can be varied by Morris screening.
_MUTABLE_FIELDS = frozenset(
    {"residence_time_s", "pressure_drop_pa", "wall_temperature_k", "ua_w_m2_k", "mix_fraction"}
)


def perturb_config(
    base: ForwardModelConfig,
    parameter_values: dict[str, float],
) -> ForwardModelConfig:
    """Return a new :class:`ForwardModelConfig` with specified parameters overridden.

    Parameters
    ----------
    base:
        Template configuration.
    parameter_values:
        Mapping of ``"<stage_name>.<field_name>"`` → new scalar value.  Only
        the fields listed in ``_MUTABLE_FIELDS`` may be varied.

    Returns
    -------
    A new frozen :class:`ForwardModelConfig` with the requested overrides
    applied.  All other fields are unchanged.

    Raises
    ------
    KeyError
        If a stage name is not found in the base config.
    ValueError
        If a field is not in the set of supported mutable fields.
    """
    stage_overrides: dict[str, dict[str, float]] = {}
    for path, value in parameter_values.items():
        stage_name, field_name = path.split(".", 1)
        if field_name not in _MUTABLE_FIELDS:
            raise ValueError(
                f"Field {field_name!r} is not in the set of mutable fields: {sorted(_MUTABLE_FIELDS)}"
            )
        stage_overrides.setdefault(stage_name, {})[field_name] = value

    new_stages = []
    stage_by_name = {s.name: s for s in base.stages}
    for stage in base.stages:
        overrides = stage_overrides.get(stage.name, {})
        if overrides:
            if stage.name not in stage_by_name:
                raise KeyError(f"Stage {stage.name!r} not found in base config.")
            new_stage = dataclasses.replace(stage, **overrides)
        else:
            new_stage = stage
        new_stages.append(new_stage)

    return dataclasses.replace(base, stages=tuple(new_stages))
