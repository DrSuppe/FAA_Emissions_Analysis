# CRN 02: combustion physicist's view (flow/flame physics -> network -> identifiability)

Read: Murdock et al. GT2026 (`references/2026_TurboExpo_Murdock_LII.txt`, Sec. 1-3, Fig. 2); D2/D3/D5; `02_fuel_comparison_hypotheses.md`; the config scaffold. Everything else is tagged reasoning.

## 1. Processes that set probe NOx, CO, UHC (by importance)
1. **Pilot-side local stoichiometry and unmixedness -> NOx.** At phi 0.49 the main flame makes little thermal NO in ms; NOx comes from the richer pilot and near-stoichiometric pockets [Medium: thermal NO is exponential in T, so the hot tail of the phi pdf dominates]. *T_fuel*: vaporization -> better premixing (lower NOx) vs sensible enthalpy (+~15-20 K Tad for +300 K: 0.032 x 2.2 kJ/kgK x 300 K / 1.25 kJ/kgK) [Medium, assumed cp]; these oppose. *Fuel type*: volatility, H/C (small), soot radiation (Jet A LII ~3.5x HEFA, Murdock Sec. 3).
2. **Hot-product residence in the recirculation zones -> NOx.** CRZ and IRZ hold near-flame-T products long; NO accrues there [High]. Fuel-independent to first order; flame wings move downstream/inward with T_fuel (Murdock Sec. 3.1, citing Philo et al.) [Medium].
3. **Quench by cold air -> CO, UHC.** Film air and, at pilot-only, the unfuelled main air freeze CO oxidation [High pilot-only, Medium pilot-and-main]. T_fuel/type act via how much fuel is unburned on meeting cold air (Jet A heavy tail, aromatics) [Medium].
4. **Liquid survival / flash boiling -> UHC.** Liquid in cold streams is the direct UHC source; heating shortens penetration and evaporation (Murdock Sec. 1); flash boiling >~450 K changes regime [Medium].
5. **Wall/window/bluff-body heat loss and soot radiation -> NOx down a few %.** [Low-Medium]
6. **Probe/line chemistry -> NO2/NOx, CO.** Separate network (D3/D4); degenerate with in-chamber NO2 formation in quench layers.

## 2. Minimum network
```
 pilot air(a_p)+pilot fuel        main air(a_m)+main fuel         film air(a_f)
        |                                 |                            |
   [EVAP_P mixer]--x_l,P liquid--+   [EVAP_M mixer]--x_l,M--+          |
        |  phi-pdf (S_P)         |        | phi-pdf (S_M)   |          |
   [PSR_P bank x3] <---r_I---+   |   [PSR_M bank x3]        |          |
        |         \          |   |        |                 |          |
        |          +-->[PSR_IRZ]<---------+ (UA_bb)         |          |
        v                                 v                 |          |
   [PSR_CRZ] <------------- r_C ---- [MIX_core] <-----------+(late evap)
   (UA_win)  ----------------------------> |                           |
                                      [PFR_burnout] (UA_wall) --> contraction
                                           |                           |
                                      [PFR_wallmix] <--- beta(x) ------+
                                           |
                                        PROBE  -> sampling-train network (D3)
```
EVAP passes (1-x_l) as gas to a 3-PSR bank spanning a phi pdf of width S; x_l bypasses and evaporates late in MIX_core. IRZ (r_I) and CRZ (r_C) recycle hot products to the pilot bank. Pilot-only: main circuit is air only, the quench stream. Heat loss: bluff body, windows, liner. Film air joins only in PFR_wallmix; beta depends on probe position vs the contraction.

| Class | Parameters |
|---|---|
| Hardware (drawings, D2/D3) | a_p:a_m:a_f effective areas; fuel split (metered); chamber/contraction geometry; probe position; coolant/wall T |
| Flow-field (PIV, OH*) | V_CRZ, V_IRZ -> tau; reverse mass flux -> r_C, r_I; flame location (which reactor burns which fuel) |
| Free | S_P, S_M; x_l (per circuit, T_fuel-dependent); UA scale; beta |

