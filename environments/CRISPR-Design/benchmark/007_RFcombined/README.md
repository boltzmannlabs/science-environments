# RFcombined published-method refit evaluation

## Evaluation definition

Completed1000native randomForest2000tree/mtry12fits using published2918row35feature matrix,sourceR3.5seed schedule,screen-balanced70/30splits and training-only scaling. All1000partitions/predictions independently verified.

Primary source(s): https://europepmc.org/articles/PMC7294996

## Scientific limits

Completed qualified published-method reimplementation,not exact replay of conflicting source variants:comparative code uses defaults/finalCVmtry10. Published precomputed features/globalfeatureselection inherited. Refit percentile spread is not independent-targetCI. GFPLOSO0.294688 limits transfer.

This benchmark evaluates a model endpoint, not a complete design application.

## Captured protocol and execution evidence

The following files are the original execution snapshots under `results/`; they
record inputs, splits, model identity or independent verification where available.

- [independent_verification.json](../../results/benchmarks/007_RFcombined/Run-4_2026-11-12/independent_verification.json)
- [protocol.json](../../results/benchmarks/007_RFcombined/Run-4_2026-11-12/protocol.json)

[Completed report](../../results/benchmarks/007_RFcombined/Run-4_2026-11-12/REPORT.md) · [Registry](../BENCHMARK_RUNS.md)

Original execution recipe: [inference.R](../../scripts/benchmarks/007_RFcombined/inference.R).
