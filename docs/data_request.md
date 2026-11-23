# Data request for the GT2027 paper (architect, 2026-11-23)

What the reduction, the model and the figures need, in the order of importance. Drop files under
`data/raw/<campaign>/` (git-ignored except this note) or give a server path in `coordination/STATUS.md`.
Formats: whatever the rig produces; CSV/XLSX/MAT are all fine. Do not pre-process. Say what each column means
if the header is not self-explanatory.

## 1. Test summary sheet (the one with operating points and emissions already tabulated)
Per case: case id, date, fuel, test type (pilot-and-main / pilot-only / phi sweep), P3, T3, air mass flow,
pilot and main fuel flows, fuel temperatures (pilot, main), sample-line setpoints, steady-state window
(start/end time), and any emissions numbers already reduced (which basis: wet/dry, ppm/EI). This single file
drives the test-matrix figure and the per-case model inputs.

## 2. FTIR time series (1 Hz), raw export per test day
All quantified species (CO2, CO, H2O, NO, NO2, UHC and whatever else the method reports), cell temperature and
pressure, sample flow or pressure, plus the FTIR method/calibration file name. Timestamps that line up with the
station data. Zero/span checks if logged.

## 3. Station (test-stand) time series
P3, T3, air and fuel flows, fuel temperatures, sampling-line heater temperatures, probe coolant in/out, any
exhaust thermocouples, at the stand's logging rate, with timestamps.

## 4. Hardware (one page, `coordination/notes/sampling_train.md`, decisions D2/D3)
- Probe: body geometry, number and diameter of sampling holes, internal passage length and bore, coolant and
  its temperature, axial/radial position in the combustor.
- Sample line: heated stainless length, bore, setpoint; PTFE length, bore, temperature; venturi/orifice size
  and downstream pressure; sample mass flow; FTIR cell temperature and pressure; pump or ejector.
- Injector: pilot and main air effective areas (or the split the rig team uses), film-cooling air fraction and
  where it enters relative to the sampling plane, combustor cross-section and length to the probe.

## 5. Fuels (decision D7)
GS190 datasheet; Jet A and HEFA lot certificates: density, distillation curve, aromatics, H/C or hydrogen
content, net heat of combustion, viscosity.

## 6. Nice to have
PIV / OH-PLIF / chemiluminescence datasets or figures at the same operating points (for the insight quorum);
photos of the probe installation; the LII operating-point table if the emissions cases map onto it.
