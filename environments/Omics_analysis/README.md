# Omics Analysis

A benchmark environment for evaluating AI agents on practical omics data-analysis tasks. Each task defines a scientific objective, dataset and input instructions, required outputs, constraints, and task-specific evaluation criteria. Tasks are independent and span multiple datasets and analysis types.

## Available tasks

The repository currently contains eight task specifications:

| # | Task | Data and analysis |
|---|---|---|
| 01 | [PBMC3k quality control and filtering](tasks/01_pbmc3k_qc_filtering.md) | Human PBMC single-cell RNA-seq; assess cell quality and filter cells. |
| 02 | [PBMC3k clustering](tasks/02_pbmc3k_clustering.md) | Human PBMC single-cell RNA-seq; cluster cells and characterize the result. |
| 03 | [PBMC3k cluster-level cell-type annotation](tasks/03_pbmc3k_annotation.md) | Human PBMC single-cell RNA-seq; identify cluster markers and assign cell types. |
| 04 | [PBMC3k end-to-end cell-type annotation](tasks/04_3KPBMC_celltype_annotation.md) | Human PBMC single-cell RNA-seq; perform an end-to-end clustering and annotation workflow. |
| 05 | [Single-cell stimulation response](tasks/05_single_cell_stimulation_response.md) | Human PBMC single-cell RNA-seq; compare control and cytokine-stimulated cells, accounting for donors. |
| 06 | [Myeloid progenitor lineages](tasks/06_myeloid_progenitor_lineages.md) | Mouse bone-marrow single-cell RNA-seq; identify progenitor populations, markers, and lineage relationships. |
| 07 | [Melanoma tumor ecosystem](tasks/07_melanoma_tumor_ecosystem.md) | Human metastatic melanoma single-cell RNA-seq; characterize cell populations and malignant-cell programs across tumors. |
| 08 | [DLPFC spatial domain identification](tasks/08_dlpfc_spatial_domain_identification/08_dlpfc_spatial_domain_identification.md) | Human dorsolateral prefrontal cortex Visium data; identify spatially coherent expression domains. |

Tasks 01 and 04–07 identify their source data in their specifications. Tasks 02 and 03 expect prepared AnnData inputs described in their specifications; those input files are not checked into this repository. Task 08 includes its agent-accessible AnnData input at `tasks/08_dlpfc_spatial_domain_identification/DLPFC_151673_agent_input.h5ad`.

## How tasks are evaluated

Each task describes its required outputs and evaluation criteria. Depending on the task, evaluation may consider whether outputs are present and valid, analytical and biological reasoning, evidence for conclusions, identifier consistency, and reproducibility. Some tasks include reference-based or heuristic scoring; the task specification and benchmark materials define the applicable criteria.

Benchmark references are computational or curated baselines, not necessarily biological ground truth. Agreement with a reference should not be interpreted as proof of biological correctness. Results from these tasks do not establish generalization to other datasets, tissues, organisms, technologies, or conditions.

## Repository structure

```text
.
├── ENVIRONMENT_SPEC.md        # Shared environment principles and task model
├── STATUS.md                  # Environment status notes
├── tasks/                     # Agent-facing task specifications and task 08 input
├── benchmark/                 # Evaluation references, methods, and scoring data (not task inputs)
├── results/                   # Existing task outputs and analysis reports
├── scripts/                   # Benchmark scorers and task comparison utilities
├── config/                    # Configuration directory (currently empty)
└── tests/                     # Test directory (currently empty)
```

The `benchmark/` directory contains evaluation reference material, including hidden labels; do not use it when solving the tasks. The PBMC3k scorer documentation is in [scripts/pbmc3k_benchmark/scripts_pbmc3k_benchmark_README.md](scripts/pbmc3k_benchmark/scripts_pbmc3k_benchmark_README.md). Each task's specification is authoritative for its inputs, constraints, required outputs, and evaluation procedure.

The `results/` folders contain checked-in analysis artifacts for all eight tasks.

For tasks 05–08, results are organized into two runs:

- `run_1` — GPT-6-Sol
- `run_2` — discoveryrsi

## Further documentation

- [Environment specification](ENVIRONMENT_SPEC.md)
- [Task specifications](tasks/)
- Benchmark references and scoring data are evaluator-only; see `benchmark/` when working on evaluation.
- [Existing results](results/)
