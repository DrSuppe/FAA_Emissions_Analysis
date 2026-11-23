# Science insights synthesis for the GT2027 emissions paper

Merges quorum_01 (experimentalist, Q1), quorum_02 (chemist, Q2), quorum_03 (skeptic, Q3), `02_fuel_comparison_hypotheses.md` (note) and `docs/literature/comrad_library.md` (lib). File 04 was absent on 2026-11-23, so it is not covered. Nothing here was computed.

## 1. Novelty position

**Already published or announced:**
- **Heated Jet A changes NOx/CO/UHC at 1 MPa.** mcdonald2021aiaa reports NOx, CO and UHC at Tfuel 373, 473 and 568 K, phi 0.33-0.51, plus OH* [Verified: DOI, search result; full text not read]. "Emissions vs Tfuel for Jet A" is therefore not new [High].
- **NO roughly doubles from 366 to 589 K** (ascent2025). These are exactly this paper's sweep temperatures, which suggests a shared campaign [Medium].
- **Jet A and GS190 emissions vs Tfuel at 1-2 MPa** are listed in ascent2025slides. mcdonald2025jegtp is "to be submitted"; if it is published first, plain Jet A/GS190 trend claims are pre-empted [High risk].

**New** (per the lib §3 gaps) [Medium-High; the literature search could not reach most AIAA and ASME pages, which returned 403 errors]:
1. HEFA emissions.
2. Pilot-only emissions.
3. Speciated NO/NO2/H2O/CO2 with a described sampling train.
4. Emissions at Murdock's LII/OH* conditions.
5. phi up to 0.61 at three Tfuel.

**Must cite and differ from:** mcdonald2021aiaa, ascent2025, murdock2026jegtp, philo2023fuel, hodge2025jpp.

## 2. Ranked insight candidates

Format: hypothesis; confirm/refute signature; needs; voices.

- **I1 Vaporization transition in emissions and structure.** At pilot+main phi 0.49, knees in EI_CO/UHC/NOx vs Tfuel coincide with Murdock's transitions (LII peak J-3, re-rise J-12/13, OH* wings downstream/inward); a smooth trend while structure jumps refutes. Needs LII/OH* J-1..13 and HEFA set. Q1 H1/H3, Q2 H3; Q3: may sit inside scatter.
- **I2 Pilot-only burnout and soot oxidation are both OH-limited in the CRZ.** CO/UHC fall with Tfuel for Jet A together with LII, not for HEFA; high, fuel-ordered UHC/CO = spray-limited. Needs LII/OH* J-P1..5, H-P1..5. Q1 H2, Q2 H4; Q3: T3 drift.
- **I3 Aromatics control soot, not gases.** After partitioning phi, model T_ad and vaporization state (Q3 Fig. A), the Jet A-paraffin residual is within a stated minimum detectable effect (MDE); HEFA vs GS190 isolates volatility. Emissions + model. Q1 H4, note; Q2: 20 K T_ad = ~20% NOx, so correction is mandatory.
- **I4 NOx vs phi is Zeldovich-limited above a non-thermal floor.** ln EI_NOx linear in 1/T_ad, slope ~38,000 K, flattening lean. Emissions + T_ad. Q2 H2, Q3; Q2 forbids pathway shares as measured.
- **I5 Lean CO/UHC rise moves to lower phi with heating.** Emissions only (no optics below phi 0.49). Q1 H5, Q2 H4.
- **I6 Measured NO2/NOx is partly flame-formed.** Rises with falling phi and with CO at fixed line conditions; line-residence extrapolation gives the in-chamber intercept. Needs Q3 Fig. B test + train model. Q2 H1, Q3; note and Q1: mostly sampling.
- **I7 H2O/CO2 and carbon balance give an H/C check and probe representativeness.** Emissions only; foundation. Q2 H5, Q3.
- **I8 NOx tracks OH* flame position (premixedness), not T_ad.** Q1 H3; Q1 rates it Low (sign open).

| Rank | Insight | Value | Risk | Risk reason |
|---|---|---|---|---|
| 1 | I1 | High | Medium | Trend partly published; the knee may sit inside the scatter |
| 2 | I3 | High | Medium | GS190 phi offset; a null result needs an MDE |
| 3 | I2 | High | High | T3 aliased with Tfuel; no GS190 at pilot-only |
| 4 | I4 | Medium | Low | Large signal; T_ad must be computed |
| 5 | I7 | Medium | Low | Needs H2O measured without condensation |
| 6 | I5 | Medium | Medium | Needs dense phi sampling |
| 7 | I6 | High | High | No line test known; wall loss not modelled (D4) |
| 8 | I8 | Medium | High | Sign undetermined; OH* is relative only |

I7 and I4 are the paper's foundation; spend most of the analysis effort on I1 and I3. If Question 2 is answered yes, I6 jumps to rank 1 [Medium].

## 3. Gaps the dataset fills
HEFA emissions and pilot-only emissions: none exist on this injector (lib §3 b3). NO2, CO2, H2O: never reported; ascent2025 gives NO only (§3 b1, b5). Gaseous emissions at the Murdock cases (1.01 MPa, 759 K, phi 0.49): none (§3 b10). Sampling-line treatment: unpublished (§3 b8). phi > 0.51 at controlled Tfuel: none (row mcdonald2021aiaa).

