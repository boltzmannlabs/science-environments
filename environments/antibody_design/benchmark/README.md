# Antibody Design Benchmarks

Benchmark documents are organized by task family and task ID. The [monoclonal benchmark catalog](monoclonal_antibody_design/README.md) links to the reference documents and calculated comparisons.

```text
benchmark/
├── README.md
└── monoclonal_antibody_design/
    ├── README.md
    └── <task_id>/
        ├── reference.md
        ├── comparison.md
        └── figures/
            ├── results_comparison.png
            └── workflow_results.png
```

Each task folder contains `reference.md`, which describes the published source, benchmark context, metrics and reference values. Folders with calculated results also contain `comparison.md` and the PNG figures embedded in that document. Comparisons explain the measured endpoints, comparator and sample scope alongside the numerical tables.

Task identifiers match the [task definitions](../tasks/monoclonal_antibody_design/README.md). Per-run tables and native scientific outputs are described in the [results guide](../results/README.md).
