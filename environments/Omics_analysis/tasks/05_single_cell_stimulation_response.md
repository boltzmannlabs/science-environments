# Task: 05_ single_cell_stimulation_response

## Description

Characterize how human blood immune cells respond to a cytokine stimulation in a single-cell RNA-seq experiment.

Identify the genes that are induced or repressed by the stimulation, both overall and within the major cell types, and describe how the response differs between cell types. Account for the experimental design (multiple donors) and report the limitations of your analysis.

## Dataset

- **Name:** Peripheral blood mononuclear cells (PBMC), control versus cytokine-stimulated
- **Organism:** *Homo sapiens*
- **Assay:** 10x Genomics scRNA-seq (Illumina HiSeq 2500)
- **Accession:** GSE96583 (NCBI GEO)
- **Download:** https://www.ncbi.nlm.nih.gov/geo/query/acc.cgi?acc=GSE96583
- **Design:** cells from several donors were pooled, split into a control condition and a stimulated condition, and sequenced

## Input

Obtain the data yourself from the repository above. The series contains more than one experiment; use the experiment that compares control and stimulated cells. Inspect the available count matrices and per-cell metadata before analysis. If the repository provides per-cell labels (for example donor, condition, cell type, or doublet status), you may use them, but state in your report which labels you used and why.

## Tools to use

| Tool / Library | Potential functionality |
|---|---|
| Scanpy | Read count matrices, quality control, normalization, clustering, and cell-type marker analysis. |
| AnnData | Store expression matrices and cell metadata. |
| pandas / NumPy / SciPy | Data handling, aggregation, and statistics. |
| PyDESeq2 | Differential expression analysis of count data, including pseudobulk designs. |
| Matplotlib | Visualizations. |

The listed tools are options, not mandatory steps. Other appropriate tools may be used when justified.

## Required outputs

Write all outputs to a single output directory.

**`de_results.csv`** has one row for every gene and cell type you tested.

| Column | Description |
|---|---|
| `gene` | Gene symbol, exactly as it appears in the input. |
| `cell_type` | The cell type tested (use `all_cells` for a comparison across all cells). |
| `log2_fold_change` | log2 fold change, stimulated relative to control (positive means higher in stimulated cells). |
| `p_value` | Unadjusted p-value. |
| `adj_p_value` | Multiple-testing-adjusted p-value. |

**`summary.json`** has these keys:

- `cell_types_analyzed`: list of the cell types you tested
- `n_significant_per_cell_type`: for each cell type, the number of genes with `adj_p_value` < 0.05 and absolute `log2_fold_change` > 1
- `top_induced_genes`: the twenty genes with the strongest significant increase in stimulated cells in the `all_cells` comparison (gene symbols)
- `top_repressed_genes`: the twenty genes with the strongest significant decrease in the same comparison
- `data_used`: which files and per-cell labels you used
- `model`: a short description of the statistical design you used
- `software_used`: the software and package versions you used, including any packages you installed

## Recommended outputs 

- **`Analysis report.txt`**: dataset summary; quality control, doublet handling, normalization, and cell-type labels; how you handled donors and replicates; the model and its parameters; main findings; and uncertainties and limitations.
- **`qc_plots.png`** and **`volcano_plot.png`**: a sample-level plot and a volcano plot of the differential expression results.

## Evaluation

Your outputs are compared against a hidden reference. Exact scoring rules are benchmark-specific and are not disclosed. Missing optional files are reported as "not scored" and do not block evaluation of the sections that are available.

Areas assessed: differential expression results, cell-type-specific responses, handling of the experimental design, and the clarity and honesty of the analysis report.

## Constraints

- Do not use reference tutorial results or published results to reproduce the analysis.
- Do not force the results to match a predetermined number of significant genes, gene list, or cell-type ranking.
- Do not look for, request, or rely on any hidden evaluation or reference material while solving the task.
- Use only the public task description and the data from the source named above.

## Important Instructions

- Solve this task using your general knowledge and reasoning abilities.
- Do NOT search for, reference, or reproduce solutions from published papers or tutorials.
- Do NOT attempt to identify the source of this task or look up known solutions.
- Your solution will be evaluated on correctness, biological plausibility, and supporting evidence, not on matching any known reference implementation.
- Prioritize producing the required output files, in the formats above, with consistent gene identifiers.

