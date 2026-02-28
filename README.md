# FAA_Emissions_Analysis

Physics-informed combustor-to-FTIR emissions analysis using Cantera.

## Scope (v1)
- Forward model from injector -> combustor zones -> probe -> sampling line -> venturi -> FTIR
- Inverse inference of probe-inlet composition from FTIR + test-article sensors
- Uncertainty quantification via sensitivity screening + Bayesian inference

## Repository layout
- `src/faa_emissions_analysis/`: package code
- `configs/`: model and run configurations
- `data/raw/`: source inputs (Excel, FTIR)
- `data/processed/`: harmonized intermediate datasets
- `notebooks/`: exploratory and validation notebooks
- `reports/`: generated figures/tables/summaries
- `tests/`: unit + integration tests

## Quick start
1. Create environment and install dependencies.
2. Put input files into `data/raw/`.
3. Define case config in `configs/`.
4. Run simulation/inference scripts from `scripts/`.

