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

## Pipeline quick start
1. Install base dependencies:
   - `python -m pip install -e .`
2. Optional Bayesian stack:
   - `python -m pip install -e '.[inference]'`
3. Put source files in `data/raw/` and edit:
   - `configs/example_ingestion_config.yaml`
   - `configs/example_model_config.yaml`
4. Prepare harmonized inputs:
   - `python scripts/prepare_data.py --config configs/example_ingestion_config.yaml`
   - Smoke test with provided synthetic files in `data/raw/`.
5. Run forward model:
   - `python scripts/run_forward_model.py --inlet-csv data/processed/station_harmonized.csv --model-config configs/example_model_config.yaml`
6. Run Bayesian calibration:
   - `python scripts/run_inference.py --predicted-csv data/processed/forward_simulation.csv --observed-csv data/processed/ftir_harmonized.csv --predicted-location heated_ptfe_to_ftir --species CO2 CO NO NO2`
7. Generate evolution plots:
   - `python scripts/plot_evolution.py --input-csv data/processed/forward_simulation.csv --species CO2 CO NO NO2`

## Notes
- `scripts/run_forward_model.py` expects Cantera to be installed.
- `scripts/run_inference.py` expects JAX + NumPyro (the `inference` extra).
- The current model is a scientifically structured scaffold (3-zone + line chain) and is designed to be calibrated with your campaign data.
