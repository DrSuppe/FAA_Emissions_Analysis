# 04 CRN proposal for the COMRAD swirl injector (quorum synthesis)

Inputs: `crn_01` literature (L), `crn_02` physics (P), `quorum_03` skeptic (S), D2-D5. Proposal only until D9-D11 are decided.

## 1. Agreement, conflict, ruling

| Topic | Literature (L) | Physics (P) | Ruling |
|---|---|---|---|
| Core zoning | T1: pilot, main, recirc PSRs, film mixer, burnout PFR (L Sec. 4) | Same, IRZ and CRZ split (P Sec. 2) | Merge IRZ+CRZ: emissions cannot separate them (L Sec. 5) [High] |
| Unmixedness | Phi bins only in T2, if T1 fails (L Sec. 4) | 3-PSR bank per circuit; premix underpredicts NOx (P Sec. 2, 5) | Pilot bank in Stage A, main single PSR: NOx is from the pilot hot tail (P Sec. 1.1); D2b already showed premixed zones fail [Medium] |
| Liquid / evaporation | Evaporator element in T2 (L Sec. 2) | x_l bypass per circuit (P Sec. 2) | Stage B; UHC not a Stage A target [Medium] |
| Recycle ratio, tau | Not pinnable by emissions; tuned per case (Innocenti, L Sec. 2, 5) | Fix from PIV (P Sec. 4.1) | Fixed from PIV/geometry, never fitted; removes the S-O1 degeneracy [High] |
| Film air | Joins late; unquantified (L Sec. 2) | beta from carbon balance (P Sec. 3) | beta from D6 carbon balance per case [High] |
| Heat loss | One q cannot fit NOx and CO (Grimm, L Sec. 5) | Scaffold UA negligible (P Sec. 5) | One global q; CO misfit reported, not absorbed [Medium] |
| NO2/NOx | Silent | Not a combustor observable; fit total NOx (P Sec. 3) | P; NO2 split settled by experiment (Sec. 3.4) [High] |

## 2. Network

### Stage A (required for the 2026-12-21 draft): 7 combustor reactors + sampling train

```
pilot air+fuel        main air+fuel                film air
      |                    |                          |
 [P1|P2|P3] <--r--+       [M]                         |
   (S_P, q)       |        |                          |
      +-----> [R] recirc <-+   (IRZ+CRZ, q)           |
      v           v        v                          |
      +--------> [X] mixer <                          |
                  |                                   |
             [B] burnout PFR (q) --> [F] film PFR <---+ (k_f)
                                          |
                                       PROBE -> sampling train (D3)
```

- P1-P3: PSRs, pilot air + fuel (split 29.7 % at P&M, Murdock Sec. 2), bins at mean phi, +/- S_P, fixed weights; loss q. M: main air + fuel PSR (air only at pilot-only: the quench stream, P Sec. 2). R: PSR taking fraction r of P+M outflow, returned to the pilot bank (outer iteration).
- X mixer; B burnout PFR; F PFR with film air at rate k_f, probe film share = beta. Gas phase, HyChem A2 + NOx, prevaporized.

| Parameter | Class | Source / prior | Pinned by | Sharing |
|---|---|---|---|---|
| a_p : a_m : a_f | hardware | injector ACd (D2, from rig team) | drawings | global |
| fuel split, phi, P3, T3, m_air | hardware | logged (D1) | metering | per case |
| V_P, V_M, V_R, V_B | flow-field | geometry + PIV/OH* extents | PIV (Sec. 4) | global; tau = rho V/m_dot per case |
| r | flow-field | PIV reverse mass flux | PIV | one per mode (P&M, pilot-only) |
| beta | flow-field | carbon-balance vs metered FAR | D6 (kinetics-free) | per case, computed |
| S_P = S_0 + S_1 (T_fuel - T_ref) | free | S_1 sign from OH* wing shift (Sec. 4) | NOx phi-slope; NOx vs T_fuel at fixed phi (P Sec. 3) | global, all fuels |
| q | free | radiative ordering from LII | NOx level | global |
| k_f | free | none | CO | global per mode |

Free: **4** (S_0, S_1, q, k_f). Sampling train: hardware only (D3).

### Stage B (only if Stage A misses a named trend)

Triggers: (i) UHC vs T_fuel at pilot-only; (ii) NOx vs T_fuel at fixed phi missed by the linear S_P law; (iii) HEFA/GS190 hold-out NOx outside the band. Adds per-circuit evaporator + liquid bypass x_l(T_fuel) evaporating in X (P Sec. 2; John et al. per L Sec. 2) and a 3-bin main bank on the S_P law: +4 reactors, +2 free (x_l level, slope; anchored by the ~50 % droplet reduction at 338 K, Murdock via P Sec. 4.3).

## 3. Identifiability plan

