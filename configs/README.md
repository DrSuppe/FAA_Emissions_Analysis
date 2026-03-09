# Config Directory Guide

This directory contains YAML configuration templates used by scripts and pipelines.

## File responsibilities
- `example_ingestion_config.yaml`  
  Maps raw station/FTIR input columns and alignment settings.
- `example_model_config.yaml`  
  Defines the staged forward-model setup (mechanism, species, stages, restrictions).
- `example_inference_config.yaml`  
  Defines Bayesian inference options and comparison targets.
- `example_plot_config.yaml`  
  Defines plotting defaults (species, snapshots, output path).

## Fast navigation
- Importing new campaign data: start with `example_ingestion_config.yaml`.
- Tuning combustor/probe/line physics: start with `example_model_config.yaml`.
- Changing posterior run behavior: start with `example_inference_config.yaml`.
- Adjusting figure generation defaults: start with `example_plot_config.yaml`.

## Naming convention for future configs
- Use `<campaign>_<purpose>.yaml`, for example:
  - `camp12_model.yaml`
  - `camp12_ingestion.yaml`
  - `camp12_inference.yaml`
