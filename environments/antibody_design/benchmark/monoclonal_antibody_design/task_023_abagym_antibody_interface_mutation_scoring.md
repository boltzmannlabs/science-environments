# Benchmark: AbAgym: Antibody Interface Mutation-Effect Scoring

**Task ID:** `task_023_abagym_antibody_interface_mutation_scoring`

**Task:** [AbAgym: Antibody Interface Mutation-Effect Scoring](../../tasks/monoclonal_antibody_design/task_023_abagym_antibody_interface_mutation_scoring.md)

## Published Computational Metrics

**Source:** [AbAgym, mAbs 2025](https://doi.org/10.1080/19420862.2025.2592421), Table 1 and Supplement Section 5; source snapshot [3BioCompBio/AbAgym @ `87af82ad68bb`](https://github.com/3BioCompBio/AbAgym/tree/87af82ad68bb90921e15fb8b79c7bcb1d05b23d3).

| Published method | Mean per-DMS Spearman ρ | Mean per-DMS ROC-AUC |
| --- | --- | --- |
| FoldX | 0.25 | 0.72 |
| BeAtMuSiC | 0.20 | 0.63 |
| Relative solvent accessibility baseline | 0.28 | 0.69 |

These are source Table 1 averages across interface-mutation DMS experiments. ROC-AUC uses each source assay's top 5% most disruptive mutations as the positive class. The nonredundant source interface set uses a 6 Å heavy-atom definition.

## Evaluation Protocol

- Preserve the source experiment, mutation partner, residue mapping and DMS score direction.
- Calculate Spearman ρ and ROC-AUC per DMS experiment and report equal-assay averages.
- Apply the same source assay population, top-5% threshold and tie convention as the compared Table 1 result.
- Keep antibody-side subset results separately labelled from the source mixed-partner aggregate.
