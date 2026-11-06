# Task: pbmc3k_clustering

## Description

Cluster the PBMC 3K cells into groups of transcriptionally similar cells.

Perform dimensionality reduction, build a neighborhood graph, and cluster the cells. Do not assign cell-type labels in this task.

## Dataset

- **Name:** PBMC 3K
- **Organism:** *Homo sapiens*
- **Genome build:** hg19
- **Assay:** 10x Genomics scRNA-seq

## Input

`input/pbmc3k_normalized.h5ad`: an AnnData object with raw integer counts in `layers['counts']`, normalized log-transformed expression in `X`, and a boolean `var['highly_variable']` column. The cells have already passed quality control.

## Tools to use

| Tool / Library | Potential functionality |
|---|---|
| Scanpy | Perform dimensionality reduction, neighborhood graph construction, UMAP and Leiden clustering. |
| AnnData | Read and write `.h5ad` files and store embeddings and cluster assignments. |
| NumPy | Support numerical operations and array manipulation. |
| pandas | Manage cluster assignments and export results to CSV files. |
| Matplotlib | Generate UMAP plots of the clusters. |

The listed tools are options, not mandatory steps. Other appropriate tools may be used when justified.

## Required outputs

Write all outputs to a single output directory.

**`cluster_assignments.csv`** has one row for every cell in the input.

| Column | Description |
|---|---|
| `cell_id` | The cell identifier exactly as it appears in the input object. |
| `cluster_id` | Your cluster assignment (integer or string). |

## Recommended outputs (scored when present)

- **`pbmc3k_clustered.h5ad`**: the object with your embeddings (for example PCA and UMAP) and cluster labels.
- **`umap_clusters.png`**: a UMAP plot showing the clusters.
- **`Analysis report.txt`**: the dimensionality-reduction, graph, and clustering methods and parameters, and how you chose the clustering resolution.
- **`run_manifest.json`** with `seed`, `parameters`, and `versions`.

## Evaluation

Your outputs are compared against a hidden reference. Exact scoring rules are benchmark-specific and are not disclosed. Missing optional files are reported as "not scored" and do not block evaluation of the sections that are available.

Areas assessed: valid and complete cluster assignments, whether clusters correspond to distinct populations, whether small populations are resolved instead of absorbed into larger clusters, and justified analytical choices.

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
