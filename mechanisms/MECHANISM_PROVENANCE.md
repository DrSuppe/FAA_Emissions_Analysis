# Mechanism provenance — FAA Jet-A + NOx

## In use: `A2NOx_skeletal.yaml`  (HyChem A2 / Jet-A POSF10325 + NOx, skeletal)

- **What it is:** Stanford HyChem physics-based real-fuel model for Jet-A (POSF10325),
  combined with Glarborg N-chemistry, skeletally reduced by T. Lu (UConn).
- **Size (verified by import in Cantera 3.2.0):** 71 species, 538 reactions.
- **Fuel representation:** a single *lumped* pseudo-species `POSF10325` that undergoes a
  7-step HyChem pyrolysis into small fragments (C2H4, H2, CH4, C3H6, iC4H8, C4H81,
  benzene, toluene, CH3, H), which are then oxidized by USC-Mech IIa.
  This is the HyChem functional-group approach — **not** a discrete n-dodecane surrogate.
- **NOx pathways present:** thermal + prompt + N2O + fuel-N. N-species in the file:
  NO, NO2, N2O, HCN, NH3, HNO, N, NH, NH2, N2. (NNH is absent in the skeletal version.)
- **Validity range:** intended for high-temperature flame/combustor conditions
  (our products are ~1000–2200 K — in range). It has **no resolved low-temperature /
  cool-flame / autoignition chemistry**, so do not use it for cold-staging or ignition-delay work.
- **Verified:** imports cleanly in Cantera 3.2.0; `equilibrate('HP')` gives T_ad ≈ 2406 K;
  runs as an `IdealGasReactor` PSR at 2.5 bar producing steady-state NO/NO2.

### Source & conversion
- Download (Chemkin): `https://web.stanford.edu/group/haiwanglab/HyChem/download/A2NOx_skeletal.txt`
  plus thermo `https://web.stanford.edu/group/haiwanglab/HyChem/download/therm.txt`.
- Converted with: `python3 -m cantera.ck2yaml --permissive --input A2NOx_skeletal.txt --thermo therm.txt`
  (`--permissive` only needed to skip a stray `ENDOFDATA` token in the thermo file; validation then PASSED).
- Transport intentionally omitted: not needed for 0-D PSR/ideal-gas reactor networks, and the
  HyChem `tran.txt` uses a non-standard 5-parameter fit for the `POSF10325` pseudo-species that
  ck2yaml rejects.

### Citation (required)
- C. Saggese, K. Wan, R. Xu, Y. Tao, C.T. Bowman, J. Park, T. Lu, H. Wang,
  "A physics-based approach to modeling real-fuel combustion chemistry – V. NOx formation from a
  typical Jet A," *Combustion and Flame* 212 (2020) 270–278.
- NOx base chemistry: P. Glarborg, J.A. Miller, B. Ruscic, S.J. Klippenstein,
  "Modeling nitrogen chemistry in combustion," *Prog. Energy Combust. Sci.* 67 (2018) 31–68.
- License/availability: free for academic use from the Stanford HyChem site
  ("Copyright © 2020 HyChem"); citation required, no explicit OSI license.

## Verified fallbacks (NOT committed — re-downloadable from the URLs below)
- **Detailed HyChem A2 NOx** — 201 species, 1589 reactions (adds NNH pathway). Accuracy reference.
  `https://web.stanford.edu/group/haiwanglab/HyChem/download/A2NOx.txt` + `therm.txt`.
- **CRECK (POLIMI) n-dodecane/diesel TOT HT+LT + Soot-NOx** — 537 species, 18250 reactions.
  The only verified option with a *discrete* multi-component surrogate (NC12H26, IC8H18, C7H8…)
  + NOx + low-T chemistry; heavy/slow. Ranzi, Frassoldati et al. (CRECK Modeling Group).
  `https://raw.githubusercontent.com/CRECKMODELING/Kinetic-Mechanisms/master/Gas-Phase/Diesel-Biodiesel/Soot-NOx/TOT_HT_LT_NOX_537_18250/kinetics.CHEMKIN.CKI` + `thermo.CHEMKIN.CKT`.

## Rejected (do not use)
- CERFACS n-dodecane "27sp + Luche NOx": distributed Cantera artifact is legacy CTML with **no NOx
  species** and reactions hidden in an AVBP `.f90` subroutine — not importable in Cantera 3.2.
- HyChem `A2NOx_reduced.txt` (advertised 51-species reduced): the file at the official URL is a
  header-only stub with an **empty REACTIONS block** — not usable as downloaded.
