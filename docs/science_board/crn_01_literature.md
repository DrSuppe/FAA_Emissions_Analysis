# CRN 01: literature voice (reactor-network topologies for the piloted swirl injector)

Sources: only the LNG-project reference files (LNG/references/*, LNG/docs/specs/topology.md), our decisions.md (D2, D3, D5), Murdock GT2026 Sec. 1-2. Tags: [Verified] = the file marks it read; otherwise [High/Medium/Low] reasoned; [unverified recall] = not in the files. Most primary papers were not read by the sibling project either (only Innocenti 2018, Bedick 2025, John 2026 preprint, Novosselov thesis were read).

## 1. Topologies that apply, and those that do not

Apply (swirl, spray, partially premixed):
- **Novosselov et al., ASME GT2006-90282, 10.1115/gt2006-90282** (JEGTP 130, 2008, 10.1115/1.2795787): pilot flame, main flame, centre and dome recirculation, burnout; 5 regions refined to 31 PSR/PFR/MIX. The only published zoning with a separate pilot and recirculation reactors. Hand-built from CFD. [Verified, thesis/table read]
- **Innocenti et al., Fuel 215:853 (2018), 10.1016/j.fuel.2017.11.097**: few-tens-reactor CRN of a lean-burn spray Jet A-1 swirl combustor at 5-22 bar, fuel placed per CFD evaporation, turbulent-diffusion exchange "mandatory" for the corner recirculation. Closest in fuel, pressure and swirl. [Verified]
- **John et al. (2026), arXiv:2510.13033; Combust. Flame 2026, 10.1016/j.combustflame.2026.115199** (DOI from bibliography A20): evaporator then mixer element ahead of PSR/PFR for Jet-A swirl can; NOx within 10% of CFD, not of measurements. [Verified preprint; journal text unread]
- **Bedick & Boyette, JEGTP 148 (2026), 10.1115/1.4069551**: finite-rate mixing (PaSR) and heat loss explain ideal-CRN bias. [Verified abstract]
- **Fichet et al., Fuel 89:2202 (2010), 10.1016/j.fuel.2010.02.010**: flame/recirculation/post-flame/dilution zoning. [High]
- **Gkantonas et al., ISRN, 10.1115/1.4048408**: micro-mixing per reactor; needs CFD mixing field, soot not CO. [Verified formulation]

Transfer poorly (diffusion/RQL/can): Zakharov/Lebedev flamelet reactor (10.1007/s10573-009-0017-5), Monaghan and KPP (hundreds to 1114 reactors of a lab diffusion flame), Bedick's ammonia RQL (topology fuel-agnostic, but staged air does not exist here), Rizk-Mongia and Mellor characteristic-time correlations (conventional can), Perpignan flameless AGNES.

## 2. Design rules

- **Pilot:** a separately fed, small, stability-holding PSR (Novosselov: pilot as its own PSR plus PFR). No source gives a pilot volume rule [gap]. Pilot-only operation (phi 0.28) tests it in isolation.
- **Main partially premixed zone:** PSR on the mean phi, or N parallel phi-bins (Nicol/Tonouchi 5 bins, Gaussian [Low]; 300 reactors in Frassoldati via Perpignan [Medium]). No convergence rule beyond "increase N until emissions stop changing" [gap].
- **Recirculation as recycle:** treat IRZ and CRZ as well-stirred volumes exchanging mass with the through-flow (Swithenbank [Low content]); entrained mass from CFD (zero-axial-velocity surface, Novosselov Eq. 6-2) or a tuned exchange (Innocenti, case-by-case). No published a-priori recycle fraction [gap]. Measured PIV/OH* structure (Philo, in Murdock Fig. 2) can bound it qualitatively only.
- **Spray evaporation delay:** evaporator then mixer element for the liquid branch only (John; Mellor "evaporation first, then mixing, then kinetics" [Medium]). SMD and evaporation correlations exist in the bibliography (Rizk-Lefebvre 10.1115/1.3239617, Chin-Lefebvre 10.2514/3.8264, Burger 10.1016/s0017-9310(03)00286-2) but are unread. The 291-579 K fuel-temperature sweep is a natural lever on this element [High, reasoning].
- **Film cooling air:** boundary-layer stream joining late, not into the primary (Lefebvre via R-10 [Low]; no published CRN quantifies it [gap]). Murdock Fig. 1 shows film air along the liner.
- **Reactor count vs emissions:** Khodayari review: counts span 5 to 10^6, "at least 5000" for CO in one study [Verified-summary]; Grimm 2022: no CO gain from more reactors [Verified]. For emissions-only data, keep N at the minimum that changes the answer.

## 3. LNG topology: carries over / does not

Carries over: PSR then PFR burnout with distributed or staged air as a PFR rather than a one-step PSR dilution (the CO-overshoot lesson, CO 4-9x high); parallel-PSR phi distribution as an unmixedness handle; the evaporation-element hook (spec Sec. 8, fuel streams kept separable); wall heat loss as a prescribed fraction; the flag-and-report discipline.
Does not: the stoichiometric-interface PSR (built for rich primary air-starved RQL; here the main is lean, phi 0.49 overall, and no rich pockets are expected from design [Medium]); the secondary/dilution air rows (no dilution here, film only); the 2-stage air bookkeeping; the NG-vs-Jet-A matched-Tt4 target.

## 4. Candidate topologies (ranked)

**T1 (preferred): pilot and main PSRs with CRZ recycle, burnout PFR, late film air.** Matches D2(a) plus the one missing physical feature (back-mixing) and film air. Air split from injector effective areas, pilot fuel 29.7%. Few, physically labelled parameters.
- R1 pilot PSR: feed pilot air + pilot fuel (+ recycle); tau_p, phi_p from the split.
- R2 main PSR: main air + main fuel (+ recycle); tau_m.
- R3 recirculation PSR (IRZ/CRZ merged): fed by fraction r of R1+R2 outflow, returns to R1/R2 inlet; r, tau_r.
- R4 mixer: R1+R2 outflow plus film air f; wall heat-loss fraction q.
- R5 PFR to the contraction/exit: tau_b, same q.

**T2: liquid-resolved network.** T1 plus an evaporator/mixer element before each PSR (John) and the main as 3 parallel phi-bins with an exchange rate (Innocenti/Novosselov cross-mixing, or a PaSR tau_mix, Bedick). Targets the fuel-temperature and fuel-property trends. More free parameters than emissions can pin; use only if T1 fails the fuel-temperature trend.
- R1/R2 as T1 but R2 = 3 parallel PSRs (phi_k, mass shares from unmixedness S); E1/E2 evaporator, tau_evap(T_fuel, SMD); X cross-mixing flow m_x (symmetric); then R3-R5 as T1.

**T3: two-stream stoichiometric interface (D2(c), LNG topology B).** Pilot and main streams meet through an interface PSR at phi = 1 (g, tau_int), then PFR. Cheapest NOx knob but unvalidated outside the LNG project, and its rich-parcel premise is weak at phi 0.49. Rank last.
- R1 pilot PSR, R2 main PSR, R_int (fraction g, tau_int), R5 PFR.

## 5. What emissions can and cannot pin

Can (reasoned [High]): overall phi (metered), exit temperature if measured, NOx level (dominated by hot-zone T and tau), CO freeze/burnout lumped as a burnout time plus heat loss (Grimm: CO best at ~40% heat loss vs 20-30% for NOx, so one q cannot fit both [Verified]). Cannot: pilot vs main tau separately, recycle ratio r (confounded with tau and S), film fraction (confounded with q), unmixedness S vs tau_int vs exchange rate (LNG spec Sec. 7 itself expects at least one of S, g, tau_int unidentified [Verified]), mixing time vs CO-chemistry. Published CO errors stay large even for tuned CRNs (70% mean, Zenodo item, unverified) so do not expect a fit of CO to calibrate structure. Identifiability tools: Raue 2009 (10.1093/bioinformatics/btp358) [title only]; D5's Morris screening is the cheap precursor. Report parameter-correlation or profile-likelihood evidence per parameter instead of one best fit.
