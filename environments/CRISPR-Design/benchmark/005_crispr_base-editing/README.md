# Task 005: crispr base editing — benchmark evidence

[Task definition](../../tasks/005_crispr_base-editing.md) · [Benchmark registry](../BENCHMARK_RUNS.md)

The evaluations below support this task at the component level. They do not
establish full application or experimental validation. Shared evaluations reference
the same execution records and are not independent task replications.

| Evaluation | Definition and limitations | Completed report |
| --- | --- | --- |
| BE-Hive BE4 any-edit efficiency | [Evaluation definition](../005_crispr_base-editing/README.md#evaluation-004) | [Report](../../results/benchmarks/004_BEHive_BE4/Run-4_2026-11-12/REPORT.md) |

## Evaluation 004

**BE-Hive BE4 any-edit efficiency**

### Evaluation definition

Native released HEK293T/BE4 regressor;9975measured external-library any-edit efficiency labels;known training20mer/31nt contexts excluded. Source-used31nt feature encoding independently matched to native featurizer without fabricated flanks.

Primary source(s): https://europepmc.org/articles/PMC7384975

### Scientific limits

BE4,notBE4max. Target is normalizedlogit any-edit efficiency,not intended-edit purity or genotype distribution. Original internal tuning membership/whole-gene exclusion not fully available. Weak transfer performance is retained.

This benchmark evaluates a model endpoint, not a complete design application.

### Captured protocol and execution evidence

The following files are the original execution snapshots under `results/`; they
record inputs, splits, model identity or independent verification where available.

- [fresh_metric.json](../../results/benchmarks/004_BEHive_BE4/Run-4_2026-11-12/fresh_metric.json)
- [model_identity.json](../../results/benchmarks/004_BEHive_BE4/Run-4_2026-11-12/model_identity.json)
- [protocol.json](../../results/benchmarks/004_BEHive_BE4/Run-4_2026-11-12/protocol.json)

[Completed report](../../results/benchmarks/004_BEHive_BE4/Run-4_2026-11-12/REPORT.md) · [Registry](../BENCHMARK_RUNS.md)

Original execution recipe: [inference.py](../../scripts/benchmarks/004_BEHive_BE4/inference.py).