## 4. Disagreements and rulings

- **NO2/NOx as observable** (note, Q1: "mostly sampling"; Q2, Q3: no). Ruling: Q2/Q3 are right; the note prejudges the inferred quantity. Report analyzer NO2/NOx and its phi/CO correlation at fixed line conditions as *suggestive* of flame formation; no "line fraction" without the residence or span-gas test, since a homogeneous-only fraction is not the line fraction (Q2 §3, Q3 rank 7) [High].
- **Skeptic vs note:** boiling point at 0.1 MPa, accepted (use injection-pressure saturation plus 20-30 K manifold heat-up, Q1). NOx-vs-LII radiation test, dropped (LII relative; lean soot too small, Q2); LII only for rank correlation with CO/UHC. Uncited [High] tags on CO2/T_ad offsets, accepted: [Medium] until computed.
- **Fuel-temperature mechanism.** Q1 and Q2 agree on vaporization/premixing over enthalpy (~20 K T_ad, Q2). Q2 expects the knee mainly at pilot-only with premixing *cutting* NO; Q1 ties pilot+main knees to structure, sign open. Ruling: ascent2025's NO *doubling* is too large for enthalpy (~20%) and opposite to Q2's sign, so I1/I8 must explain an increase: wing shift downstream/inward, unburnt-fuel accumulation at low Tfuel (hodge2025jpp), or a probe artifact [Medium].
- **Q3 O1, circularity:** accepted. Shared combustor parameters across fuels, calibrate on CO2/H2O/CO, hold out NO/NO2, show parameters off bounds; until hold-out and line tests pass, say "model-consistent", not "inferred" [High]. **O3, novelty:** accepted and widened; McDonald, not Murdock, is the main threat.

## 5. Confounds and fixes

1. **phi mismatch** (GS190 about 0.52-0.53 vs HEFA about 0.48, read off the plot by Q3): regress EI on measured phi, or interpolate the sweeps; compare fuels only at matched T_ad.
2. **T3 drift at pilot-only** (630-706 K, Murdock Table 2): include the logged T3 as a regressor and subtract dEI/dT3 taken from the CRN. If that fails, use T3-matched pairs only, or label I2 as confounded.
3. **Replicates and campaigns** (two Jet A series): compute repeatability from repeat points, test the offset between campaigns, and state an MDE per species.
4. **Boiling point:** 579 K exceeds the final boiling points measured at 0.1 MPa. Use saturation curves at 1.0 and 0.53 MPa from distillation data, with the heat-up as an uncertainty band.
5. **Probe representativeness:** check metered phi against phi from the carbon balance for every case (I7).

## 6. Three carrying figures

- **Fig. 1 (tests I1, I8, I3; Q1 §3).** Shared x = Tfuel 290-590 K, pilot+main phi 0.49. Rows: (a) EI_CO, EI_UHC, log y; (b) EI_NOx; (c) LII over pilot ROI normalized to the coldest case; (d) OH* main-wing axial centroid. Series Jet A, HEFA (GS190 in a-b). Shaded injection-pressure saturation bands. Pilot-only twin adds T3 as row (e) and tests I2.
- **Fig. 2 (tests I4, I3).** (a) ln EI_NOx vs 1/T_ad (model) over all phi sweeps; marker = fuel, color = Tfuel 366/478/589 K; Zeldovich reference slope. (b) residual EI after variance partition by fuel, with MDE bars. Inset: EI_CO vs phi with onset marked (I5).
- **Fig. 3 (tests I6, O1).** NO2/NOx vs line residence time at one combustor point, with span-gas recovery and model curves with and without radical carry-over (needs question 2). Fallback: measured vs model parity for *held-out* NO, NO2 and fuels.

## 7. Questions for the user

1. **Provenance (the most important question).** Are the Jet A and GS190 data from the same campaign as mcdonald2021aiaa, ascent2025 and the planned mcdonald2025jegtp, and how is authorship coordinated? The answer sets the novelty statement and avoids double publication.
2. **Line test.** Can one condition be run with line temperature or venturi flow varied, plus NO/NO2 span gas sent through the full train? This would move I6 from High to Low risk and settle O1.
3. **Matching to the optical cases.** Were the emissions recorded in the same runs as Murdock's J-1..13 and P1..5? Is there access to per-case LII/OH* centroids, the unpublished OH-PLIF and the 10 kHz PIV/Mie vs Tfuel (ascent2025slides)? This would move I1 and I2 from Medium to High confidence.
4. **Replicates.** How many repeat points are there per condition and fuel, and do the two Jet A series overlap? This sets the MDE for I3.
5. **Pilot-only T3 and GS190.** Is T3 logged per case, and are there any GS190 pilot-only runs? I2 depends on it.
6. **FTIR species.** Were N2O and individual hydrocarbons retrieved? N2O would test the non-thermal floor in I4 directly (Q2 §2).
7. **GS190 composition and distillation curves (D7).** These are needed for the I3 volatility split and the saturation correction.
