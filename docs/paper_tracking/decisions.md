# Decisions (open and path-critical)

Maintained by the architect session. Rendered on the dashboard decisions tab. One block per decision: status
`open`, `proposed` (recommendation stated, user to confirm) or `decided` (date and outcome). Order: path-critical
first. Context: GT2027 abstract accepted (user, 2026-11-17); draft paper due 2026-12-21.

## D1 Model operating point: COMRAD, not the 1.85 bar lab rig of the June spec
status: proposed
owner: user
blocks: every model number in the paper (T7)
options: (a) pilot-and-main 1.0 MPa, T3 ~760 K, air 0.59 kg/s, phi 0.49, pilot fuel split ~30 %; pilot-only 0.53 MPa, phi 0.28 (Murdock GT2026 Table 2); the June design spec's 1.85 bar / 0.18 kg/s point is void. (b) keep the June point.
recommendation: (a); confirm the sampling-plane pressure the probe sees and whether the model runs per test case from the logged P3, T3, flows (preferred) or at nominal points.

## D2 Combustor zoning and air split
status: open
owner: user
blocks: T7
options: (a) pilot PSR (near-stoichiometric) + main PSR + mixing PFR to the exit, air split from injector effective areas; (b) single partially-premixed zone at overall phi (unphysical for NOx, the June diagnosis); (c) two-stream (pilot/main) with a stoichiometric interface as in the LNG topology B.
recommendation: (a) with the pilot/main air split from the injector's measured effective areas (hardware, not invented); needs the ACd or air-split numbers for the injector from the rig team.

## D3 Sampling-train geometry and temperatures
status: open
owner: user
blocks: T7, sample-line NO2 fraction claim
options: hardware numbers needed: probe internal passage (length, ID, wall/coolant temperature), heated line length/ID/setpoint, PTFE section, venturi, sample flow rate, FTIR cell T and p.
recommendation: a one-page `coordination/notes/sampling_train.md` filled by the user from drawings; the model config is generated from it.

## D4 Sample-line NO2: homogeneous chemistry only, limitation stated
status: proposed
owner: user
blocks: results wording
options: (a) gas-phase mechanism only; the paper states that wall-catalysed NO2 reduction on the metal probe and NO2 uptake in PTFE (SAE ARP1256) are not modelled, so the reported sample-line NO2 fraction is the homogeneous part; (b) add a wall/surface sub-model (not in scope by December).
recommendation: (a).

## D5 Uncertainty bounds in Paper 1: sensitivity-based, not Bayesian
status: proposed
owner: user
blocks: results figures
options: (a) Morris screening to rank parameters, then bounds from one-at-a-time sweeps of the top parameters over their plausible ranges; (b) full NUTS posteriors (Paper 2).
recommendation: (a), matching the abstract ("uncertainty bounds obtained from a sensitivity analysis").

## D6 Emission-index basis
status: proposed
owner: user
blocks: data reduction spec
options: (a) EI from the carbon balance of the sampled gas (SAE ARP1533 convention, dilution-invariant), metered flows as model inputs, metered/carbon-balance fuel-air ratio reported per case as a probe-representativeness check; (b) EI from metered fuel and air.
recommendation: (a), same ruling as the LNG project (EI-D1).

## D7 GS190 fuel properties
status: open
owner: user
blocks: H/C, stoichiometric air, surrogate choice for the GTL fuel
options: Shell GTL solvent GS190 datasheet (density, distillation, aromatics, H/C) and the lot certificates for Jet A and HEFA; mechanism surrogate: HyChem A2 for Jet A; for HEFA and GS190 a paraffinic surrogate (HyChem C1 or n-dodecane) to be decided once properties are in hand.
recommendation: user supplies the datasheets; architect proposes the surrogates in a note.

## D8 GT2027 paper number, author list, affiliations
status: open
owner: user
blocks: header of main.tex, dashboard header
options: user fills `\author{}` in Overleaf and posts the GT number here.
recommendation: none needed.

## D9 Reactor-network topology for the paper (Stage A)
status: proposed
owner: user
blocks: T9 model rebuild
options: (a) pilot zone as a 3-bin equivalence-ratio bank of PSRs + main PSR + merged inner/central recirculation PSR with recycle + mixer + burnout PFR + film-air PFR, then the sampling-train chain: 7 combustor reactors, 4 global free parameters (pilot unmixedness S0, S1 linear in fuel temperature; heat-loss scale q; film mixing rate k_f); residence times and recycle from geometry and PIV; film share beta from the carbon balance. (b) same without the pilot bank: 5 reactors, 3 free, likely repeats the June NOx underprediction. (c) the fuller Stage B network now: 11 reactors, 6 free, underdetermined by emissions.
recommendation: (a) [Medium]; see docs/paper_sections/04_crn_swirl_injector_proposal.md sections 2-3.

## D10 Calibration design: global parameters, held-out cases
status: proposed
owner: user
blocks: results section, abstract wording
options: (a) calibrate the 4 global parameters on Jet A pilot-and-main at 366 and 589 K only; predict 478 K, HEFA, GS190 and pilot-only without refitting; (b) calibrate on everything and hold out NO only; (c) per-case fits (not identifiable: ~4 informative observables vs 6 unknowns per case).
recommendation: (a). Consequence: the paper says residence times and air split are fixed from hardware and PIV, and only effective mixing and heat-loss parameters are calibrated; the abstract's "calibrated so that the model reproduces the FTIR measurements" is reworded accordingly in the draft.

## D11 Model-independent sample-line test and the word "inferred"
status: proposed
owner: user
blocks: the sample-line NO2 claim (most exposed claim per the skeptic)
options: (a) run one fixed operating point with sample-line temperature or venturi flow varied, plus NO and NO2 span gas through the full train; read the NO2/NOx intercept at zero line residence time; keep "inferred in-chamber composition"; (b) no test; the paper says "model-consistent" in-chamber composition and reports bounds.
recommendation: (a) if rig time exists before camera-ready (March 22); use (b) wording in the December draft regardless [High].

## D12 Provenance and authorship relative to McDonald 2021 / ASCENT reports
status: open
owner: user
blocks: novelty statement in the Introduction
options: the library found McDonald, AIAA 2021-3480 (NOx, CO, UHC for heated Jet A on this injector at 1-2 MPa) and ASCENT Project 67 reports with a planned journal paper. Are the Jet A and GS190 emissions from that campaign? Is the planned journal paper still planned, and how is authorship split?
recommendation: answer before the Introduction is drafted; the paper cites McDonald 2021 and differentiates on fuels, pilot-only, phi sweeps, speciated NO2/H2O and the sampling-train model.
