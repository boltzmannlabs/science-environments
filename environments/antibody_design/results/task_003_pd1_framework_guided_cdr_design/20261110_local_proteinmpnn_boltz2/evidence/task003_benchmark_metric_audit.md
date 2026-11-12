# Task 003 Benchmark Metric Audit — PD-1 Framework-Guided CDR Design

Generated: 2026-11-11T12:22:48.876756+00:00

Only task 003 is included in this audit. Other antibody-design tasks are intentionally excluded.

Benchmark source: `benchmark/monoclonal_antibody_design/task_003_pd1_framework_guided_cdr_design.md`, based on the tFold PD-1 study (PMC12815924).

| Metric | Published benchmark | Scope/method | Current task result | Status | Limitation |
|---|---|---|---|---|---|
| PD-1 virtual-screening AUROC | 0.76 | 745-antibody panel; 27 positives; higher is better | Not computed | unresolved | Original labelled panel, negative/positive definitions and score orientation are absent. A single candidate cannot yield AUROC. |
| PD-1 top-1% enrichment factor | 7.41 | Same 745-antibody panel; 2 positives among 7 selected | Not computed | unresolved | Original panel and exact ranking score are absent. Candidate ipTM is not the benchmark score. |
| PD-1 designed-antibody discrimination AUROC | 0.95 | Separate tFold design-campaign analysis | Not computed | unresolved | Campaign labels and evaluation protocol are absent. |
| Epitope-informed CDR-H3 AAR | 0.317 | SAbDab-22-DesignAb aggregate; reconstruction metric | Not computed on benchmark dataset | unresolved | Exact dataset release, mask, split and scoring implementation are absent. |
| Candidate-level Boltz2 complex confidence | No published candidate-level benchmark value | H965 individual values are not the paper AUROC/AAR metrics | H965 ipTM 0.878; cand2 0.760; cand9 0.671; cand11 0.652 | candidate_level_only | Useful matched local control comparison, but not comparable to the four published aggregate metrics. |

## Current task execution boundary

- The historical local run contains 20 CDR-H3 designs, with 3 candidates structurally evaluated and retained in the current result package.
- The pending six-CDR Boltzmann platform run was not submitted because partial-upload approval timed out.
- Therefore no newly generated platform candidate can be assigned to the published tFold aggregate metrics.

## Conclusion

**The four published benchmark metrics are not reproduced for task 003.** This is a data/protocol limitation, not a zero score. The available candidate-level Boltz2 values are reported separately and must not be interpreted as AUROC, enrichment or AAR.
