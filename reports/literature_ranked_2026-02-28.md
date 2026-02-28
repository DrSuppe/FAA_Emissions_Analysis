# Literature Shortlist and Ranking (2026-02-28)

## Why this ranking
To prioritize strong references quickly, we use a transparent proxy score:

`quality_proxy = 0.6 * normalized(journal_impact_score) + 0.4 * normalized(author_h_index)`

- `journal_impact_score`: journal-level impact score from Resurchify (derived from SCImago/Scopus metadata).
- `author_h_index`: highest relevant combustion/modeling author h-index available from public profile pages (Scinapse or Scopus profile pages).

This is only a prioritization heuristic, not proof of scientific correctness.

## Ranked references (priority reading)
1. **Lu, T.; Law, C. K. (2009)**  
   *Toward accommodating realistic fuel chemistry in large-scale computations.*  
   Journal: *Progress in Energy and Combustion Science*  
   DOI: https://doi.org/10.1016/j.pecs.2008.10.002  
   Proxy inputs: journal impact score 44.90, author h-index 91  
   Quality proxy: **1.000**

2. **Luo, Z.; Som, S.; Sarathy, S. M.; Pitz, W. J.; et al. (2012)**  
   *A reduced mechanism for biodiesel surrogates for compression ignition engine applications.*  
   Journal: *Fuel*  
   DOI: https://doi.org/10.1016/j.fuel.2012.04.028  
   Proxy inputs: journal impact score 8.78, author h-index 78  
   Quality proxy: **0.460**

3. **Liu, M.; Demirel, Y.; Liang, X.; et al. (2021)**  
   *Reaction Mechanism Generator v3.0: Advances in automatic mechanism generation.*  
   Journal: *Journal of Chemical Information and Modeling*  
   DOI: https://doi.org/10.1021/acs.jcim.0c01480  
   Proxy inputs: journal impact score 5.45, author h-index 78  
   Quality proxy: **0.416**

4. **Kundu, P.; Wang, Y.; Som, S.; Pitz, W. J. (2021)**  
   *Implementation of multi-component diesel fuel surrogates in engine simulations.*  
   Journal: *Transportation Engineering*  
   DOI: https://doi.org/10.1016/j.treng.2020.100042  
   Proxy inputs: journal impact score 5.01, author h-index 78  
   Quality proxy: **0.410**

5. **Selim, H.; Nativel, D.; et al. (2017)**  
   *Premixed laminar flame chemistry of gasoline and its surrogate fuel PRF95 in a flow reactor and a flat-flame burner.*  
   Journal: *Combustion and Flame*  
   DOI: https://doi.org/10.1016/j.combustflame.2017.02.008  
   Proxy inputs: journal impact score 7.13, author h-index 66  
   Quality proxy: **0.385**

## Strong method anchors (not ranked in the proxy table)
- **Kennedy, M. C.; O'Hagan, A. (2001)**, Bayesian calibration framework.  
  DOI: https://doi.org/10.1111/1467-9868.00294
- **Novosselov, I. V.; Malte, P. C.; Yuan, S.; et al. (2010)**, CRN NOx prediction for gas turbine combustors.  
  DOI: https://doi.org/10.1016/j.fuel.2010.02.010
- **Park, P.; Keel, S.; Yun, S.; et al. (2013)**, CRN-based NOx/CO prediction in lean premixed GT combustors.  
  DOI: https://doi.org/10.1021/ef301741t
- **Lignell, D.; Contino, F.; et al. (2019)**, practical CRN emissions workflow for GT systems.  
  DOI: https://doi.org/10.1115/1.4044369

## Data sources used for proxy inputs
- Journal impact score (PECS): https://www.resurchify.com/impact/details/21496
- Journal impact score (Fuel): https://www.resurchify.com/impact/details/21100342914
- Journal impact score (Combustion and Flame): https://www.resurchify.com/impact/details/24844
- Journal impact score (JCIM): https://www.resurchify.com/impact/details/16332
- Journal impact score (Transportation Engineering): https://www.resurchify.com/impact/details/21101040699
- Author h-index (C. K. Law): https://www.scinapse.io/authors/2052469365
- Author h-index (S. M. Sarathy): https://www.scinapse.io/authors/2150047950
- Author h-index (S. Som): https://www.scinapse.io/authors/144213212
- Author h-index (W. J. Pitz, Scopus profile): https://www.sciencedirect.com/scientist/321722/william-j-pitz
- Author h-index (W. H. Green, Scopus profile): https://www.sciencedirect.com/scientist/1831846/william-h-green
- Author h-index (T. Lu, Scopus profile): https://www.sciencedirect.com/scientist/556357/tianfeng-lu

## Notes and cautions
- h-index and journal impact are field- and age-dependent; they should not replace mechanistic relevance, validation quality, and reproducibility.
- For your use case, relevance filters should be: gas-turbine combustors, CRN/PFR abstractions, probe/sampling-line transport effects, and Bayesian inversion under model discrepancy.
