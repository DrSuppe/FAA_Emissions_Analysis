# Module Map (AI-Optimized)

Use this file as the first stop before opening code files.

## Top-level package
- `src/faa_emissions_analysis/__init__.py`  
  Re-export surface. Import from here when you want stable APIs.

## Forward model
- `src/faa_emissions_analysis/model/types.py`  
  Dataclasses for stage/restriction/model configs.
- `src/faa_emissions_analysis/model/config.py`  
  YAML -> dataclass parsing.
- `src/faa_emissions_analysis/model/physics_utils.py`  
  Choked-flow and composition helper math.
- `src/faa_emissions_analysis/model/stages.py`  
  Cantera reactor path simulation logic.

## Ingestion
- `src/faa_emissions_analysis/ingestion/types.py`  
  Source config dataclass and standard column constants.
- `src/faa_emissions_analysis/ingestion/loaders.py`  
  CSV/Excel readers and source table normalization.
- `src/faa_emissions_analysis/ingestion/align.py`  
  Time alignment between station and FTIR streams.
- `src/faa_emissions_analysis/ingestion/config.py`  
  YAML-driven pipeline assembly.

## Inference
- `src/faa_emissions_analysis/inference/types.py`  
  MCMC settings dataclass.
- `src/faa_emissions_analysis/inference/alignment.py`  
  Predicted-vs-observed alignment.
- `src/faa_emissions_analysis/inference/nuts.py`  
  NumPyro NUTS run function.
- `src/faa_emissions_analysis/inference/summary.py`  
  Posterior summary tables.

## Plotting
- `src/faa_emissions_analysis/plotting/heatmaps.py`  
  Spatiotemporal heatmaps.
- `src/faa_emissions_analysis/plotting/species_profiles.py`  
  Time traces and distance snapshots.
- `src/faa_emissions_analysis/plotting/pack.py`  
  Bundle generation for report figures.
- `src/faa_emissions_analysis/plotting/utils.py`  
  Plot helper checks and filesystem helpers.

## CLI scripts
- `scripts/prepare_data.py`  
  Raw -> harmonized/aligned CSV.
- `scripts/run_forward_model.py`  
  Run staged Cantera model over time series.
- `scripts/run_inference.py`  
  Run Bayesian calibration from predicted vs FTIR.
- `scripts/plot_evolution.py`  
  Generate figure pack from simulation output.

## Editing guideline
- Keep each file focused on one concern.
- Prefer adding a module over growing an existing module beyond ~150 lines.
- Keep `__init__.py` files as thin re-export layers only.
