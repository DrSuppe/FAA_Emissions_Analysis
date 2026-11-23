# COMRAD literature library (Slabaugh group, Purdue Zucrow)

Compiled 2026-11-23 by web search (WebSearch/WebFetch) plus the Murdock GT2026 reference list
(`references/2026_TurboExpo_Murdock_LII.txt`, refs [20], [35]-[39], [42]). Purpose: let a later agent look for gaps
that FTIR gaseous-emissions data could fill. BibTeX: `comrad_library.bib` (keys in column 1).

Tag meaning. `[Verified: URL]` = the paper or its metadata was seen at that URL (search result or fetched page); a
verified row means the citation exists, not that the full text was read. Most rows were verified from abstracts or
metadata only, so the "measured / concluded" column is limited to what those pages state. `[Unverified: ...]` = only
in the Murdock reference list. Full texts were not read except Murdock GT2026 and the ASCENT reports (read as text).

Test-article note. Murdock (GT2026) describes "a piloted, partially premixed, liquid-fueled, swirl burner" in COMRAD.
The ASCENT 2025 report and the Oct-2025 ASCENT slide deck describe the injector as a lean-burn, piloted, partially
premixed, liquid-fueled swirl injector (GE TAPS named in the slide deck). Whether the earlier PIV papers (2017-2021)
used exactly the same injector hardware is not stated on the pages seen.

## 1. Paper table

