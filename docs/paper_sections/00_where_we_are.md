# Where we are (2026-11-17)

- Abstract accepted for GT2027 (Combustion, Fuels and Emissions). Draft due 2026-12-21.
- Paper text: the user writes in Overleaf (repo `DrSuppe/FAA_emissions_paper`, read here as `papers/FAA_emissions_paper`).
  The agent's proposed text lives in `docs/paper_ideal/main.tex`; the Paper diff tab shows the two side by side.
- Data: FTIR and station files not yet in hand (T1). Model: the June scaffold is at a non-reacting baseline and a
  wrong operating point (D1); nothing in the paper can come from it yet.
- Next: decisions D1-D8, hardware numbers (T3, T4), then the model config and the first forward run (T9).

## Paper skeleton mapped to the abstract's claims
1. Introduction: SAF gaseous emissions at pressure; heated fuels; why the analyzer composition differs from the chamber.
2. Experiment: COMRAD, injector, fuels (Table: properties incl. GS190), sampling train (Figure: probe to FTIR), FTIR, test matrix (Figure: phi vs T_fuel).
3. Data reduction: wet/dry basis, carbon balance, emission indices (D6), uncertainty of the FTIR.
4. Model: reactor network of combustor and sampling train (Figure: network), mechanism, calibrated parameters (D2, D3, D5).
5. Results: EI NOx, CO, UHC vs fuel temperature per fuel; vs phi at three fuel temperatures; fuel comparison; inferred combustor-exit composition and sample-line NO2 fraction (D4); uncertainty bounds.
6. Conclusions.
