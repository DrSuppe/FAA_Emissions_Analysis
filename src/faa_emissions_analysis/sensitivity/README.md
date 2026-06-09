# sensitivity — Morris Elementary-Effects Screening

Answers the question: *which stage parameters most influence predicted emissions?*

## Method

The **Morris method** (Morris 1991) uses one-at-a-time (OAT) parameter perturbations
along random trajectories through the parameter space.  It requires only
`r × (k+1)` forward model evaluations for `r` trajectories and `k` parameters —
far fewer than full Sobol or variance-based indices.

### Summary statistics

| Statistic | Meaning |
|-----------|---------|
| **μ\*** | Mean \|EE\| — overall parameter influence |
| **σ** | Std-dev of EE — non-linearity or interaction with other parameters |
| **μ** | Mean EE — directional bias (positive → increases output) |

## Usage

```python
from faa_emissions_analysis.sensitivity import (
    MorrisConfig, ParameterSpec, make_model_fn, morris_screening
)

specs = [
    ParameterSpec("pilot_primary.residence_time_s",  low=0.001, high=0.010),
    ParameterSpec("pilot_primary.wall_temperature_k", low=1200., high=1600.),
    ParameterSpec("main_zone.mix_fraction",           low=0.01,  high=0.10),
]

model_fn = make_model_fn(
    base_config=my_config,
    inlet_df=inlet_df,
    specs=specs,
    output_species=["CO", "NO"],
    output_location="heated_ptfe_to_ftir",
)

results = morris_screening(model_fn, specs, config=MorrisConfig(n_trajectories=15))
print(results.sort_values("mu_star", ascending=False))
```

## Parameter addressing

Parameters are addressed as `"<stage_name>.<field_name>"`.  Supported fields:

- `residence_time_s`
- `pressure_drop_pa`
- `wall_temperature_k`
- `ua_w_m2_k`
- `mix_fraction`
