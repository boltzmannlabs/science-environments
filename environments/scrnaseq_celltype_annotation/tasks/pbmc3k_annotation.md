# Task: pbmc3k_annotation

## Description

Assign cell-type labels to the clusters of PBMC 3K cells, with marker-gene evidence.

Provide biologically meaningful labels, report uncertainty or ambiguous annotations where appropriate, and avoid unsupported specificity.

## Dataset

- **Name:** PBMC 3K
- **Organism:** *Homo sapiens*
- **Genome build:** hg19
- **Assay:** 10x Genomics scRNA-seq

## Input

`input/pbmc3k_clustered.h5ad`: an AnnData object with raw integer counts in `layers['counts']`, normalized log-transformed expression in `X`, and cluster labels in `obs['cluster_id']`. Cluster identifiers are arbitrary and carry no biological meaning. Compute whatever marker evidence you need.

## Tools to use

| Tool / Library | Potential functionality |
|---|---|
| Scanpy | Inspect expression and marker genes per cluster, and plot gene expression on UMAP or dot plots. |
| AnnData | Read and write `.h5ad` files and store annotations. |
| pandas | Manage cluster annotations and marker evidence, and export results to CSV files. |
| CellTypist | Provide automated immune-cell type predictions using available pretrained models. Optional cluster-level majority voting can help derive cluster-level annotations. |
| Matplotlib | Generate visualizations, including UMAP plots of cell-type labels. |

The listed tools are options, not mandatory steps. Other appropriate tools may be used when justified.

## Required outputs

Write all outputs to a single output directory.

**`cluster_assignments.csv`** has one row for every cell in the input.

| Column | Description |
|---|---|
| `cell_id` | The cell identifier exactly as it appears in the input object. |
| `cluster_id` | The cluster identifier, as in the input. |
| `cell_type` | Your label for the cell. |
| `annotation_status` | `resolved`, `tentative`, or `unresolved`. |

Label rules:

- `cell_type` is a specific biological label supported by your evidence (for example a lineage or subtype name), not a placeholder.
- Use `annotation_status` = `resolved` when the evidence clearly supports the label, `tentative` when the label is the best-supported option but the evidence is ambiguous or conflicting, and `unresolved` when no label is adequately supported. For `unresolved`, set `cell_type` to `Unresolved`.
- Avoid unsupported specificity: prefer a broader label over a subtype you cannot justify.

## Recommended outputs (scored when present)

- **`cluster_annotation.csv`**: one row per cluster with columns `cluster_id`, `cell_type`, `annotation_status`, `supporting_markers` (gene symbols separated by `;`), and `evidence` (short text, including any conflicting evidence).
- **`Analysis report.txt`**: how you assigned labels, the evidence for each, and uncertainties and limitations.
- **`run_manifest.json`** with `seed`, `parameters`, and `versions`.

## Evaluation

Your outputs are compared against a hidden reference. Exact scoring rules are benchmark-specific and are not disclosed. Missing optional files are reported as "not scored" and do not block evaluation of the sections that are available.

Areas assessed: label correctness and appropriate specificity, marker-gene evidence for each label, honest handling of ambiguous populations, and consistency of cell identifiers.

## Constraints

- Do not use reference scRNA-seq tutorial results to reproduce the analysis.
- Do not force the results to match a predetermined number of clusters, cell-type labels, or marker genes.
- Do not look for, request, or rely on any hidden evaluation or reference material while solving the task.
- Use only the public task description, the provided input files and the installed environment.

## Important Instructions

- Solve this task using your general knowledge and reasoning abilities.
- Do NOT search for, reference, or reproduce solutions from published papers or tutorials.
- Do NOT attempt to identify the source of this task or look up known solutions.
- Your solution will be evaluated on correctness, biological plausibility, and supporting evidence, not on matching any known reference implementation.
- Prioritize producing the required output files, in the formats above, with consistent cell identifiers.
