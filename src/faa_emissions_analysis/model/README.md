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

## Reacting forward model (combustion)

The model now BURNS a fresh fuel/air charge rather than relaxing pre-burned gas.

- **Mechanism**: `mechanisms/A2NOx_skeletal.yaml` — HyChem A2 Jet-A (lumped pseudo-species
  `POSF10325`, C11H22) + NOx skeletal (71 species, 538 reactions). Provenance and required
  citation: `mechanisms/MECHANISM_PROVENANCE.md` (Saggese et al., *Combust. Flame* 212 (2020)
  270-278; Glarborg et al., *PECS* 67 (2018) 31-68). It is HIGH-TEMPERATURE chemistry only —
  no low-T / cool-flame / autoignition pathways.
- **Inlet**: `ForwardModelConfig.fuel_composition` + `oxidizer_composition` + `equivalence_ratio`
  build the inlet via `ct.Solution.set_equivalence_ratio(phi, fuel, oxidizer)` at
  `t_inlet_air_k` / `inlet_pressure_pa` (see `CanteraPathModel.flame_inlet_state`).
- **Flame anchoring (pilot ignition)**: a ~700 K premix does NOT autoignite in the few-ms stage
  residence time (ignition delay > 0.1 s at 700 K; ~3 ms only above ~1100 K). A real pilot is
  stabilized on a hot recirculation zone, so an UNBURNED fuel-bearing stage starts its reactor at
  the stage **wall temperature** when that is hotter than the gas (`_advance_stage`). This ties
  ignition to an existing config value (pilot wall = 1400 K), not a new free knob.
- **Station data = validation target**: the station CSV (`PROBE_INLET`, ~0.60 m) is what the
  prediction is compared against — it is no longer the inlet. `simulate_timeseries` seeds every
  trajectory with the flame inlet and uses the CSV only for timestamps and mass flow.

## Calibration (`scripts/calibrate_phi.py`)

Sweeps `phi` to minimize the relative SSR of (O2, CO2, H2O, CO) between the predicted
post-main-zone composition and the station target. `t_inlet_air_k` is a documented assumption
(compressor-discharge ~700 K), NOT a fit knob; the probe temperature is an independent
validation check. The synthetic target is stoichiometrically inconsistent for this fuel
(H2O/CO2 ~ 1.63 vs ~1.0 for C11H22), so H2O cannot be matched — residuals are reported honestly.
