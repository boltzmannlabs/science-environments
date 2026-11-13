# Task: 06_myeloid_progenitor_lineages

## Description

Characterize the transcriptional heterogeneity of mouse bone marrow myeloid progenitor cells in a single-cell RNA-seq dataset.

Identify distinct progenitor subpopulations, determine the differentiation fates they are transcriptionally primed towards, identify marker genes for each subpopulation, and describe the relationships between them (for example, branches or trajectories). Report uncertainty and limitations.

## Dataset

- **Name:** Bone marrow myeloid progenitors, single-cell RNA-seq
- **Organism:** *Mus musculus*
- **Assay:** UMI-based single-cell RNA-seq (Illumina NextSeq 500), sequenced in several batches
- **Accession:** GSE72857 (NCBI GEO)
- **Download:** https://www.ncbi.nlm.nih.gov/geo/query/acc.cgi?acc=GSE72857

## Input

Obtain the data yourself from the repository above. Inspect the supplementary files, including the count table and the file that maps cells to samples, before analysis. Account for the batch structure of the data and for quality control of cells and genes, and describe your choices in the report.

## Tools to use

| Tool / Library | Potential functionality |
|---|---|
| Scanpy | Quality control, normalization, dimensionality reduction, clustering, marker-gene analysis, and trajectory analysis. |
| AnnData | Store expression matrices and cell metadata. |
| pandas / NumPy / SciPy | Data handling and statistics. |
| scikit-learn | Dimensionality reduction and clustering utilities. |
| Matplotlib | Visualizations. |

The listed tools are options, not mandatory steps. Other appropriate tools may be used when justified.

## Required outputs

Write all outputs to a single output directory.

**`cluster_assignments.csv`** has one row for every cell retained after quality control.

| Column | Description |
|---|---|
| `cell_id` | The cell identifier exactly as it appears in the input. |
| `cluster_id` | Your cluster assignment (integer or string). |
| `cell_type` | Your label for the subpopulation, supported by marker genes (for example a progenitor type or the differentiation fate it is primed towards). |

**`cluster_markers.csv`** has marker evidence for each cluster, with columns `cluster_id`, `gene`, `score`, `log2_fold_change`, and `adj_p_value`.

**`summary.json`** has these keys:

- `cells_input` and `cells_retained`: number of cells in the input and after quality control
- `n_clusters`: number of clusters
- `fates_identified`: list of the differentiation fates or lineages you identified
- `cluster_relationships`: a short description of which clusters or lineages are related (for example, which clusters lead to which fates)
- `model`: a short description of the methods you used
- `software_used`: the software and package versions you used, including any packages you installed

## Recommended outputs 

- **`pseudotime.csv`**: one row per cell with `cell_id`, `pseudotime`, and, if applicable, the branch or lineage the cell belongs to.
- **`Analysis report.txt`**: dataset summary; quality control and batch handling; normalization, clustering, and trajectory methods and parameters; the evidence for each subpopulation and fate; and uncertainties and limitations.
- **`umap_clusters.png`**: a plot showing the clusters and, ideally, the fate labels.

## Evaluation

Your outputs are compared against a hidden reference. Exact scoring rules are benchmark-specific and are not disclosed. Missing optional files are reported as "not scored" and do not block evaluation of the sections that are available.

Areas assessed: identification of the progenitor subpopulations and differentiation fates, marker-gene evidence, handling of batches and quality control, and the clarity and honesty of the analysis report.

## Constraints

- Do not use reference tutorial results or published results to reproduce the analysis.
- Do not force the results to match a predetermined number of clusters, fates, or marker genes.
- Do not look for, request, or rely on any hidden evaluation or reference material while solving the task.
- Use only the public task description and the data from the source named above.

## Important Instructions

- Solve this task using your general knowledge and reasoning abilities.
- Do NOT search for, reference, or reproduce solutions from published papers or tutorials.
- Do NOT attempt to identify the source of this task or look up known solutions.
- Your solution will be evaluated on correctness, biological plausibility, and supporting evidence, not on matching any known reference implementation.
- Prioritize producing the required output files, in the formats above, with consistent cell identifiers.