1. **Count.** CO2, H2O, carbon balance are set by phi; they yield beta and the H/C check (P Sec. 3), validating, not calibrating. Informative per case: total NOx, CO (2; UHC in Stage B). 4 global parameters over tens of cases: overdetermined globally, underdetermined per case [High]; no per-case calibration (S-O1).
2. **Sharing.** Hardware and volumes global; tau = rho V/m_dot; r per mode (PIV); S_P linear in T_fuel, identical across fuels (the injector does not know the fuel, S-O1); q global; k_f per mode. Fuel effects must emerge from chemistry and properties: that is the test.
3. **Hold-out.** Calibrate on Jet A P&M phi sweeps at 366 and 589 K. Predict without refit EI NOx and EI CO for: Jet A 478 K (T_fuel interpolation), all HEFA and GS190 cases (fuel transfer), the pilot-only sweep (mode transfer; only PIV/OH* inputs change). Pass band = per-case replicate scatter (S-O2). Report bounds per parameter, flagging any at a range limit (S Sec. 1; D5).
4. **Sample-line check (experiment request, S Fig. B).** Hold Jet A, P&M, phi 0.49, T_fuel 366 K. Vary one at a time: (a) sample flow via venturi/bypass, >= 3 levels; (b) heated-line setpoint, >= 3 levels in the condensation-safe range; (c) if feasible, line length by a known extension. Log NO, NO2, CO, line wall T, sample flow, probe coolant T. Plot NO2/NOx vs computed line residence time: intercept = in-chamber NO2 fraction, slope tests the gas-phase rate (D4). Add NO and NO2 span gas injected at the probe tip. Without this: "model-consistent", not "inferred" (S Sec. 3).

## 4. How the optical data enters

1. **PIV (Philo et al., via Murdock Sec. 2), P&M and pilot-only nominal:** zero-axial-velocity surface and reverse mass flux -> V_R, r; jet extents -> V_P, V_M; uncertainty into D5. [Guess] that quantitative fields exist at these points: ask the rig team.
2. **OH* (Murdock Fig. 2) / OH-PLIF, P&M vs pilot-only across T_fuel:** heat-release location assigns fuel to reactors (pilot-only peak on the centreline at x/Dj 1.5: pilot fuel burns in R); the T_fuel wing shift fixes the sign of S_1. OH-PLIF is undocumented in the position files [Guess]; if available, its OH extent replaces the line-of-sight OH* volume.
3. **LII (Murdock Sec. 3), pilot flow and CRZ, Jet A vs HEFA:** relative only, so it constrains the ordering of radiative loss (Jet A >= HEFA) on q and supports Fig. C as rank correlation, never a calibrated input (S Sec. 3).

## 5. Claims

"The reactor network is an interpretive model: residence times and recirculation are fixed from geometry and PIV, and four global effective parameters are calibrated on a Jet A subset and tested without refitting on held-out fuel temperatures, fuels and operating mode. Combustor-exit NOx is reported as a value with sensitivity bounds where the hold-out passes; exit CO and UHC as bounds conditional on the quench representation. The sampling-train NO2 fraction is the homogeneous gas-phase part, checked against the measured residence-time extrapolation; wall reduction and PTFE uptake are not modelled, and all bounds are parametric, not structural." [High if Sec. 3.3-3.4 are done; Medium otherwise]

## 6. Open decisions (to become D-entries)

1. **D9 Stage A topology.** (a) T1 + 3-bin pilot bank (7 reactors, 4 free); (b) pure T1 (5, 3 free; likely repeats the June NOx underprediction); (c) T2 now (11, 6 free; underdetermined). Recommend (a) [Medium].
2. **D10 Calibration design.** (a) global parameters, Jet A P&M 366/589 K calibrate, rest held out; (b) calibrate all, hold out NO only (S Sec. 3); (c) per case (fails S-O1). Recommend (a). Consequence: the abstract should say residence times and air split are fixed from hardware and PIV, and effective mixing and heat-loss parameters are calibrated.
3. **D11 Sample-line test and wording.** (a) request the Sec. 3.4 test + span gas before camera-ready, keep "inferred"; (b) no test, "model-consistent". Recommend (a), using (b) wording in the December draft until data exist [High].

## 7. Build plan (src/faa_emissions_analysis/model/ and siblings)

1. **Network schema** (`types.py`, `config.py`; combustor YAML + separate sampling-train YAML from D3). Accept: configs round-trip; existing train chain still loads.
2. **Combustor builder** (new `network.py`: PSR bank, recycle outer loop, PFRs; HyChem A2 + NOx). Accept: element/mass balance closed to solver tolerance; r = S_P = q = 0 reduces to one adiabatic PSR; long tau tends to equilibrium.
3. **Probe interface + train** (`stages.py` takes F outflow; beta in `physics_utils.py`). Accept: frozen-chemistry run preserves composition; beta reproduces measured FAR per case.
4. **Case driver** (`ingestion` logged P3, T3, flows, T_fuel -> network). Accept: whole matrix runs with no hand-set per-case values.
5. **Calibration, hold-out, bounds** (`inference/`, `sensitivity/morris.py`, `perturbation.py`). Accept: hold-out EI table vs replicate band; Morris ranking and bounds; range-limit flags.
