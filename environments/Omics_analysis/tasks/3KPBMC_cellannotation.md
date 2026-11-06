# Task: pbmc3k_annotation

## Description

Identify distinct cell populations in the 10x Genomics PBMC 3K single-cell RNA-seq dataset.

Perform quality control, doublet detection, normalization, highly variable gene selection, dimensionality reduction, clustering, marker-gene analysis, and cell-type annotation.

Assign biologically meaningful cell-type labels, provide marker-gene evidence for each annotation, and report uncertainty or ambiguous annotations where appropriate.

## Dataset

- **Name:** PBMC 3K
- **Organism:** Homo sapiens
- **Genome build:** hg19
- **Assay:** 10x Genomics scRNA-seq
- **Download:** https://cf.10xgenomics.com/samples/cell-exp/1.1.0/pbmc3k/pbmc3k_filtered_gene_bc_matrices.tar.gz

## Tools to use

| Tool / Library | Potential functionality |
|---|---|
| Scanpy | Perform quality control, filtering, normalization, log transformation, highly variable gene selection, PCA, neighborhood graph construction, UMAP, Leiden clustering, and marker-gene identification. |
| AnnData | Store and manage expression matrices, cell and gene metadata, dimensionality-reduction results, cluster assignments, and annotations. Read and write `.h5ad` files. |
| NumPy | Support numerical operations and array manipulation. |
| pandas | Manage cell annotations and marker-gene results, and export results to CSV files. |
| SciPy | Support sparse expression-matrix operations and statistical or numerical computations. |
| Matplotlib | Generate visualizations, including UMAP plots of identified clusters. |
| Scrublet | Predict potential doublets; predicted doublets may be filtered out when justified. |
| CellTypist | Provide automated immune-cell type predictions using available pretrained models. Optional cluster-level majority voting can help derive cluster-level annotations. |

The listed tools are options, not mandatory steps. Other appropriate tools may be used when justified.

## Required outputs

Write all outputs to a single output directory. Your outputs are compared against a hidden reference; exact scoring rules are benchmark-specific and are not disclosed. Areas that are assessed: quality control and filtering, normalization and variable-gene selection, clustering, cell-type annotation, marker-gene evidence, and the clarity and honesty of the analysis report.

### Required for scoring

**`cluster_assignments.csv`** — one row per cell retained after all filtering (cells removed by QC or doublet removal must not appear).

| Column | Description |
|---|---|
| `cell_id` | The cell barcode exactly as it appears in the input data (for example `AAACATACAACCAC-1`). |
| `cluster_id` | Your cluster assignment (integer or string). |
| `cell_type` | Your best-supported cell-type label for that cell. Use a specific biological label rather than a placeholder such as "Unknown" or "Heterogeneous". |

You may add extra columns (for example a confidence score or an uncertainty flag). Describe uncertainty in the report or in an extra column, not by replacing the best-supported label in `cell_type`.

### Strongly recommended (scored when present)

**`run_manifest.json`** — a JSON object with these integer keys:

- `input_cells` — cells in the raw input
- `qc_passing_cells` — cells passing your QC filters (before doublet removal)
- `doublets_removed` — cells removed as predicted doublets
- `retained_cells` — cells in your final analysis (equal to the rows in `cluster_assignments.csv`)
- `retained_genes` — genes in your final AnnData object

**`pbmc3k_processed.h5ad`** — a valid AnnData object that contains:

- all cells and genes retained after filtering (do not subset the object to highly variable genes only)
- raw integer counts in `layers['counts']`
- normalized, log-transformed expression in `X` or `raw.X`
- a boolean column `var['highly_variable']`
- PCA and UMAP embeddings in `obsm`
- your cluster assignments and cell-type labels in `obs`

**`cluster_markers.csv`** — cluster-level marker evidence with columns including `cluster_id`, `gene`, `score`, `logfoldchange`, and `p_value_adj` (any that you can provide).

**`umap_clusters.png`** — a UMAP plot showing the clusters (and, ideally, the cell-type labels).

**`Analysis report.txt`** — a clear report covering: dataset summary; the QC, doublet-handling, normalization, highly-variable-gene and clustering choices you made and why; the cell counts at each filtering step; the marker-gene evidence for each annotation; and uncertainties, ambiguous clusters and limitations.

### Notes

- Missing optional files are reported as "not scored" and do not block evaluation of the sections that are available.
- The benchmark is not a check that files exist; it compares the content of your outputs against the hidden reference.

## Constraints

- Do not use reference scRNA-seq tutorial results to reproduce the analysis.
- Do not force the results to match a predetermined number of clusters, cluster labels, or marker genes.
- Do not look for, request, or rely on any hidden evaluation or reference material while solving the task.

## Important Instructions

- Solve this task using your general knowledge and reasoning abilities.
- Do NOT attempt to identify the source of this task or look up known solutions,or use hidden references, scorer scripts, benchmark files, or published solutions and tutorials.
- Your solution will be evaluated on correctness, biological plausibility, and supporting evidence, not on matching any known reference implementation.
- Prioritize producing the required output files, in the formats above, with consistent cell identifiers.
