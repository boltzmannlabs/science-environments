# Completed computational benchmarks

This directory is the **active benchmark publication**: only completed
native-model/endpoint evaluations are included. No heuristic rule, missing-feature
imputation or surrogate endpoint was added. A completed model benchmark is **not**
validation of the full design application and not experimental safety — scientifically
material limitations (weak transfer, source-protocol differences, label-threshold
semantics) remain attached to every result.

## Registry

| Benchmark | Model | Evidence |
| --- | --- | --- |
| 001 | RS3 Sequence held-out activity | [Report](001_RS3_Sequence/Run-4_2026-11-12/REPORT.md) |
| 002 | CRISPRon v1 external activity | [Report](002_CRISPRon/Run-4_2026-11-12/REPORT.md) |
| 003 | CFD2016 experimentally assayed specificity | [Report](003_CFD2016/Run-4_2026-11-12/REPORT.md) |
| 004 | BE-Hive BE4 any-edit efficiency | [Report](004_BEHive_BE4/Run-4_2026-11-12/REPORT.md) |
| 005 | PRIDICT2.0 published grouped OOF outcomes | [Report](005_PRIDICT2/Run-4_2026-11-12/REPORT.md) |
| 006 | DeepPrime base fixed test | [Report](006_DeepPrime_PE2/Run-4_2026-11-12/REPORT.md) |
| 007 | RFcombined published-method refit evaluation | [Report](007_RFcombined/Run-4_2026-11-12/REPORT.md) |

Scope and limitation details per benchmark: [BENCHMARK_RUNS.md](BENCHMARK_RUNS.md).
Machine-readable ledger (drives `tests/test_completed_benchmarks.py` and
`tests/validate_spec.py` check 8): [completed_benchmarks.json](completed_benchmarks.json)
(+ [CSV](completed_benchmarks.csv)).

## Run layout and provenance

Each benchmark lives at `00N_<Model>/Run-4_2026-11-12/` and contains `REPORT.md`,
`predictions.csv`, `metrics.csv` (or `metrics.json`), `model_identity.json`,
`benchmark_record.json`, an execution log, the exact protocol manifest(s) and the
scripts used. Fresh native-inference retries completed for RS3, BE-Hive, PRIDICT2.0,
DeepPrime and CFD (predictions verified identical at saved precision); CRISPRon and
RFcombined retain their already-completed native runs. Confidence intervals use
declared resampling units; repeated use of the same measured labels is reproducibility
evidence, not a new independent replication.

All copied scientific files are bound by [PROVENANCE.json](PROVENANCE.json) /
[PROVENANCE.sha256](PROVENANCE.sha256) (source and destination SHA-256). Large
datasets, weights and environments remain at indexed source locations — this is not a
self-contained portable distribution.

## Relationship to older evidence

Earlier mixed evidence — publication-label replays, per-task Run-2/Run-3 comparisons,
heuristic component tests, partial and failed attempts — is preserved byte-identically
in [execution_history/](../execution_history/before_completed_only_20261112T061830Z/README.md)
and is not promoted into this registry. No wet-lab validation or calibrated design-gate
freeze is claimed anywhere in this package.
