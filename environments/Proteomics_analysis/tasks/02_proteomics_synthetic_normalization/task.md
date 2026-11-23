# Task 2: proteomics_synthetic_normalization

## Description
Perform log2 transformation, missing-value handling, and sample normalization on a simulated Label-Free Quantification (LFQ) mass spectrometry protein intensity matrix.

In LFQ proteomics, technical differences between runs (for example sample loading, injection volume, or ionization efficiency) shift the overall intensity of whole samples up or down. These sample-wide shifts are technical, not biological, and must be removed before samples can be compared. At the same time, genuine biological differences between conditions must be preserved.

Your goal is to inspect the data, handle the small number of missing values, transform intensities to log2, and choose and apply a sample normalization method you can justify for this dataset. Examine the data before deciding which method is appropriate.

Do not filter proteins, run differential expression statistics, or build classification models in this task.

## Dataset
- **Name:** Simulated LFQ proteomics matrix with sample-wise technical shifts (yeast background)
- **Modality:** LFQ LC-MS/MS protein intensity matrix
- **Input file:** `/home/boltzmann6/.sci/profiles/prot_02/workspace/inputs/raw_protein_intensities.csv`

## Input data structure
`raw_protein_intensities.csv` contains raw, linear-scale (not logged) intensities for 6 samples:
- `Protein_ID`: protein accession (e.g. `YAL001C`)
- `Control_Rep1`, `Control_Rep2`, `Control_Rep3`: control replicates
- `Treated_Rep1`, `Treated_Rep2`, `Treated_Rep3`: treated replicates

Empty cells are missing values.

## Suggested tools
| Tool | Possible use |
|---|---|
| pandas | Loading, per-sample summaries, index bookkeeping |
| NumPy / SciPy | Log transformation, distribution checks, normalization |
| scikit-learn | Imputation of missing values |

These are options, not required steps. Other Python libraries are fine if justified.

## Required outputs
Write all outputs to `results/`.

### 1. `normalized_matrix_log2.csv`
- First column `protein_id`, followed by the six sample columns **in the same order as the input**.
- One row for **every** protein in the input (250 rows). No proteins are removed.
- Values are on the **log2 scale**, using base 2 and no pseudocount, after normalization.
- No missing values.
- The overall intensity level is your choice. For example, centring on 0 and aligning to the original global median are both acceptable. Only the relative alignment of samples and proteins is evaluated.

### 2. `run_manifest.json`
A JSON object with these integer keys:
- `total_input_proteins`: number of unique protein IDs in the input
- `output_proteins`: number of rows in `normalized_matrix_log2.csv`
- `imputed_value_cells`: number of cells that were missing in the input and filled by imputation

It may also include these string keys:
- `normalization_method`: the method and any key parameters
- `imputation_method`: the imputation method
- `processing_order`: the order of the steps (e.g. "log2 -> impute -> normalize")

## Optional output
**`analysis_report.txt`**: a short report covering the per-sample distributions before and after normalization, your assessment of the technical shifts, any features of the data that influenced your choice of method, and your reasoning. This file is recorded but does not affect the score.

## Evaluation
Outputs are checked automatically against hidden reference data with the technical shifts removed:
- **Format:** files, columns and row counts are as specified, and values are on the log2 scale.
- **Integrity:** within each sample, the ordering of observed values is preserved.
- **Sample alignment:** how completely the technical shifts between samples are removed.
- **Accuracy:** how close the normalized values are to the reference, ignoring any constant overall offset.
- **Biological preservation:** whether genuine differences between Control and Treated are kept intact.
- **Imputation and bookkeeping:** accuracy of filled values, and consistency of the manifest with your files.

## Constraints
- Do not search for, request, or use hidden evaluation files or reference data.
- Use only this task description and the provided input file.
