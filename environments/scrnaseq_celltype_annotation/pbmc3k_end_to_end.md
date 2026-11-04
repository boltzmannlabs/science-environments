# Task: pbmc3k_end_to_end

## Description

Identify distinct cell populations in the 10x Genomics PBMC 3K single-cell RNA-seq dataset.

Perform quality control, doublet detection, normalization, highly variable gene selection, dimensionality reduction, clustering, marker-gene analysis, and cell-type annotation.

Assign biologically meaningful cell-type labels, provide marker-gene evidence for each annotation, and report uncertainty or ambiguous annotations where appropriate.

## Dataset

- **Name:** PBMC 3K
- **Organism:** *Homo sapiens*
- **Genome build:** hg19
- **Assay:** 10x Genomics scRNA-seq
- **Download:** https://cf.10xgenomics.com/samples/cell-exp/1.1.0/pbmc3k/pbmc3k_filtered_gene_bc_matrices.tar.gz

## Input

Raw 10x Genomics matrix from the download link above. Inspect it before analysis.

## Tools to use

| Tool / Library | Potential functionality |
|---|---|
| Scanpy | Quality control, filtering, normalization, log transformation, highly variable gene selection, PCA, neighborhood graph construction, UMAP, Leiden clustering, and marker-gene identification. |
| AnnData | Store expression matrices, cell and gene metadata, embeddings, cluster assignments, and annotations. Read and write `.h5ad` files. |
| NumPy / SciPy | Numerical operations and sparse expression-matrix computations. |
| pandas | Manage tables and export results to CSV files. |
| Matplotlib | Visualizations, including UMAP plots. |
| Scrublet | Predict potential doublets; predicted doublets may be filtered out when justified. |
| CellTypist | Automated immune-cell type predictions using available pretrained models. Optional cluster-level majority voting can help derive cluster-level annotations. |

The listed tools are options, not mandatory steps. Other appropriate tools may be used when justified.

## Required outputs

Write all outputs to a single output directory.

**`cluster_assignments.csv`** has one row for every cell retained after all filtering (cells removed by quality control or doublet removal must not appear).

| Column | Description |
|---|---|
| `cell_id` | The cell barcode exactly as it appears in the input (for example `AAACATACAACCAC-1`). |
| `cluster_id` | Your cluster assignment (integer or string). |
| `cell_type` | Your label for the cell. |
| `annotation_status` | `resolved`, `tentative`, or `unresolved`. |

Label rules:

- `cell_type` is a specific biological label supported by your evidence (for example a lineage or subtype name), not a placeholder.
- Use `annotation_status` = `resolved` when the evidence clearly supports the label, `tentative` when the label is the best-supported option but the evidence is ambiguous or conflicting, and `unresolved` when no label is adequately supported. For `unresolved`, set `cell_type` to `Unresolved`.
- Avoid unsupported specificity: prefer a broader label over a subtype you cannot justify.

You may add extra columns (for example a confidence score).

## Recommended outputs (scored when present)

- **`run_manifest.json`**: a JSON object with integer keys `input_cells`, `qc_passing_cells` (cells passing QC filters, before doublet removal), `doublets_removed`, `retained_cells` (rows in `cluster_assignments.csv`), and `retained_genes` (genes in your final object). In `run_manifest.json` you may also record `seed`, `parameters`, and `versions` (software and annotation-resource versions) so the run can be reproduced.
- **`pbmc3k_processed.h5ad`**: a valid AnnData object with all retained cells and genes (not subset to highly variable genes), raw integer counts in `layers['counts']`, normalized log-transformed expression in `X` or `raw.X`, a boolean `var['highly_variable']`, PCA and UMAP embeddings in `obsm`, and your cluster assignments and labels in `obs`.
- **`cluster_markers.csv`**: cluster-level marker evidence with columns including `cluster_id` and `gene`, and, where available, `score`, `logfoldchange`, and `p_value_adj`.
- **`umap_clusters.png`**: a UMAP plot showing the clusters (and, ideally, the cell-type labels).
- **`Analysis report.txt`**: dataset summary; the QC, doublet-handling, normalization, highly-variable-gene, and clustering choices you made and why; cell counts at each filtering step; marker-gene evidence for each annotation; and uncertainties, ambiguous clusters, and limitations.

## Evaluation

Your outputs are compared against a hidden reference. Exact scoring rules are benchmark-specific and are not disclosed. Missing optional files are reported as "not scored" and do not block evaluation of the sections that are available.

Areas assessed: quality control and filtering, normalization and variable-gene selection, clustering, cell-type annotation, marker-gene evidence, and the clarity and honesty of the analysis report.

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
