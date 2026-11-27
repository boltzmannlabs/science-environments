# Task 002: crispr knockout — benchmark evidence

[Task definition](../../tasks/002_crispr_knockout.md) · [Benchmark registry](../BENCHMARK_RUNS.md)

The evaluations below support this task at the component level. They do not
establish full application or experimental validation. Shared evaluations reference
the same execution records and are not independent task replications.

| Evaluation | Definition and limitations | Completed report |
| --- | --- | --- |
| RS3 Sequence held-out activity | [Evaluation definition](../002_crispr_knockout/README.md#evaluation-001) | [Report](../../results/benchmarks/001_RS3_Sequence/Run-4_2026-11-12/REPORT.md) |
| CRISPRon v1 external activity | [Evaluation definition](../002_crispr_knockout/README.md#evaluation-002) | [Report](../../results/benchmarks/002_CRISPRon/Run-4_2026-11-12/REPORT.md) |
| CFD2016 experimentally assayed specificity | [Evaluation definition](../003_crispr_therapeutic-in-vivo/README.md#evaluation-003) | [Report](../../results/benchmarks/003_CFD2016/Run-4_2026-11-12/REPORT.md) |

## Evaluation 001

**RS3 Sequence held-out activity**

### Evaluation definition

Six author-defined activity cohorts; native30nt context and Hsu2013/Chen2013 tracr features. Exact20mer four-model training-union exclusions;23629unique contexts/26915deduplicated dataset observations.

Primary source(s): https://europepmc.org/articles/PMC9448816

### Scientific limits

RS3 Sequence only, not Sequence+Target. Gene-cluster intervals for genomewide cohorts, guide-row intervals otherwise. Original source duplicate-row weighting is a separate retained reproduction, not extra independent observations.

This benchmark evaluates a model endpoint, not a complete design application.

### Captured protocol and execution evidence

The following files are the original execution snapshots under `results/`; they
record inputs, splits, model identity or independent verification where available.

- [model_identity.json](../../results/benchmarks/001_RS3_Sequence/Run-4_2026-11-12/model_identity.json)
- [source_cohort_protocol.json](../../results/benchmarks/001_RS3_Sequence/Run-4_2026-11-12/source_cohort_protocol.json)
- [source_replay_protocol.json](../../results/benchmarks/001_RS3_Sequence/Run-4_2026-11-12/source_replay_protocol.json)

[Completed report](../../results/benchmarks/001_RS3_Sequence/Run-4_2026-11-12/REPORT.md) · [Registry](../BENCHMARK_RUNS.md)

Original execution recipe: [inference.py](../../scripts/benchmarks/001_RS3_Sequence/inference.py).

## Evaluation 002

**CRISPRon v1 external activity**

### Evaluation definition

Completed native v1 inference on the same six RS3-publication common-exclusion cohorts; exact30nt contexts and native thermodynamic inputs.

Primary source(s): https://europepmc.org/articles/PMC8163799 ; comparator protocol https://europepmc.org/articles/PMC9448816

### Scientific limits

This is the RS3 comparative held-out protocol, not CRISPRon_v0 internal0.80 reproduction or its different<=3mm training-exclusion procedure. No cross-assay universal superiority claim.

This benchmark evaluates a model endpoint, not a complete design application.

### Captured protocol and execution evidence

The following files are the original execution snapshots under `results/`; they
record inputs, splits, model identity or independent verification where available.

- [protocol.json](../../results/benchmarks/002_CRISPRon/Run-4_2026-11-12/protocol.json)

[Completed report](../../results/benchmarks/002_CRISPRon/Run-4_2026-11-12/REPORT.md) · [Registry](../BENCHMARK_RUNS.md)
