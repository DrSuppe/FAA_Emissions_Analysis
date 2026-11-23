# Quorum 01: experimental diagnostician

Sources read: `docs/paper_ideal/main.tex` (abstract, Test Matrix), `docs/paper_sections/02_fuel_comparison_hypotheses.md`, `docs/paper_tracking/decisions.md` (D1, D7), `references/2026_TurboExpo_Murdock_LII.txt` (Tables 1-2, Sec. 3.1-3.2, Sec. 4), the 2026-10-11 test matrix PNG (x-axis is T_fuel in deg F).

Gap flagged: "insight" is undefined. I take it as "a claim a Turbo Expo reviewer would not already assume". Also: Murdock Table 2 has LII/OH* only at phi ~0.49 (pilot-and-main) and ~0.28 (pilot-only), for Jet A and HEFA only. No GS190, no phi sweeps. That limits every cross-diagnostic claim below.

## 1. Five hypotheses

**H1. Fuel heating changes emissions through a vaporization transition, not a smooth trend.**
Interest: heated fuel is a thermal-management lever, and the question is whether it is monotonic.
Confirm: EI_CO/UHC (and NOx) vs T_fuel show a knee or sign change near the mean/final boiling points (Jet A 493.1/561.8 K, HEFA 467.5/541.5 K, Murdock Table 1). Refute: smooth monotonic trend with no fuel-specific break.
Needs: Jet A pilot-and-main LII J-1..J-13 (Murdock Fig. 4-5: signal peaks at J-3, 338 K, falls J-4/5, rises again at J-12/13), plus OH* chemiluminescence and the Philo PIV/OH* work cited there (main-flame wings move downstream and inward with heating).
[Medium] Murdock shows structural transitions at specific T_fuel; whether they reach the exhaust gas is unknown.

**H2. At pilot-only, CO/UHC burnout and soot oxidation share one controlling process (OH-limited burnout in the recirculation zone).**
Interest: pilot-only is the taxi/approach condition, where CO/UHC are regulatory drivers.
Confirm: where Murdock sees faster downstream soot consumption with heating (J-P5, aromatic fuel only), CO/UHC also fall for Jet A but not (or less) for HEFA. Refute: CO/UHC trend identical for both fuels.
Needs: LII J-P1..J-P5 and H-P1..H-P5, pilot-only OH* (Fig. 2b), PIV of the CRZ.
[Low] Table 2 shows T3 drifting 629-706 K across pilot-only cases, which confounds T_fuel. It must be modelled or regressed out first.

**H3. At fixed phi, NOx responds to fuel temperature through premixedness (where the flame sits), not flame temperature.**
Interest: sensible-enthalpy gain is small, so any NOx change signals a mixing effect, which is a design-relevant mechanism.
Confirm: NOx tracks OH* flame-brush location or spread (main-wing shift) across J-1..J-13. Refute: NOx flat while the structure moves, or NOx moves with computed adiabatic T only.
Needs: Jet A and HEFA pilot-and-main OH* images (phi 0.49), PIV of main/IRZ flow.
[Low] Sign undetermined and the effect may sit inside run-to-run scatter.

**H4. Aromatic content, which controls soot by an order of magnitude, barely touches gaseous emissions once stoichiometry is corrected.**
Interest: it separates soot-relevant from gas-relevant fuel specification, which matters for SAF certification.
Confirm: Jet A vs HEFA CO/UHC/NOx differences are explained by H/C and volatility; HEFA vs GS190 (both aromatic-free, different distillation, per D7 once datasheets exist) isolates volatility from aromatics. Refute: a residual Jet A offset at high T_fuel where volatility differences vanish.
Needs: LII Jet A vs HEFA (pilot-and-main: aromatics vital; pilot-only: about 3.5x signal, Murdock abstract). GS190 has no LII.
[Medium] The three-fuel design is a strong lever, and the null result is publishable if uncertainty is stated.

**H5. Heated fuel moves the lean-side CO/UHC rise to lower phi.**
Interest: it defines the usable phi window, which is a stability-versus-emissions result.
Confirm: at 366/478/589 K the CO/UHC upturn onset shifts to lower phi with T_fuel. Refute: same onset at all three.
Needs: OH* and PIV at phi below 0.49. None exist in Table 2, so this needs new runs or is emissions-only.
[Low] Plausible, but the structural data does not exist at those conditions.

## 2. What emissions cannot tell us

1. **Where species form.** Extractive exit sampling gives one mixed value, so pilot-versus-main contribution, CRZ versus wall burnout, and local hot or rich pockets are unrecoverable. Only PIV/PLIF/OH* with a model can attribute.
2. **Soot and PAH precursors, and in-chamber NO2/CO versus analyzer values.** FTIR UHC is lumped, so no speciation or soot yield. Sample-line chemistry (main.tex abstract) is separable only through the CRN, not measurable by FTIR.

## 3. Missing figure

Pilot-and-main, phi ~0.49, shared x = T_fuel [K], 290-590 K, Jet A and HEFA, with GS190 where measured. Rows:
(a) EI_CO and EI_UHC (log y).
(b) EI_NOx.
(c) LII mean signal integrated over the pilot-flow ROI, normalised to the coldest case.
(d) OH* axial centroid of the main-flame wings.
Vertical lines mark each fuel's mean and final boiling point (Murdock Table 1). A shared x-axis lets a reader see whether a knee in (a)-(b) lines up with a structural transition in (c)-(d). A pilot-only twin figure follows, with T3 shown as an extra row (see H2).

## 4. Disagreements with 02_fuel_comparison_hypotheses.md

- **NOx vs LII soot as a radiation test (lever 4):** weak. Murdock states LII is used for relative structure and trends, not calibrated soot volume fraction (Sec. 2.2). Pilot-only T3 also varies. An inverse correlation would not isolate radiation.
- **Collapse against T_fuel/T_boil:** the note uses one boiling point. Table 1 is at 0.1 MPa, while injection is into 1.0 or 0.53 MPa. Murdock also reports a 20-30 K manifold heat-up between measurement and injector (Sec. 3.1). The reduced temperature carries an uncertainty comparable to the fuel differences, so the collapse test needs distillation curves and an error bar.
- **Lever 4 "small" at lean swirl-flame soot:** Murdock says the pilot runs locally rich above critical sooting limits (Sec. 3.2). Radiation may be locally non-negligible, though still not testable here.
- **Agreement:** NO2/NOx as mostly sampling-driven; H/C correction as computable.
