# task_001_her2_trastuzumab_interaction_optimization

## Latest independent benchmark audit

[20261111_ref15_benchmark_audit — comprehensive report](20261111_ref15_benchmark_audit/report.md)

The previous approximate-coordinate Prodigy ranking is **not validated binding-improvement evidence**: the audit found missing backbone oxygen atoms, a mismatched HER2 construct and an AB_13 edit-mask discrepancy. New ABodyBuilder2/PyMOL/OpenMM evaluations and rescored published controls are available in the audit run. Exact REF15 comparison remains blocked; no benchmark superiority is established.

## Historical design run

Canonical scientific run: `20261110_antibmpnn_her2_prodigy`.

- [Scientific report](20261110_antibmpnn_her2_prodigy/report.md)
- [Candidate inventory](20261110_antibmpnn_her2_prodigy/candidates.csv): 20 rows, with controls identified in the table.
- [Selection table](20261110_antibmpnn_her2_prodigy/shortlist.csv): 5 selections; consult rank/status fields for their interpretation.
- [Designed sequences](20261110_antibmpnn_her2_prodigy/designed_sequences.fasta): 10 records; coverage is described in the report.
- [Metrics](20261110_antibmpnn_her2_prodigy/metrics.json)
- [Benchmark comparison](20261110_antibmpnn_her2_prodigy/benchmark_comparison.csv)
- [Structures](20261110_antibmpnn_her2_prodigy/structures/)
- [Packaging validation](20261110_antibmpnn_her2_prodigy/evidence/validation.json)
- [Source execution](../../src/task_001_her2_trastuzumab_interaction_optimization/runs/20261110_antibmpnn_her2_prodigy/execution.md)

Scientific measurements were retained during normalization; this packaging pass did not rerun design, prediction or scoring.
