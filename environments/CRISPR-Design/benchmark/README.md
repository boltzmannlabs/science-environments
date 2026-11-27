# Completed computational benchmarks

This directory holds **benchmark definitions, evaluation criteria and the registry** for completed
native-model/endpoint evaluations. No heuristic rule, missing-feature
imputation or surrogate endpoint was added. A completed model benchmark is **not**
validation of the full design application and not experimental safety — scientifically
material limitations (weak transfer, source-protocol differences, label-threshold
semantics) remain attached to every result.

## Registry

| Benchmark | Model | Evidence |
| --- | --- | --- |
| 001 | RS3 Sequence held-out activity | [Report](../results/benchmarks/001_RS3_Sequence/Run-4_2026-11-12/REPORT.md) |
| 002 | CRISPRon v1 external activity | [Report](../results/benchmarks/002_CRISPRon/Run-4_2026-11-12/REPORT.md) |
| 003 | CFD2016 experimentally assayed specificity | [Report](../results/benchmarks/003_CFD2016/Run-4_2026-11-12/REPORT.md) |
| 004 | BE-Hive BE4 any-edit efficiency | [Report](../results/benchmarks/004_BEHive_BE4/Run-4_2026-11-12/REPORT.md) |
| 005 | PRIDICT2.0 published grouped OOF outcomes | [Report](../results/benchmarks/005_PRIDICT2/Run-4_2026-11-12/REPORT.md) |
| 006 | DeepPrime base fixed test | [Report](../results/benchmarks/006_DeepPrime_PE2/Run-4_2026-11-12/REPORT.md) |
| 007 | RFcombined published-method refit evaluation | [Report](../results/benchmarks/007_RFcombined/Run-4_2026-11-12/REPORT.md) |

Scope and limitation details per benchmark: [BENCHMARK_RUNS.md](BENCHMARK_RUNS.md).
Machine-readable ledger (drives `tests/test_completed_benchmarks.py` and
`tests/validate_spec.py` check 8): [completed_benchmarks.json](completed_benchmarks.json)
(+ [CSV](completed_benchmarks.csv)).

## Run layout and provenance

Task benchmarks live at `00N_<task-name>/README.md`, matching the task definition
filenames. Each task index links its shared evaluation definitions and describes endpoint
evaluation scope, primary sources and scientific limitations. Execution outputs live
at `../results/benchmarks/00N_<Model>/Run-4_2026-11-12/`: reports, predictions, metrics,
benchmark records, execution logs and exact protocol/model snapshots. Original
execution scripts are under `../scripts/benchmarks/00N_<Model>/`.
Fresh native-inference retries completed for RS3, BE-Hive, PRIDICT2.0,
DeepPrime and CFD (predictions verified identical at saved precision); CRISPRon and
RFcombined retain their already-completed native runs. Confidence intervals use
declared resampling units; repeated use of the same measured labels is reproducibility
evidence, not a new independent replication.

All copied scientific files are bound by [PROVENANCE.json](../results/benchmarks/PROVENANCE.json) /
[PROVENANCE.sha256](../results/benchmarks/PROVENANCE.sha256) (source and destination SHA-256). Large
datasets, weights and environments remain at indexed source locations — this is not a
self-contained portable distribution.

## Relationship to older evidence

Earlier mixed evidence — publication-label replays, per-task Run-2/Run-3 comparisons,
component tests and partial attempts — was referenced under `execution_history/` in
older documentation. That archive is [absent from this checkout](../results/HISTORY.md).
Its preservation is unverified here. No wet-lab validation or calibrated design-gate
freeze is claimed anywhere in this package.

## Task benchmarks

- [001_crispr_design_general](001_crispr_design_general/README.md)
- [002_crispr_knockout](002_crispr_knockout/README.md)
- [003_crispr_therapeutic-in-vivo](003_crispr_therapeutic-in-vivo/README.md)
- [004_crispr_variant-correction](004_crispr_variant-correction/README.md)
- [005_crispr_base-editing](005_crispr_base-editing/README.md)
- [006_crispr_prime-editing](006_crispr_prime-editing/README.md)
- [009_crispr_rna-targeting-cas13](009_crispr_rna-targeting-cas13/README.md)
- [011_crispr_library-screen-design](011_crispr_library-screen-design/README.md)

Only tasks supported by completed evaluations have benchmark directories. Other task
statuses remain in the [task index](../tasks/README.md). Model names identify the
underlying evaluations and execution artifacts within the registry.
