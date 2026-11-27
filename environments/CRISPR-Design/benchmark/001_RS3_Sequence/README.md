# RS3 Sequence held-out activity

## Evaluation definition

Six author-defined activity cohorts; native30nt context and Hsu2013/Chen2013 tracr features. Exact20mer four-model training-union exclusions;23629unique contexts/26915deduplicated dataset observations.

Primary source(s): https://europepmc.org/articles/PMC9448816

## Scientific limits

RS3 Sequence only, not Sequence+Target. Gene-cluster intervals for genomewide cohorts, guide-row intervals otherwise. Original source duplicate-row weighting is a separate retained reproduction, not extra independent observations.

This benchmark evaluates a model endpoint, not a complete design application.

## Captured protocol and execution evidence

The following files are the original execution snapshots under `results/`; they
record inputs, splits, model identity or independent verification where available.

- [model_identity.json](../../results/benchmarks/001_RS3_Sequence/Run-4_2026-11-12/model_identity.json)
- [source_cohort_protocol.json](../../results/benchmarks/001_RS3_Sequence/Run-4_2026-11-12/source_cohort_protocol.json)
- [source_replay_protocol.json](../../results/benchmarks/001_RS3_Sequence/Run-4_2026-11-12/source_replay_protocol.json)

[Completed report](../../results/benchmarks/001_RS3_Sequence/Run-4_2026-11-12/REPORT.md) · [Registry](../BENCHMARK_RUNS.md)

Original execution recipe: [inference.py](../../scripts/benchmarks/001_RS3_Sequence/inference.py).
