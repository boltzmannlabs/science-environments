# Benchmark: CHIMERA: Epitope-Conditioned CDR Design

**Task ID:** `task_010_chimera_epitope_conditioned_cdr_design`

**Task:** [CHIMERA: Epitope-Conditioned CDR Design](../../tasks/monoclonal_antibody_design/task_010_chimera_epitope_conditioned_cdr_design.md)

## Published Computational Metrics

**Source:** [CHIMERA-Bench paper, 2026](https://arxiv.org/abs/2603.13431), [data release](https://zenodo.org/records/20598827), and [mansoor181/chimera-bench @ `c0ada2ff045e`](https://github.com/mansoor181/chimera-bench/tree/c0ada2ff045e1622ef39e4a25db34724813f378a), README leaderboard and evaluation metric definitions.

| Published comparator | AAR | CAAR | Cα RMSD (Å) | Fnat | DockQ | Epitope F1 |
| --- | --- | --- | --- | --- | --- | --- |
| MEAN | 0.42 ± 0.15 | 0.21 ± 0.23 | 2.01 ± 0.89 | 0.48 ± 0.31 | 0.63 ± 0.21 | 0.67 ± 0.29 |
| RAAD | 0.38 ± 0.13 | 0.21 ± 0.23 | 1.95 ± 0.87 | 0.49 ± 0.30 | 0.64 ± 0.21 | 0.67 ± 0.27 |

These are source-reported best-of-K HCDR3 results on the epitope-group test set, expressed as mean ± standard deviation. AAR, CAAR, Fnat, DockQ and epitope F1 favor higher values; Cα RMSD favors lower values.

## Evaluation Protocol

- Retain the source dataset release, epitope-group split, CDR masks and source metric implementations.
- Use the same candidate budget K and best-of-K selection rule as the compared result; report model-ranked top-1 separately.
- Match residue correspondence, atom selection, alignment and contact definitions for each structural/interface metric.
- Compare filtered target subsets using baselines rerun on the same subset and generation budget.
