# Task: 07_melanoma_tumor_ecosystem

## Description

Characterize the cellular composition and expression heterogeneity of human metastatic melanoma tumors in a single-cell RNA-seq dataset.

Identify the cell populations present, separate malignant from non-malignant cells, and label the non-malignant cell types. Determine whether 
malignant cells group by tumor of origin and whether non-malignant cells group by cell type across tumors. Identify recurring expression programs 
that vary between malignant cells, with the genes that define them. Report uncertainty and limitations.

## Dataset

- **Name:** Metastatic melanoma tumors, single-cell RNA-seq
- **Organism:** *Homo sapiens*
- **Assay:** Smart-seq2 single-cell RNA-seq (Illumina NextSeq 500), cells from multiple tumors
- **Accession:** GSE72056 (NCBI GEO)
- **Download:** https://www.ncbi.nlm.nih.gov/geo/query/acc.cgi?acc=GSE72056

## Input

Obtain the data yourself from the repository above. Inspect the supplementary files and the structure of the processed expression table before 
analysis. Check what kind of values the table holds (counts, TPM, log-scaled) and choose normalization accordingly.

The first rows of the table are annotation rows, not genes. They contain the tumor of origin, a malignant classification based on inferred 
copy-number changes, and cell-type codes for non-malignant cells. Use the tumor-of-origin row as sample metadata. Do not use the malignant 
classification or cell-type rows in your analysis. Describe your quality control, filtering and normalization choices in the report.

## Required outputs

Write all outputs to a single output directory.

**`cell_annotations.csv`** has one row for every cell retained after quality control.

| Column | Description |
|---|---|
| `cell_id` | The cell identifier exactly as it appears in the input. |
| `tumor_id` | The tumor of origin for the cell (from the tumor annotation row or the cell name). |
| `cell_type` | Your label for the cell (for example malignant, T cell, B cell, macrophage, or another type you identify). |
| `malignant_call` | `malignant`, `non-malignant`, or `unresolved`. |

**`cell_type_counts.csv`** has the number of cells of each cell type in each tumor, with columns `tumor_id`, `cell_type`, and `n_cells`.

**`cell_type_markers.csv`** has marker genes for each cell type you identified, with columns `cell_type`, `gene`, `score`, `log2_fold_change`, and
`adj_p_value`. List the top genes per cell type ranked from strongest to weakest.

**`malignant_programs.csv`** lists the recurring expression programs you found within malignant cells, with columns `program`, `gene`, and `score`
(the strength of the gene's association with the program). List up to 100 genes per program, ranked from strongest to weakest.

**`summary.json`** has these keys:

- `cells_input` and `cells_retained`: number of cells in the input and after quality control
- `cell_types_found`: object mapping each cell type you identified to its number of cells
- `n_malignant` and `n_nonmalignant`: number of cells in each group
- `data_used`: which file and which value scale you used (for example counts or log-scaled TPM)
- `model`: a short description of the methods you used
- `software_used`: the software and package versions you used, including any packages you installed

## Recommended outputs 

- **`Analysis report.txt`**: dataset summary; quality control and normalization; how malignant cells were called; the evidence for each cell type;
whether malignant and non-malignant cells group by tumor or by cell type, with supporting evidence; how you identified the malignant programs; and
uncertainties and limitations.
- **`umap.png`**: a plot of the cells colored by cell type and by tumor.

## Evaluation

Your outputs are compared against a hidden reference. Exact scoring rules are benchmark-specific and are not disclosed. Missing optional files are
reported as "not scored" and do not block evaluation of the sections that are available.

Areas assessed: the cell types identified and their numbers across tumors, marker-gene evidence for each cell type, the malignant expression 
programs, and the clarity and honesty of the analysis report.

## Constraints

- Do not use reference tutorial results or published results to reproduce the analysis.
- Do not force the results to match a predetermined number of clusters, cell types, or marker genes.
- Do not look for, request, or rely on any hidden evaluation or reference material while solving the task.
- Do not use the malignant classification or cell-type annotation rows of the input table in your analysis.
- Use only the public task description and the data from the source named above.

## Important Instructions

- Solve this task using your general knowledge and reasoning abilities.
- Do NOT search for, reference, or reproduce solutions from published papers or tutorials.
- Do NOT attempt to identify the source of this task or look up known solutions.
- Your solution will be evaluated on correctness, biological plausibility, and supporting evidence, not on matching any known reference 
implementation.
- Prioritize producing the required output files, in the formats above, with consistent cell identifiers.
