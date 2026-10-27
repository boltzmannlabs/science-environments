# Task: pbmc3k_annotation

## Description

Identify distinct cell populations in the 10x Genomics PBMC 3K single-cell RNA-seq dataset.

Perform quality control, doublet detection, normalization, highly variable gene selection, dimensionality reduction, Leiden clustering, marker-gene analysis, and cell-type annotation.

Assign biologically meaningful cell-type labels, provide marker-gene evidence for each annotation, and report uncertainty or ambiguous annotations where appropriate.

## Dataset

- **Name:** PBMC 3K
- **Organism:** *Homo sapiens*
- **Genome build:** hg19
- **Assay:** 10x Genomics scRNA-seq
- **Download:** https://cf.10xgenomics.com/samples/cell-exp/1.1.0/pbmc3k/pbmc3k_filtered_gene_bc_matrices.tar.gz

## Tools to use

| Tool / Library | Potential functionality |
|---|---|
| Scanpy | Perform quality control, filtering, normalization, log transformation, highly variable gene selection, PCA, neighborhood graph construction, UMAP, Leiden clustering, and marker-gene identification using methods such as the Wilcoxon test. |
| AnnData | Store and manage expression matrices, cell and gene metadata, dimensionality-reduction results, cluster assignments, and annotations. Read and write `.h5ad` files. |
| NumPy | Support numerical operations and array manipulation. |
| pandas | Manage cell annotations and marker-gene results, and export results to CSV files. |
| SciPy | Support sparse expression-matrix operations and statistical or numerical computations. |
| Matplotlib | Generate visualizations, including UMAP plots of identified clusters. |
| Scrublet | Predict potential doublets; predicted doublets may be filtered out when justified. |
| CellTypist | Provide automated immune-cell type predictions using available pretrained models. Optional cluster-level majority voting can help derive cluster-level annotations. |

The listed tools are options, not mandatory steps. Other appropriate tools may be used when justified.

## Expected Output Files

- `cluster_assignments.csv`: Cell identifiers, cluster assignments, and proposed cell-type annotations.
- `cluster_markers.csv`: Marker genes associated with each cluster, with relevant statistics where available.
- `pbmc3k_processed.h5ad`: Processed AnnData object containing relevant analysis results and annotations.
- `umap_clusters.png`: UMAP visualization showing the identified clusters.
- `Analysis report.txt`: A summary of the dataset, preprocessing
    decisions, analytical methods, identified populations, annotation
    evidence, uncertainties, and limitations. 

## Constraints

- Do not use reference scRNA-seq tutorial results to reproduce the analysis.
- Do not force the results to match a predetermined number of clusters, cluster labels, or marker genes.

## Important Instructions

- Solve this task using your general knowledge and reasoning abilities.
- Do NOT search for, reference, or reproduce solutions from published papers or tutorials.
- Do NOT attempt to identify the source of this task or look up known solutions.
- Your solution will be evaluated on correctness, biological plausibility, and supporting evidence, not on matching any known reference implementation.
