# Task 1: proteomics_synthetic_imputation

## Description
Perform quality-control filtering, log2 transformation, and missing-value imputation on a simulated Label-Free Quantification (LFQ) mass spectrometry protein intensity matrix.

In mass spectrometry proteomics, lower-abundance proteins frequently go undetected in some runs, producing missing values (NaN) that are not random. Your goal is to inspect the dataset, exclude low-confidence protein rows, transform intensities to log2 scale, and impute the remaining missing values with a strategy you can justify for this kind of data.

Do not run differential expression, normalization across samples, or classification in this task. Values that were observed in the input must not be altered beyond the log2 transform.

## Dataset
- **Name:** Simulated proteomics matrix (yeast background + spiked human proteins)
- **Modality:** LFQ LC-MS/MS protein intensity matrix
- **Input file:** `/home/boltzmann6/.sci/profiles/prot_01/workspace/inputs/raw_protein_intensities.csv`

## Input data structure
`raw_protein_intensities.csv` contains raw, linear-scale (not logged) intensities for 6 replicates:
- `Protein_ID`: protein accession (yeast ORF IDs such as `YAL001C`, or spiked human IDs such as `P60001`)
- `Control_Rep1`, `Control_Rep2`, `Control_Rep3`: control replicates
- `Treated_Rep1`, `Treated_Rep2`, `Treated_Rep3`: treated replicates

Empty cells are missing values. Inspect the data before processing.

## Suggested tools
| Tool | Possible use |
|---|---|
| pandas | Loading, filtering rows, index bookkeeping |
| NumPy / SciPy | Log transformation, distribution checks |
| scikit-learn | Statistical or neighbourhood-based imputers |

These are options, not required steps. Other Python libraries are fine if justified.

## Required outputs
Write all outputs to `results/`.

### 1. `imputed_matrix_log2.csv`
- First column `protein_id`, followed by the six sample columns **in the same order as the input**.
- One row per **retained** protein only.
- Values are **log2(raw intensity)**, using base 2 and no pseudocount.
- No missing values.
- Observed input values must equal log2 of the raw value. Only originally missing cells may be filled.

### 2. `protein_qc.csv`
Exactly one row for every protein ID in the input (215 rows).

| Column | Description |
|---|---|
| `protein_id` | Accession exactly as in the input |
| `status` | `retained` or `excluded` |
| `exclusion_reason` | Empty for retained rows. For excluded rows, one of: `excessive_missing_values`, `no_valid_values` |

### 3. `run_manifest.json`
A JSON object with these integer keys:
- `total_input_proteins`: number of unique protein IDs in the input
- `retained_proteins`: number of rows marked `retained` (must equal the row count of `imputed_matrix_log2.csv`)
- `excluded_proteins`: number of rows marked `excluded`
- `imputed_value_cells`: number of cells in `imputed_matrix_log2.csv` that were missing in the input and filled by imputation

It may also include these string keys:
- `filter_rule`: your filtering rule in words (e.g. "retain proteins with at least 3 valid values")
- `imputation_method`: your imputation method and its key parameters

## Optional output
**`analysis_report.txt`**: a short report covering the intensity distribution before and after transformation, your assessment of the missing-value pattern, and the reasons for your filtering and imputation choices. This file is recorded but does not affect the score.

## Evaluation
Outputs are checked automatically against hidden reference data:
- **Format:** files, columns and row counts are as specified.
- **Integrity:** observed values are preserved after log2 transformation.
- **Bookkeeping:** manifest counts are consistent with your files and the input.
- **QC:** low-confidence proteins are excluded, without discarding proteins that have adequate data.
- **Imputation accuracy:** error of your imputed values against the hidden true values, compared with standard reference methods.

## Constraints
- Do not search for, request, or use hidden evaluation files or reference data.
- Use only this task description and the provided input file.
