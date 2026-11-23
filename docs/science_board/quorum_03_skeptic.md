# Quorum 03: the skeptical reviewer

Sources: main.tex, hypotheses note, decisions.md, Murdock GT2026, matrix plot (axis in F).

## 1. Three likely objections

**O1. "Inferred in-chamber composition" is circular.** Zone residence times, air split and wall heat transfer are tuned until the model reproduces the FTIR output; the model then "predicts" that output. CO2, H2O and the carbon balance are fixed by phi, so the only free observables (NO, NO2, CO) are what the tuned parameters absorb. Per-case calibration absorbs fuel effects into tau. [High]
Answer: a model-independent test of the sample line (section 3, Fig. B); hold-out prediction; parameters shared across fuels (injector hardware does not know the fuel); profile-likelihood or bounds showing parameters are not pinned to their limits.

**O2. Fuel and fuel-temperature effects are confounded and unreplicated.** The plot shows GS190 pilot-and-main at phi ~0.52-0.53 versus HEFA ~0.48 at the same T_fuel, so phi offsets NOx. Two Jet A series (Jet A, "Colin Jet A") come from different campaigns, and no GS190 points appear at pilot-only. [Medium; read off a plot] Murdock Table 2 shows pilot-only T3 drifting 640 to 706 K with T_fuel for Jet A and ~630 K for HEFA; NOx is strongly T3-dependent. If the emissions runs inherit this, T_fuel is aliased with T3. [Medium]
Answer: replicates with error bars, a regression of EI on measured phi, T3, P3 and fuel T, and a stated minimum detectable effect so null results are meaningful.

**O3. Novelty beyond Murdock GT2026.** That paper already gives the injector, a near-identical matrix and flame structure versus T_fuel; emissions trends alone are "same rig, another instrument". [High]
Answer: tie emissions to optical data (Fig. C); the sampling-artifact quantification is the real novelty.

## 2. Claims ranked, safest to most exposed

1. Analyzer-level CO2/H2O/CO/NO vs phi at fixed T_fuel; carbon-balance closure. [High]
2. NOx and CO vs overall phi (large signal; sweeps at three T_fuel). [High]
3. T_fuel effect on NOx/CO/UHC: depends on effect size vs repeatability. [Medium]
4. Fuel-to-fuel differences (paraffinic vs Jet A). The hypotheses note itself predicts differences "inside scatter". [Low-Medium]
5. Aromatic-content effect on gaseous emissions, isolated from vaporization. Table 1 has only wt% aromatics and a 0.1 MPa boiling point; no composition (GCxGC) is available for GS190 (D7 open). [Low]
6. Inferred combustor-exit CO. The probe quench rate sets CO freeze, and the water-cooled probe wall is unmodelled. [Low]
7. Inferred combustor-exit NOx and "fraction of NO2 formed in the line". D4 admits wall reduction and PTFE uptake are omitted, the dominant artifacts per SAE ARP1256 as cited in main.tex. A homogeneous-only fraction is not the line fraction. Flame-side NO2 (real, in lean cool zones) is not separable from line NO2 by a model alone. Sensitivity bounds are parametric, not structural; they say nothing about missing physics. [Low]

Single probe position: only the D6 carbon-balance fuel-air check bounds representativeness. [Medium]

## 3. What makes it strong

**Fig. A, variance partition.** Regress EI(NOx, CO, UHC) on measured phi, computed T_ad and vaporization state across all fuels; show which lever (hypotheses note) explains each residual. Use boiling at injection pressure, not 0.1 MPa (Table 1 values are atmospheric; 579 K exceeds the 562/542 K final boiling points). [Medium]

**Fig. B, line-residence extrapolation (model-independent).** At one fixed combustor point, vary sample-line temperature, flow (venturi) or length, and plot NO2/NOx vs line residence time. The intercept at zero residence is the in-chamber NO2 fraction; the slope tests the model's gas-phase rate. Add a bench NO span-gas run through the train. This is the single most persuasive addition. [High]

**Fig. C, emissions vs optical.** Plot NOx/CO against OH* flame position or LII intensity at matched Murdock cases. Caveat: LII there is relative, not calibrated soot volume fraction (Murdock Sec. 1), so only rank or qualitative correlation is defensible. [Medium]

**Minimum validation for "inferred".** (i) Elemental balance closure; (ii) calibrate on CO2/CO/H2O and hold out NO/NO2, or calibrate on Jet A and predict HEFA/GS190 with shared parameters; (iii) Fig. B or span-gas test; (iv) more independent observables than tuned parameters, shown. Without (ii) and (iii), say "model-consistent" not "inferred". [High]

## 4. Journal conversion (JEGTP or Combustion and Flame)

- JEGTP: the above plus replicate statistics, composition-resolved fuel properties, and a general emissions-index correction recipe others can apply to extractive FTIR data. [Medium]
- Combustion and Flame needs mechanism: a second pressure or T3 (only two operating points exist), spatially resolved or multi-position sampling, structural model-form uncertainty (wall chemistry, mechanism choice, zoning alternatives D2), and a validated gas-phase NO-to-NO2 path rather than a tuned CRN. [Medium]

## 5. Disagreements with the hypotheses note

- "NO2/NOx: mostly sampling, fuel-independent to first order." Disagree: it prejudges the quantity the paper claims to infer, and line conversion depends on NO level, O2, T and residence time, so it is not fuel-independent. Flame-side NO2 is plausible at lean low power. [Medium]
- Lever tags [High] on 2-3 % CO2 and "within tens of K" T_ad carry no cited source or computation; mark [Medium] until computed. [High]
- Signature (1), collapse against T_fuel/T_boil, uses a boiling point at the wrong pressure and ignores that Jet A and HEFA differ by ~26 K in mean boiling point. Use injection-pressure saturation and spray data. [Medium]
- Signature (4), NOx inversely tracking LII: LII is relative only, and soot radiation is called "small", so the test is both weak and unfalsifiable at once. [Medium]
- Missing lever: injector-side effects of T_fuel (viscosity, flashing, pilot/main split drift) and T3/phi drift between cases. [Medium]