## 3. Identifiability (per case: CO2, CO, H2O, NO, NO2, UHC)
- **beta** is pinned by the carbon balance: sample fuel-air ratio vs metered phi gives the film/dilution share at the probe, kinetics-free [High] (the D6 check, doing double duty).
- **H/C** from H2O/CO2 checks surrogate stoichiometry [High].
- **NOx** alone is degenerate in {pilot local phi, S_P, tau_CRZ, UA}: richer, less mixed, longer, adiabatic all raise it [High]. Fix pilot phi from hardware air split and tau from PIV; then the *phi-sweep slope* d ln NOx/d phi pins S (unmixedness flattens the slope because the hot tail dominates) [Medium], and the *T_fuel trend at fixed phi* pins S(T_fuel) after removing the computed sensible-enthalpy effect [Medium].
- **UHC vs CO** separates bypass from quench: UHC needs fuel that never saw a flame (x_l, cold-stream escape); CO comes from partially oxidized products quenched by film/main air. UHC pins x_l, then CO pins quench (UA, film mixing rate) [Medium]. tau_burnout and UA stay mutually degenerate unless PIV fixes tau.
- **NO2/NOx** is not a combustor observable: in-chamber HO2+NO in the film mixing layer is degenerate with probe conversion [Medium]. Use total NOx.
- ~4 informative numbers per case vs 6 free parameters: underdetermined per case [High]. Share parameters across the matrix with physical scaling (tau ~ rho V/m_dot; S, x_l monotone in T_fuel/T_boil) and fix tau, r from PIV.

## 4. Use diagnostics to constrain, not fit
1. **PIV**: reverse mass flux across CRZ/IRZ boundaries -> r_C, r_I; V/m_dot -> tau. Fixed inputs; PIV uncertainty goes into D5 sweeps.
2. **OH***: heat-release location decides topology per condition. Pilot-and-main peaks along the main flow (x/Dj 0.5, y/Dj 1.0); pilot-only compresses to the centreline, peak at x/Dj 1.5 (Murdock Sec. 3, pilot-only discussion), so pilot-only fuel burns in the CRZ/shear layer. The wing shift with T_fuel sets the evaporation-delay trend.
3. **LII + spray data**: soot in the pilot flow and CRZ, Jet A >> HEFA, gives a fuel-dependent radiative-loss prior on PSR_P/PSR_CRZ and evidence the pilot is locally rich at pilot-only (Murdock); the ~50 % droplet reduction at 338 K (Murdock, citing [37,38]) anchors x_l(T_fuel).

## 5. What the config scaffold gets wrong
- Linear chain only: no parallel pilot/main circuits, no recycle, so no recirculation zones.
- Inlet is pure air; no fuel, evaporation, or air split.
- gri30 (C1-C3): no kerosene surrogate, no meaningful UHC; HyChem A2 + NOx needed. UHC not tracked.
- No unmixedness: perfectly premixed PSRs underpredict NOx at phi 0.49 (the June diagnosis, D2b).
- Heat loss is negligible as written: 25 W/m2K x 0.08 m2 x ~600 K ~ 1.2 kW vs ~800 kW heat release (0.59 x 0.032 x 43 MJ/kg) [shown]; placeholder numbers.
- Dilution "mix_stream" 4-5 % is not tied to film-cooling hardware or to probe position.
- Combustor and sampling train in one chain; the probe interface (beta, local sample) is implicit.

## 6. Risks and how to state limits
- **Strain/local extinction** in the high-velocity main shear layers at 1 MPa: fixed-tau PSRs cannot represent extinction/re-ignition; CO error is absorbed into tau or UA [Medium].
- **Spray non-uniformity / flash boiling** (>~450 K): x_l and S may change step-wise; do not impose smooth trends across that boundary [Medium].
- **Single probe, asymmetric CRZ** (Murdock Sec. 2): beta absorbs point-vs-mean mismatch [High].
- Paper wording: "The CRN is an interpretive model with effective parameters, constrained by hardware and PIV/OH*; inferred chamber NOx is robust within the stated bounds; inferred CO and UHC are conditional on the quench representation and are reported as bounds, not predictions."
