# Task 006: crispr prime editing — benchmark evidence

[Task definition](../../tasks/006_crispr_prime-editing.md) · [Benchmark registry](../BENCHMARK_RUNS.md)

The evaluations below support this task at the component level. They do not
establish full application or experimental validation. Shared evaluations reference
the same execution records and are not independent task replications.

| Evaluation | Definition and limitations | Completed report |
| --- | --- | --- |
| PRIDICT2.0 published grouped OOF outcomes | [Evaluation definition](../006_crispr_prime-editing/README.md#evaluation-005) | [Report](../../results/benchmarks/005_PRIDICT2/Run-4_2026-11-12/REPORT.md) |
| DeepPrime base fixed test | [Evaluation definition](../006_crispr_prime-editing/README.md#evaluation-006) | [Report](../../results/benchmarks/006_DeepPrime_PE2/Run-4_2026-11-12/REPORT.md) |

## Evaluation 005

**PRIDICT2.0 published grouped OOF outcomes**

### Evaluation definition

Original Library-Diverse group-fold assignments,matching cell heads and missing-label exclusions;two source model families averaged within the single held-out fold only. Original workbook fold IDs independently matched with zero mismatches.

Primary source(s): https://europepmc.org/articles/PMC7617539

### Scientific limits

Complete base-pretraining library overlap not audited. Intended and unintended edit fractions are separate endpoints; unintended-edit prediction is not purity validation. No PE3nick-design or all-editor transfer claim.

This benchmark evaluates a model endpoint, not a complete design application.

### Captured protocol and execution evidence

The following files are the original execution snapshots under `results/`; they
record inputs, splits, model identity or independent verification where available.

- [fold_identity.json](../../results/benchmarks/005_PRIDICT2/Run-4_2026-11-12/fold_identity.json)
- [protocol.json](../../results/benchmarks/005_PRIDICT2/Run-4_2026-11-12/protocol.json)
- [published_split_concordance.json](../../results/benchmarks/005_PRIDICT2/Run-4_2026-11-12/published_split_concordance.json)

[Completed report](../../results/benchmarks/005_PRIDICT2/Run-4_2026-11-12/REPORT.md) · [Registry](../BENCHMARK_RUNS.md)

Original execution recipe: [inference.py](../../scripts/benchmarks/005_PRIDICT2/inference.py).

## Evaluation 006

**DeepPrime base fixed test**

### Evaluation definition

OriginalHEK293T/PE2/conventional-scaffold fixed test n28883against259910trainingrows;zero exact-input and74nt-target overlaps. Native74nt/24numeric inputs,source mean/std and5checkpoint ensemble.

Primary source(s): https://github.com/hkimlab/DeepPrime

### Scientific limits

Only this matched editor/cell/scaffold condition evaluated;author-provided upstreamDeepSpCas9 feature retained,not substituted. No unintended-edit or purity conclusion.

This benchmark evaluates a model endpoint, not a complete design application.

### Captured protocol and execution evidence

The following files are the original execution snapshots under `results/`; they
record inputs, splits, model identity or independent verification where available.

- [model_identity.json](../../results/benchmarks/006_DeepPrime_PE2/Run-4_2026-11-12/model_identity.json)
- [native_metrics.json](../../results/benchmarks/006_DeepPrime_PE2/Run-4_2026-11-12/native_metrics.json)
- [protocol.json](../../results/benchmarks/006_DeepPrime_PE2/Run-4_2026-11-12/protocol.json)

[Completed report](../../results/benchmarks/006_DeepPrime_PE2/Run-4_2026-11-12/REPORT.md) · [Registry](../BENCHMARK_RUNS.md)

Original execution recipe: [inference.py](../../scripts/benchmarks/006_DeepPrime_PE2/inference.py).
