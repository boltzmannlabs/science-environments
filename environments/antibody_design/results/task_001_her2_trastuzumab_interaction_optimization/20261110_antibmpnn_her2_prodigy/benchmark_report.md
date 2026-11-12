# Task-specific benchmark comparison

Task: `task_001_her2_trastuzumab_interaction_optimization`; run: `20261110_antibmpnn_her2_prodigy`.

Reference definition: [existing task-specific benchmark](../../../benchmark/monoclonal_antibody_design/task_001_her2_trastuzumab_interaction_optimization.md). The reference file on current `main` is retained unchanged.

| Record | Evidence |
| --- | --- |
| Executed results, methods and limitations | [Scientific report](report.md) |
| Metric-level comparison and comparison scope | [Comparison table](benchmark_comparison.csv) |
| Computed values and supporting outputs | [Metrics](metrics.json), [evidence](evidence/) |
| Actual tools, versions, settings and execution history | [Source execution](../../../src/task_001_her2_trastuzumab_interaction_optimization/runs/20261110_antibmpnn_her2_prodigy/execution.md), [provenance](../../../src/task_001_her2_trastuzumab_interaction_optimization/runs/20261110_antibmpnn_her2_prodigy/provenance.json) |

Scientific coverage: **partial**. Candidate Boltz2 downloads failed; approximate models rejected as binding-improvement evidence by the later audit.

This package retains existing calculations. No evaluator was run during arrangement. Values with incompatible constructs, atom selections, datasets, sampling or aggregation do not support an outperformance claim. Uncomputed values remain absent; the original report/table describes the missing inputs or evaluations. Historical numeric and mixed-format tables are retained with their original schemas rather than inventing precision or missing scores.
