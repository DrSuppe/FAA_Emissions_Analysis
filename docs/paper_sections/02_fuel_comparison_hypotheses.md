# Fuel comparison: expected trends and the levers behind them (architect, from the 2026-10-13 discussion)

Fuel properties act on emissions through four levers. Every fuel-to-fuel difference should be attributable to one.
1. **Spray and vaporization** (volatility, viscosity, surface tension, density): droplet size, liquid penetration,
   vaporization time; sets how premixed the flame is. Jet A slowest; HEFA faster (5x lower viscosity at 240 K,
   Murdock Table 1); GS190 narrow light cut, fastest. [High for Jet A vs HEFA, Medium for GS190]
2. **Stoichiometry and H/C**: at fixed phi, paraffinic fuels give ~2-3 % less CO2, more H2O, adiabatic flame
   temperature within tens of K. Small but exactly computable, so it can be corrected for. [High]
3. **Fuel-class kinetics**: aromatics oxidize more slowly than paraffins; paraffins have higher flame speed by a
   few percent. Matters for CO/UHC burnout at short residence and for prompt NO. [Medium]
4. **Soot radiation**: aromatics -> soot -> radiative loss -> lower local T. Small correction at lean swirl-flame soot
   levels. [Medium]

Predictions: NOx: paraffinic fuels at or a few percent below Jet A at pilot-and-main (levers 1 and 4 oppose 2),
inside scatter; a clearer effect possible at pilot-only where lever 1 dominates, sign undetermined. CO/UHC: small at
pilot-and-main; at pilot-only Jet A > HEFA >= GS190 (lever 1, amplified for UHC by Jet A's heavy tail). CO2/H2O:
pure lever 2, gives H/C and a carbon-balance check. NO2/NOx: mostly sampling, fuel-independent to first order.

Signatures to separate the levers: (1) fuel differences collapse against reduced temperature T_fuel/T_boil ->
vaporization; (3) residual Jet A difference at the highest T_fuel -> aromatic kinetics; (2) NOx aligns with
computed adiabatic flame temperature -> stoichiometry; (4) NOx tracks LII soot intensity inversely at pilot-only
-> radiation (Murdock GT2026 is the external handle).
