# Omics Analysis

A benchmark environment for evaluating AI agent on practical omics data-analysis tasks.

Each task gives an AI agent a scientific objective, input data, permitted tools, required outputs, and task-specific evaluation criteria. Tasks are independent and may use different datasets, omics modalities, analytical methods, and biological questions.

## Available tasks

The repository currently includes four single-cell RNA-seq tasks based on the 10x Genomics PBMC3k dataset:

1. [PBMC3k quality control and filtering](tasks/01_pbmc3k_qc_filtering.md)
2. [PBMC3k clustering](tasks/02_pbmc3k_clustering.md)
3. [PBMC3k cluster-level cell-type annotation](tasks/03_pbmc3k_annotation.md)
4. [PBMC3k end-to-end cell-type annotation](tasks/04_3KPBMC_celltype_annotation.md)

These tasks cover quality control, filtering, normalization, clustering, marker-gene analysis, and cell-type annotation.

## Planned tasks

Five additional independent omics-analysis tasks are planned. They will not necessarily use PBMC3k data or follow the same workflow.

Each future task will be added with its own:

- Task specification
- Input and output requirements
- Evaluation criteria
- Benchmark references, where applicable
- Scoring logic
- Agent results, when available

The planned tasks are not yet included in this repository and are not currently available for execution or evaluation.

## How tasks are evaluated

An AI agent receives the public task instructions and the permitted input data. It must produce the outputs specified by the task.

Evaluation may consider:

- Whether required outputs are present and valid
- Correctness and completeness of the analysis
- Biological plausibility
- Marker- or feature-based evidence
- Handling of uncertainty and ambiguous results
- Reproducibility and provenance
- Agreement with task-specific benchmark criteria

The benchmark reference is a curated computational baseline, not necessarily biological ground truth. Agreement with a reference output should not be interpreted as proof of biological correctness.

## Repository structure

```text
.
├── ENVIRONMENT_SPEC.md        # Overall environment specification
├── tasks/                     # Instructions provided to AI agents
├── benchmark/                 # Evaluator-only references and scoring metadata
├── results/                   # Agent outputs and benchmark results
├── scripts/                   # Scoring and evaluation utilities
├── config/                    # Environment configuration
├── tests/                     # Repository tests
└── skills/                    # Agent workflow guidance
```

## Results and limitations

Agent outputs and benchmark results are stored under [`results/`](results/). Evaluator references and scoring metadata are stored under [`benchmark/`](benchmark/).

The current tasks use PBMC3k, so their results should not be interpreted as evidence of generalization to other tissues, organisms, technologies, or disease contexts. Some grading criteria are heuristic and may use keyword- or rule-based checks.

## Further documentation

- [Environment specification](ENVIRONMENT_SPEC.md)
- [Task specifications](tasks/)
- [Benchmark scorer documentation](scripts/pbmc3k_benchmark/scripts_pbmc3k_benchmark_README.md)
