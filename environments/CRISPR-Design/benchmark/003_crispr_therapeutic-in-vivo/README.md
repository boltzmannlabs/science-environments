# Task 003: crispr therapeutic in vivo — benchmark evidence

[Task definition](../../tasks/003_crispr_therapeutic-in-vivo.md) · [Benchmark registry](../BENCHMARK_RUNS.md)

The evaluations below support this task at the component level. They do not
establish full application or experimental validation. Shared evaluations reference
the same execution records and are not independent task replications.

| Evaluation | Definition and limitations | Completed report |
| --- | --- | --- |
| CFD2016 experimentally assayed specificity | [Evaluation definition](../003_crispr_therapeutic-in-vivo/README.md#evaluation-003) | [Report](../../results/benchmarks/003_CFD2016/Run-4_2026-11-12/REPORT.md) |

## Evaluation 003

**CFD2016 experimentally assayed specificity**

### Evaluation definition

Native WTSpCas9 CFD2016 scores joined to1684explicitly assayed cellular sites:108positive,1576negative across9guides;correctedindel>=0.1%,3annotatedbulges excluded.

Primary source(s): Study PMID28459459; curated data https://ccsm.uth.edu/CRISPRoffT/

### Scientific limits

Negatives mean below the assay threshold in this condition, not universal noncleavage. Nominal0.1%AmpliSeq sensitivity, no individual-site read-depthLoD. Recall@500saturates due to panel exhaustion and is not genomewide recall. No variant/haplotype/SV evaluation.

This benchmark evaluates a model endpoint, not a complete design application.

### Captured protocol and execution evidence

The following files are the original execution snapshots under `results/`; they
record inputs, splits, model identity or independent verification where available.

- [metrics.json](../../results/benchmarks/003_CFD2016/Run-4_2026-11-12/metrics.json)
- [protocol.json](../../results/benchmarks/003_CFD2016/Run-4_2026-11-12/protocol.json)

[Completed report](../../results/benchmarks/003_CFD2016/Run-4_2026-11-12/REPORT.md) · [Registry](../BENCHMARK_RUNS.md)

Original execution recipe: [inference.R](../../scripts/benchmarks/003_CFD2016/inference.R).
