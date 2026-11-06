# Benchmark: LCAT: Reference Fab CDR-H3 Reconstruction

**Task ID:** `task_004_lcat_reference_fab_cdrh3_reconstruction`

**Task:** [LCAT: Reference Fab CDR-H3 Reconstruction](../../tasks/monoclonal_antibody_design/task_004_lcat_reference_fab_cdrh3_reconstruction.md)

**Reviewed:** 2026-11-05

## Benchmark Scope

A single human-LCAT CDR-H3 reconstruction case from the released RAbD test set. Paper-wide results below are aggregate comparison references, not published scores for the selected 5BV7 case.

## Published Results

**Source:** [AbFlow, KDD 2026; manuscript v2, September 2026](https://arxiv.org/html/2602.07084v2), Tables 1–2; [publication DOI](https://doi.org/10.1145/3770854.3780296). The [authors' released dataset](https://huggingface.co/wenda8759/AbFlow/blob/main/datasets.zip) contains the 60-entry RAbD test manifest, including 5BV7.

| Published metric | Table 1 result, mean ± SD | Direction |
| --- | ---: | --- |
| AAR | **0.4234 ± 0.1334** | Higher |
| TM-score | **0.9736 ± 0.0090** | Higher |
| lDDT | **0.8522 ± 0.0216** | Higher |
| CAAR | **0.2824 ± 0.2037** | Higher |
| RMSD | **8.25 ± 4.55 Å** | Lower |
| DockQ | **0.423 ± 0.161** | Higher |

| Additional Table 2 benchmark | Reported result | Scope |
| --- | ---: | --- |
| Multi-CDR RMSD: H1 / H2 / H3 | **0.63 / 0.55 / 1.83 Å** | Separate multi-CDR evaluation. |
| Multi-CDR RMSD: L1 / L2 / L3 | **0.64 / 0.25 / 0.65 Å** | Separate multi-CDR evaluation. |
| Full-atom RMSD | **1.102 Å** | Separate full-atom evaluation. |
| Full-atom TM-score / lDDT / DockQ | **0.9707 / 0.8151 / 0.431** | Same Table 2 full-atom evaluation. |

These are aggregate results, not published 5BV7 candidate scores. The paper's RMSD descriptions differ between Section 5.2 and Appendix C; resolve atom selection and alignment before claiming exact reproduction. Table 1 and Table 2 RMSDs must not be merged. lDDT measures agreement to a reference and is distinct from predicted confidence pLDDT. Published method results are not necessarily the best result for every metric across all comparators.

## Evaluation Criteria

| Criterion | Comparison requirement | Acceptance boundary |
| --- | --- | --- |
| Input isolation | Withhold the native CDR-H3 sequence, loop coordinates and native pose until candidate generation is frozen. | Record public-reference exposure; copied native outputs do not demonstrate design. |
| Recovery and structure | Report AAR, CAAR, RMSD, TM-score, lDDT and DockQ with explicit scopes, mappings and versions. | Resolve the paper's RMSD-definition discrepancy before claiming exact reproduction. |
| Dataset-level comparison | Use the complete corresponding evaluation set and sampling/aggregation procedure. | One case cannot establish the paper's mean or standard deviation. |
