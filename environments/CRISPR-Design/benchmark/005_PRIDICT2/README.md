# PRIDICT2.0 published grouped OOF outcomes

## Evaluation definition

Original Library-Diverse group-fold assignments,matching cell heads and missing-label exclusions;two source model families averaged within the single held-out fold only. Original workbook fold IDs independently matched with zero mismatches.

Primary source(s): https://europepmc.org/articles/PMC7617539

## Scientific limits

Complete base-pretraining library overlap not audited. Intended and unintended edit fractions are separate endpoints; unintended-edit prediction is not purity validation. No PE3nick-design or all-editor transfer claim.

This benchmark evaluates a model endpoint, not a complete design application.

## Captured protocol and execution evidence

The following files are the original execution snapshots under `results/`; they
record inputs, splits, model identity or independent verification where available.

- [fold_identity.json](../../results/benchmarks/005_PRIDICT2/Run-4_2026-11-12/fold_identity.json)
- [protocol.json](../../results/benchmarks/005_PRIDICT2/Run-4_2026-11-12/protocol.json)
- [published_split_concordance.json](../../results/benchmarks/005_PRIDICT2/Run-4_2026-11-12/published_split_concordance.json)

[Completed report](../../results/benchmarks/005_PRIDICT2/Run-4_2026-11-12/REPORT.md) · [Registry](../BENCHMARK_RUNS.md)

Original execution recipe: [inference.py](../../scripts/benchmarks/005_PRIDICT2/inference.py).
