# Model Package Guide

This package contains the combustor-to-FTIR forward model.

## File responsibilities
- `__init__.py`  
  Stable import surface for model APIs.
- `types.py`  
  Dataclasses for model configuration objects (`StageConfig`, `RestrictionConfig`, `ForwardModelConfig`).
- `config.py`  
  YAML parsing/loading into model dataclasses.
- `physics_utils.py`  
  Low-level math and state helpers (choked-flow, composition normalization/mixing).
- `stages.py`  
  Main Cantera simulation flow (`CanteraPathModel`) and stage advancement logic.

## Fast navigation
- Need to change model structure or stages: open `stages.py`.
- Need to add/change physical equations: open `physics_utils.py`.
- Need to change YAML schema or defaults: open `config.py` and `types.py`.
