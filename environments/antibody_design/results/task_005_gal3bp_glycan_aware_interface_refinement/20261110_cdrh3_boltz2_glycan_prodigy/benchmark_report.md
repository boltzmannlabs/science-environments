# Task-specific benchmark comparison

Task: `task_005_gal3bp_glycan_aware_interface_refinement`; run: `20261110_cdrh3_boltz2_glycan_prodigy`.

Reference definition: [existing task-specific benchmark](../../../benchmark/monoclonal_antibody_design/task_005_gal3bp_glycan_aware_interface_refinement.md). The reference file on current `main` is retained unchanged.

| Record | Evidence |
| --- | --- |
| Executed results, methods and limitations | [Scientific report](report.md) |
| Metric-level comparison and comparison scope | [Comparison table](benchmark_comparison.csv) |
| Computed values and supporting outputs | [Metrics](metrics.json), [evidence](evidence/) |
| Actual tools, versions, settings and execution history | [Source execution](../../../src/task_005_gal3bp_glycan_aware_interface_refinement/runs/20261110_cdrh3_boltz2_glycan_prodigy/execution.md), [provenance](../../../src/task_005_gal3bp_glycan_aware_interface_refinement/runs/20261110_cdrh3_boltz2_glycan_prodigy/provenance.json) |

Scientific coverage: **partial**. Heated MD and developability pending; original glycan SASA invalidated by retained cross-check.

This package retains existing calculations. No evaluator was run during arrangement. Values with incompatible constructs, atom selections, datasets, sampling or aggregation do not support an outperformance claim. Uncomputed values remain absent; the original report/table describes the missing inputs or evaluations. Historical numeric and mixed-format tables are retained with their original schemas rather than inventing precision or missing scores.
