# Task: pbmc3k_qc_filtering

## Description

Perform quality control, cell filtering, and doublet assessment on the 10x Genomics PBMC 3K dataset.

Decide which cells to retain, justify the thresholds and methods you use, and report exactly which cells were excluded and why. Do not normalize, cluster, or annotate in this task.

## Dataset

- **Name:** PBMC 3K
- **Organism:** *Homo sapiens*
- **Genome build:** hg19
- **Assay:** 10x Genomics scRNA-seq
- **Download:** https://cf.10xgenomics.com/samples/cell-exp/1.1.0/pbmc3k/pbmc3k_filtered_gene_bc_matrices.tar.gz

## Input

Raw 10x Genomics matrix from the download link above (barcodes, genes, matrix). Inspect it before analysis.

## Tools to use

| Tool / Library | Potential functionality |
|---|---|
| Scanpy | Read the 10x matrix, compute quality-control metrics, filter cells and genes. |
| AnnData | Store and manage expression matrices and cell and gene metadata. Read and write `.h5ad` files. |
| NumPy | Support numerical operations and array manipulation. |
| pandas | Manage per-cell metrics and export results to CSV files. |
| SciPy | Support sparse expression-matrix operations. |
| Scrublet | Predict potential doublets; predicted doublets may be filtered out when justified. |


The listed tools are options, not mandatory steps. Other appropriate tools may be used when justified.

## Required outputs

Write all outputs to a single output directory.

**`cell_qc.csv`** has one row for every cell in the raw input (each barcode exactly once).

| Column | Description |
|---|---|
| `cell_id` | The cell barcode exactly as it appears in the input (for example `AAACATACAACCAC-1`). |
| `status` | `retained` or `excluded`. |
| `exclusion_reason` | Empty for retained cells; otherwise the reason(s) for exclusion, separated by `;`. |

You may add columns with QC metrics.

**`run_manifest.json`** is a JSON object with these integer keys:

- `input_cells`: cells in the raw input
- `qc_passing_cells`: cells passing your QC filters, before doublet removal
- `doublets_removed`: cells removed as predicted doublets
- `retained_cells`: cells with status `retained`
- `retained_genes`: genes kept after any gene filtering

## Recommended outputs (scored when present)

- **`Analysis report.txt`**: QC metrics examined, thresholds or methods chosen and why, doublet-assessment method and settings, cell counts after each step, and limitations.
- Additional keys in `run_manifest.json`. In `run_manifest.json` you may also record `seed`, `parameters`, and `versions` (software and annotation-resource versions) so the run can be reproduced.

## Evaluation

Your outputs are compared against a hidden reference. Exact scoring rules are benchmark-specific and are not disclosed. Missing optional files are reported as "not scored" and do not block evaluation of the sections that are available.

Areas assessed: justified filtering decisions, doublet handling, accounting for every input cell, and agreement of the retained and excluded cells with the reference.

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
