# Quorum 02: combustion chemist (NOx pathways, burnout, sampling chemistry)

Read: main.tex, hypotheses note, D4, Murdock Table 1. The June spec path does not exist, so no Cantera numbers are used. Nothing here was computed.

## 1. Five hypotheses

**H1. Flame-formed NO2 tracks the cold-pocket/HO2 route, not the line.** Signature: NO2/NOx rises as phi falls and with CO or UHC (pilot-only > pilot-and-main), and is similar across fuels at equal CO/UHC. A line artefact would be set by line temperature and residence time and be indifferent to phi. Chemistry: NO + HO2 -> NO2 + OH proceeds where NO meets HO2-rich, cool gas (quenched wall/dilution/pilot-main shear regions), and NO2 survives if it does not meet O/H atoms to revert. [Medium: textbook mechanism, magnitude unknown for this rig.]

**H2. NOx versus phi is Zeldovich-limited above a floor.** Signature: ln EI_NOx linear in 1/T_ad over phi 0.36-0.61, slope near the Zeldovich activation temperature (~38,000 K, the O + N2 step, [High recall]); flattening at low phi marks N2O/NNH/prompt. Chemistry: at 1 MPa and 760 K inlet the leanest points are near the crossover where non-thermal routes are a comparable share. [Medium: crossover location unverified.]

**H3. Fuel temperature acts through vaporization/premixing, with a threshold near T_boil.** Signature: NOx, CO, UHC versus T_fuel/T_boil show a knee around 470-490 K (Table 1 boiling points) at pilot-only, much weaker at pilot-and-main. Chemistry: flashing fuel shrinks droplets and lowers peak local phi, cutting thermal NO; the enthalpy effect of preheat itself is small (my estimate ~20 K in T_ad for 300 K preheat at phi 0.49, from fuel cp times mass ratio; [Medium]). [Medium-High]

**H4. UHC/CO ratio separates spray-limited from kinetics-limited burnout.** Signature: at pilot-only, UHC/CO high and fuel-ordered (Jet A heaviest) means incomplete vaporization/mixing; low ratio with CO rising at low phi means CO freeze-out by quench. Chemistry: CO oxidation via CO + OH needs OH, which collapses below roughly 1500-1600 K [Medium]; UHC lumped FTIR also undercounts heavy ends lost to wall condensation. [Medium]

**H5. H2O/CO2 and the carbon balance give a fuel H/C check and probe-representativeness test.** Signature: H2O/CO2 higher for HEFA/GS190 by an exactly computable amount; metered vs carbon-balance phi disagreement flags spray-core sampling bias. Chemistry: pure stoichiometry. [High] Water caveat: FTIR H2O in a heated line is only valid if no condensation occurs.

## 2. NOx pathways

Likely at 1 MPa, T_ad of order 1900-2000 K at phi 0.49 [Medium, not computed]: thermal dominates pilot-and-main; N2O route and NNH grow in relative share at the lean/low-T pilot-only and low-phi ends; prompt is minor lean at high pressure but not zero; fuel-N is absent. Emissions-only data plus a CRN cannot separate them uniquely: NO is a single number and residence time, local phi distribution and heat loss are fitted parameters that trade off against pathway shares. What the data can do is test slope and curvature of NOx vs T_ad (H2), and the model can report pathway fractions only as conditional on calibrated zones. Honest claim: "consistent with thermal-dominated formation with a non-thermal floor". Pathway attribution needs rate-of-production analysis flagged as model-dependent, or N2O measurement (FTIR can see N2O; check if retrieved).

## 3. Sample-line NO2 (orders of magnitude, [Medium] unless noted)

Homogeneous NO + O2 (termolecular) at tens-to-hundreds ppm NO and sub-second to few-second residence is negligible at atmospheric line pressure [High: second-order in NO, hours timescale]. The line-relevant homogeneous route is HO2/OH-mediated conversion in the hot probe quench zone, only while radicals persist; at 1 MPa probe pressure this is the one place it could matter. My prior: the majority of measured NO2 is flame/post-flame formed, homogeneous probe conversion is a minor-to-moderate fraction, wall effects (NO2 loss on steel/PTFE, possible surface reduction) bias NO2 low and are unquantified. Do not put a number on it without the check. Settling checks: (a) spike NO and NO2 test gas through the full line at operating temperature and measure recovery; (b) vary line flow/venturi to change residence time at fixed condition (a line artefact scales with it); (c) model: HO2 and OH pool at the probe inlet, with and without radical quench. D4(a) is acceptable only if the paper states the sign of the wall bias.

## 4. Claims to avoid

- Pathway shares (thermal/N2O/NNH) as measured facts: unidentifiable from NO alone.
- A single "line fraction" of NO2 without recovery test: reviewer asks about wall loss.
- Fuel effects on NOx smaller than scatter, or any aromatic effect on NOx, without equal-T_ad comparison: confounded with stoichiometry and spray.
- UHC speciation or fuel-class kinetics from lumped FTIR UHC.
- In-chamber CO from freeze-modelled line: CO may be frozen at the probe, not in the combustor.

## 5. Disagreements with the hypotheses note

1. "Tad within tens of K, so small": thermal NO sensitivity is ~38,000/T_ad^2, about 1%/K near 1900 K [High, derived], so 20 K is ~20% in NOx. Stoichiometry correction is not negligible and must be done from the model before any fuel claim.
2. "NO2/NOx mostly sampling, fuel-independent": H1 predicts flame-formed, CO/UHC-correlated NO2, and fuel dependence through UHC/HO2.
3. Lever 4 (soot radiation) and the NOx-vs-LII link: lean soot is too small for a first-order radiative T effect [Medium], and the rig note's 80 K Tad shift concerns fuel temperature, not soot. Treat as a nulled lever, not a test.
4. "Paraffin flame speed higher by a few percent" is [Low-Medium, recall]; do not lean on it.
5. Pilot-and-main "levers oppose": the data likely cannot resolve it; say so.
