# Task-specific benchmark comparison

Task: `task_003_pd1_framework_guided_cdr_design`; run: `20261110_local_proteinmpnn_boltz2`.

Reference definition: [existing task-specific benchmark](../../../benchmark/monoclonal_antibody_design/task_003_pd1_framework_guided_cdr_design.md). The reference file on current `main` is retained unchanged.

| Record | Evidence |
| --- | --- |
| Executed results, methods and limitations | [Scientific report](report.md) |
| Metric-level comparison and comparison scope | [Comparison table](benchmark_comparison.csv) |
| Computed values and supporting outputs | [Metrics](metrics.json), [evidence](evidence/) |
| Actual tools, versions, settings and execution history | [Source execution](../../../src/task_003_pd1_framework_guided_cdr_design/runs/20261110_local_proteinmpnn_boltz2/execution.md), [provenance](../../../src/task_003_pd1_framework_guided_cdr_design/runs/20261110_local_proteinmpnn_boltz2/provenance.json) |

Scientific coverage: **partial**. CDR-H3-only local comparison; original labelled screening panels unavailable.

This package retains existing calculations. No evaluator was run during arrangement. Values with incompatible constructs, atom selections, datasets, sampling or aggregation do not support an outperformance claim. Uncomputed values remain absent; the original report/table describes the missing inputs or evaluations. Historical numeric and mixed-format tables are retained with their original schemas rather than inventing precision or missing scores.