| Key | Year | First author | Short title | Venue | DOI / URL | Diagnostics | Conditions (P3, T3, fuel, phi, pilot/main) | Measured / concluded (emissions-relevant link) | Tag |
|---|---|---|---|---|---|---|---|---|---|
| slabaugh2014rsi | 2014 | Slabaugh | Optically accessible high-power combustion test rig | Rev. Sci. Instrum. 85(3):1-9 | 10.1063/1.4867084 (seen in Murdock ref [42]) | rig description | not seen | Rig development paper cited by Murdock as the combustor basis; content not read. | [Unverified: from Murdock refs, not located online] |
| meyer2017jpc | 2017 | Meyer | Design of the High Pressure Combustion Laboratory | 53rd AIAA/SAE/ASEE Joint Propulsion Conf., Atlanta, pp. 1-9 | none seen (DOI truncated in text extract) | facility description | not seen | Facility paper (Murdock ref [39]). | [Unverified: from Murdock refs, not located online] |
| zhang2017ncm | 2017 | Zhang | Pilot stagnation region in a high-power liquid-fueled combustor | 10th U.S. National Combustion Meeting, College Park, MD | https://impact.ornl.gov/en/publications/investigation-of-the-pilot-stagnation-region-in-a-high-power-liqu/ | 2-component PIV, 5 kHz, 9.4 px/mm; stagnation-line histograms | high pressure (value not given on page); liquid fuel; varied pilot/main split and global phi | Response of the central recirculation zone to pilot/main fuel split and phi. Funded by GE Aviation. | [Verified: URL] |
| zhang2019proci | 2019 | Zhang | Structure-conditioned velocity statistics, high-pressure swirl flame | Proc. Combust. Inst. 37(4):5031-5038 | 10.1016/j.proci.2018.06.146 | stereo PIV, 6 kHz; shear stress, swirling strength | 1 MPa; varied pilot/main ratio and global phi | Velocity statistics near the stagnation line keep structure across fuel distributions; largest swirling strength coincides with highest shear stress. | [Verified: https://impact.ornl.gov/en/publications/structure-conditioned-velocity-statistics-in-a-high-pressure-swir/] |
| philo2021proci | 2021 | Philo | 100 kHz PIV, liquid-fueled swirl combustor at 1 MPa | Proc. Combust. Inst. 38(1):1571-1578 | 10.1016/j.proci.2020.06.066 | 100 kHz PIV, 10 kHz OH* chemiluminescence | 1.0 MPa; liquid fuel; piloted burner | Periodic vortex generation in the pilot / inner-recirculation-zone shear layer at 4-5.5 kHz; IRZ role in flame stabilization. Murdock cites it as COMRAD flow-field reference. | [Verified: https://ouci.dntb.gov.ua/works/4N0aL6O9] |
| mcdonald2021aiaa | 2021 | McDonald | Fuel temperature, emissions and structure of a swirl-stabilized flame | AIAA Propulsion and Energy 2021 Forum, AIAA 2021-3480 | 10.2514/6.2021-3480 | extractive emissions (NOx, CO, UHC); 50 kHz OH* chemiluminescence | P3 1.0 MPa (Tfuel 373, 473, 568 K) and 2.0 MPa (584 K); T3 755 K; phi 0.33-0.51 | NOx, CO and UHC measured vs fuel temperature and pressure, with OH* images. The only gaseous-emissions paper found on this rig. Abstract text not retrieved; conditions are from a search-engine summary of the AIAA page. | [Verified: https://doi.org/10.2514/6.2021-3480 (search result; AIAA page returned 403)] |
| philo2023fuel | 2023 | Philo | Fuel temperature, structure of high-pressure liquid-fueled swirl flame | Fuel 354:129142 | 10.1016/j.fuel.2023.129142 | per Philo thesis page: stereo PIV, chemiluminescence; Murdock: OH* CL, PIV | ~1 MPa; fuel temperature varied; Jet A (assumed; not on pages seen) | Main flame wings (OH* CL) move downstream and inward as fuel temperature rises (as cited in Murdock). | [Verified: https://ascent.aero/publication/effect-of-fuel-temperature-on-the-structure-of-a-high-pressure-liquid-fueled-swirl-flame/] |
| philo2023thesis | 2023 | Philo | Multi-scale flow and flame dynamics at engine-relevant conditions (PhD) | Purdue Univ. dissertation (posted 6 Oct 2023; ASCENT report says PhD Mar 2022) | https://docs.lib.purdue.edu/dissertations/AAI30506036 | stereo PIV, chemiluminescence (COMRAD part); VIPER-M part is a different rig | varied fuel temperature, pressure, phi | Fuel temperature vs flame structure and "combustion efficiency" in COMRAD. Full text not read. | [Verified: https://docs.lib.purdue.edu/dissertations/AAI30506036] |
| hodge2024scitech | 2024 | Hodge | Fuel temperature, combustion stability (conference) | AIAA SciTech 2024 Forum, AIAA 2024-1241 | 10.2514/6.2024-1241 | high-frequency pressure, PIV/chemiluminescence (per JPP version) | 1.0 MPa | Conference version of hodge2025jpp. | [Verified: https://s3.wp.wsu.edu/uploads/sites/2479/2026/04/ASCENT-Project-067-2025-Annual-Report.pdf] |
| hodge2025jpp | 2025 | Hodge | Fuel temperature effects on combustion stability | J. Propulsion and Power 41(1):53-63 | 10.2514/1.B39592 | dynamic pressure; flame imaging (details not on page seen) | 1.0 MPa; piloted liquid-fueled swirl flame | Self-excited 825 Hz longitudinal instability at ambient fuel temperature; low Tfuel gives unburnt fuel accumulation and strong heat-release response, higher Tfuel (faster evaporation) attenuates it. | [Verified: https://ascent.aero/publication/fuel-temperature-effects-on-combustion-stability-of-a-high-pressure-liquid-fueled-swirl-flame/] |
| mclean2025scitech | 2025 | McLean | LII in a high-pressure swirl-stabilized flame | AIAA SciTech 2025 Forum, AIAA 2025-1580 | 10.2514/6.2025-1580 | LII (soot) | high-pressure swirl-stabilized combustor at aviation-relevant conditions | First COMRAD LII soot-field paper (Murdock ref [20]). Details not read. | [Verified: https://ascent.aero/publication/laser-induced-incandescence-measurements-in-a-high-pressure-swirl-stabilized-flame/] |
| koenig2025thesis | 2025 | Koenig | Soot formation in a high-pressure swirl-stabilized flame (MS) | Purdue Univ. master's thesis | https://hammer.purdue.edu/articles/thesis/_b_Soot_Formation_in_a_High-Pressure_Swirl-Stabilized_Flame_b_/28873268 (page returned 403; seen only in search result) | LII | aviation-representative conditions | Thesis counterpart of the LII work (Murdock ref [35]). | [Verified: URL (search result only)] |
| murdock2026jegtp | 2026 | Murdock | Fuel temperature, soot, Jet A and HEFA-SPK | J. Eng. Gas Turbines Power 148(11):111028 (ASME Turbo Expo 2026 companion) | 10.1115/1.4072536 | 2D gated LII; OH* chemiluminescence | Pilot+main: P3 1.01 MPa, T3 759 K, phi 0.49, air 0.59 kg/s, pilot split 29.7%. Pilot-only: 0.53 MPa, phi 0.28, air 0.415 kg/s. Tfuel 291-579 K; Jet A, HEFA-SPK | Aromatics are needed for soot in pilot+main; HEFA gives very low LII; soot region shifts downstream and inward with Tfuel; pilot-only LII halves by 472 K for Jet A. Companion paper. | [Verified: https://ascent.aero/publication/fuel-temperature-effects-on-soot-formation-in-jet-a-and-hefa-spk-high-pressure-flames/ ; conditions from local Murdock text] |
| mcdonald2025jegtp | 2025 | McDonald | Combustion product measurements, heated fuels (planned) | ASME JEGTP, "to be submitted" | none | extractive emissions | not stated | Listed only in ASCENT 2025 annual report as to be submitted; no published version located. Must be checked before any claim of novelty. | [Verified: ASCENT 2025 report URL above, as a planned paper only; not located as published] |
| ascent2020 | 2021 | Lucht (PI) | ASCENT Project 067, 2020 annual report | FAA ASCENT report | https://s3.wp.wsu.edu/uploads/sites/2479/2021/03/ASCENT-Project-067-2020-Annual-Report.pdf | planned FTIR sampling | planned P3 150-400 psia, T3 900 F, phi 0.37 and 0.50, 30% pilot | Describes the FTIR sampling plan: GE-designed probe just downstream of primary reaction zone, sample line at 191 C. | [Verified: URL (read as PDF text)] |
| ascent2025 | 2026 | Lucht (PI) | ASCENT Project 067, 2025 annual report | FAA ASCENT report | https://s3.wp.wsu.edu/uploads/sites/2479/2026/04/ASCENT-Project-067-2025-Annual-Report.pdf | extractive sampling, LII, NO PLIF (bench), PIV, Mie, dynamic pressure | T3 755 K, up to 20 bar, Tfuel up to ~590 K, Jet A, Shell GTL GS190, World Energy HEFA | States prior extractive sampling found NO increased by a factor of two for Tfuel 366 to 589 K; NO-PLIF built to examine it; GE wants pilot/main phi variation, pilot-only, and NOx. | [Verified: URL (read as PDF text)] |
| ascent2025slides | 2025 | Lucht (PI) | ASCENT 067 project slides, Oct 2025 | ASCENT meeting presentation | https://s3.wp.wsu.edu/uploads/sites/2479/2025/10/1300_10162025_ASCENT-067_Lucht.pdf | emissions, 10 kHz stereo-PIV, Mie, chemiluminescence, LII, OH-PLIF, NO PLIF | Tfuel 370-580 K, 1-2 MPa; Jet A and GS190; lean-burn TAPS injector | "Characterized effect of fuel temperature (370-580 K) and chamber pressure (1-2 MPa) on emissions with Jet A and Shell GTL GS190." Future: HEFA+SAK emissions, NO PLIF. | [Verified: URL (read as PDF text)] |

Rows excluded on purpose (found, but not this test article): Slabaugh et al., AIAA J. 54:946 (2016) and the CPP-CARS
pair (Combust. Flame 173, 2016), which are on the DLR/Purdue gas-turbine model combustor listed on luchtgroup.org
(not seen to involve COMRAD); Chterev et al. 2017 and Ek et al. 2017 (Georgia Tech); Shahin et al. hydrogen-ammonia-natural gas
micromix work (different injector, ~1.1 MPa; osti.gov/pages/biblio/2515641). Leads not resolved: Slabaugh PhD
dissertation (Purdue, kilohertz planar laser diagnostics, https://docs.lib.purdue.edu/dissertations/AAI3636523, title only seen);
a Purdue thesis "Analysis Techniques for Characterizing High Power Turbulent Swirl Flames"
(hammer.purdue.edu/articles/thesis/8159288, title only, author not confirmed); Shahin PhD dissertation (Oct 2025, not found online); Murdock thesis (not found).
Also not found: Slabaugh or Philo OH-PLIF papers on COMRAD (the ASCENT reports say OH-PLIF is performed in COMRAD, no paper located), and any
HEFA/Jet A fuel-temperature FTIR paper.

## 2. Data and quantities measured on this test article

| Quantity | Paper | Conditions |
|---|---|---|
| 2-component velocity, 5 kHz PIV | zhang2017ncm | high pressure, varied pilot/main split and phi |
| 3-component stereo PIV, 6 kHz; shear stress, swirling strength | zhang2019proci | 1 MPa; varied split and phi |
| 100 kHz PIV of IRZ and pilot shear layer; vortex frequency 4-5.5 kHz | philo2021proci | 1.0 MPa |
| 10 kHz OH* chemiluminescence | philo2021proci | 1.0 MPa |
| 50 kHz OH* chemiluminescence | mcdonald2021aiaa | 1.0 and 2.0 MPa, Tfuel 373-584 K |
| NOx, CO, UHC (extractive) | mcdonald2021aiaa | 1.0 MPa (373, 473, 568 K), 2.0 MPa (584 K), T3 755 K, phi 0.33-0.51 |
| Extractive exhaust sampling, Jet A and GS190, Tfuel 370-580 K, 1-2 MPa (species not enumerated in ASCENT text except NO) | ascent2025slides, ascent2025 | as stated |
| NO: factor of two rise for Tfuel 366 to 589 K (value stated in prose only) | ascent2025 | conditions not given in the passage |
| Flame structure vs fuel temperature (PIV and chemiluminescence) | philo2023fuel, philo2023thesis | 1.0 MPa class, Tfuel varied |
| Dynamic pressure (plenum Kulite), 825 Hz instability, heat-release response | hodge2025jpp, ascent2025 | 1.0 MPa |
| 10 kHz stereo-PIV and Mie scattering (droplets), vs Tfuel | ascent2025slides | not tabulated |
| LII (gated) soot fields, Jet A and HEFA | mclean2025scitech, koenig2025thesis, murdock2026jegtp | Murdock: pilot+main 1.01 MPa, 759 K, phi 0.49; pilot-only 0.53 MPa, phi 0.28; Tfuel 291-579 K |
| OH* chemiluminescence concurrent with LII | murdock2026jegtp | same as above |
| Time-resolved LII particle size | ascent2025 | model applied to a lab flame only; not COMRAD data |
| Rig operating data (flows by Coriolis/venturi, pressures, K-type thermocouples at 100 Hz); mass-flow uncertainty <0.83% gas, <0.10% fuel | ascent2025 | rig-wide |
| Dissolved oxygen in fuel kept below 0.2% of saturation | ascent2025 | rig-wide |
| Rich- vs lean-dome Jet A LII at ambient fuel: global phi 0.45-0.60, pilot phi 0.97-1.33 | ascent2025slides | ambient Tfuel (300 K) |

## 3. What has not been measured or reported (observations from the sources found)

- No paper found reports FTIR spectra or a species list beyond NOx, CO and UHC for COMRAD; the 2021 paper's analyzer type was not seen.
- The only emissions publication found (mcdonald2021aiaa) is a 2021 conference paper; its data tables were not seen, and the journal paper (mcdonald2025jegtp) is marked "to be submitted" in the 2025 report.
- No emissions data found for HEFA-SPK or for any fuel at pilot-only conditions. ASCENT 2025 lists HEFA+SAK emissions and pilot-only operation as future work.
- The 2025 report says the pilot and main equivalence ratios were held fixed so far; pilot/main variation and NOx are listed as planned.
- The 2025 report gives NO rising by a factor of two with fuel temperature but gives no NO values, no CO, no CO2, no NO2, and no sampling-line treatment in the passage read.
- No published in-chamber composition or temperature measurement on COMRAD was found (no species PLIF besides OH, NO-PLIF only in a gas cell, no thermometry, no CRN or CFD paper on this rig).
- Murdock GT2026 (LII) reports no gas-phase data; no nvPM mass or number was reported there.
- The sampling-system plan (GE probe, 191 C line) appears only in the 2020 annual report; no paper describes probe position, quench, residence time, or correction for line chemistry.
- Dynamic-pressure data exist only at 1.0 MPa for the stability paper, and no paper links the 825 Hz instability to emissions.
- No gaseous emissions for the Murdock conditions (1.01 MPa, 759 K, phi 0.49, 29.7% pilot) were found in the literature searched.
- OH-PLIF, fuel-PLIF and 3-component PIV in COMRAD are named in ASCENT text; no COMRAD paper reporting them was found.
- Search coverage limit: Google Scholar, ASME and AIAA pages were mostly not retrievable (403); IEEE-style indexing may hide further papers.
