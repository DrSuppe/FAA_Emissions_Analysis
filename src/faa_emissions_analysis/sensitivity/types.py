"""Type definitions for sensitivity screening."""

from __future__ import annotations

from dataclasses import dataclass, field


@dataclass(frozen=True)
class ParameterSpec:
    """One scalar parameter to perturb during Morris screening.

    ``path`` addresses a field inside a :class:`StageConfig` using the
    notation ``"<stage_name>.<field_name>"``.  For example::

        ParameterSpec(path="pilot_primary.residence_time_s", low=0.001, high=0.010)

    Supported stage fields: ``residence_time_s``, ``pressure_drop_pa``,
    ``wall_temperature_k``, ``ua_w_m2_k``, ``mix_fraction``.
    """

    path: str           # "<stage_name>.<field_name>"
    low: float          # lower bound of the parameter range
    high: float         # upper bound of the parameter range

    def __post_init__(self) -> None:
        if "." not in self.path:
            raise ValueError(f"ParameterSpec.path must be '<stage>.<field>', got: {self.path!r}")
        if self.low >= self.high:
            raise ValueError(f"ParameterSpec low={self.low} must be < high={self.high} for {self.path!r}")

    @property
    def stage_name(self) -> str:
        return self.path.split(".")[0]

    @property
    def field_name(self) -> str:
        return self.path.split(".")[1]


@dataclass(frozen=True)
class MorrisConfig:
    """Hyper-parameters for the Morris elementary-effects method."""

    n_trajectories: int = 10   # number of Morris trajectories (r)
    n_levels: int = 4           # number of grid levels (p); Δ = p/(2*(p-1))
    random_seed: int = 42
    output_species: tuple[str, ...] = field(default_factory=lambda: ("CO2", "CO", "NO", "NO2"))
    output_location: str = "heated_ptfe_to_ftir"
    output_statistic: str = "mean"  # "mean" | "final" — how to reduce time-series output
