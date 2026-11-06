# Inflammation-IFN-cohort

Inflammation — published IFN-induction cohort (n=13 labeled): frozen UGUGU scanner rule = specificity 1.00, sensitivity 0.10; GU-content presence separates (0.124 vs 0.000). Scanner kept as hazard filter; incompleteness measured, not tuned. Rows carry per-row verification flags (Hornung 2005, Judge 2005, Goodchild 2009). Curation + caveats: CURATED_CASE_STUDIES.md in the source workspace.

## Published reference

| Metric | Published value | Source |
|---|---|---|
| UGUGU ⇒ TLR7/8 IFN induction | qualitative (motif necessary/sufficient) | PMIDs 15723075, 15778705 |
| Quantitative sens/spec | **none published** — Run-1 sets the reference | — |

## Run configuration

| Run | Config | Date |
|---|---|---|
| Run-1 | frozen scanner rules (both strands; GU cohort-decile); **no tuning after outcomes**; 13 labeled published duplexes | 2026-11-05 |

## Benchmark metrics

| | IFN-inducing | non-inducing |
|---|---|---|
| UGUGU flagged | 1 | 0 |
| Not flagged | 9 | 3 |

| Metric | Value |
|---|---|
| Sensitivity | **0.1** |
| Specificity | **1.0** |
| GU-fraction mean (IFN+ / IFN−) | 0.124 / 0.0 |
| n labeled | 13 |

Rule frozen (PMIDs 15723075/15778705); deliberately NOT tuned after measuring low sensitivity.
