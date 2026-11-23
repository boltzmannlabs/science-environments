# Task 5: 
proteomics_end_to_end_mixed_proteome

## Description
Run a complete label-free proteomics analysis, from a raw MaxQuant protein table to a list of differentially abundant proteins, on a real benchmark experiment.

You decide every processing step, its order, and its settings. Inspect the data before deciding. Document what you did and why.

## Experiment
This is a published benchmark experiment (LC-MS/MS on an LTQ Orbitrap, processed with MaxQuant 1.3 with label-free quantification and match-between-runs enabled).

- Every sample contains the **same amount of human (HeLa) protein**.
- Every sample also contains *E. coli* protein, at two different amounts:
  - **Condition L** (samples `L1`, `L2`, `L3`): lower amount of *E. coli* protein
  - **Condition H** (samples `H1`, `H2`, `H3`): higher amount of *E. coli* protein
- Each condition has three replicates.

The biological question: **which proteins differ in abundance between condition H and condition L, and by how much?**

## Input
- **File:** `/home/boltzmann6/.sci/profiles/prot_e1/workspace/inputs/proteinGroups.txt`
- **Format:** tab-separated MaxQuant `proteinGroups.txt`, one row per protein group, with all of MaxQuant's standard columns (identifiers, FASTA headers, peptide counts, several kinds of intensity per sample, quality flags, and others).

## Suggested tools
| Tool | Possible use |
|---|---|
| pandas / NumPy | Reading and filtering the table |
| SciPy / statsmodels | Statistical testing, multiple-testing correction |

These are options, not requirements. Other Python libraries, including ports of established proteomics methods, are fine if justified.

## Required outputs
Write all outputs to `results/`.

### 1. `de_results.csv`
One row for **every protein group you tested**, with these columns:

| Column | Description |
|---|---|
| `protein_id` | The protein group's `Protein IDs` value, copied exactly from the input |
| `log2fc` | Estimated log2 fold change, **H minus L** (positive = higher in H) |
| `p_value` | Unadjusted p-value |
| `adj_p_value` | p-value adjusted for multiple testing |
| `significant` | `True` if you call the protein differentially abundant, otherwise `False` |

### 2. `run_manifest.json`
A JSON object with these integer keys:
- `total_protein_groups`: rows in the input table
- `removed_reverse`: rows flagged as reverse (decoy) hits
- `removed_contaminant`: rows flagged as potential contaminants
- `removed_only_identified_by_site`: rows flagged as only identified by a modification site
- `protein_groups_after_cleaning`: rows remaining after removing all flagged rows
- `proteins_tested`: rows in `de_results.csv`
- `n_significant`: rows with `significant = True`

These number keys:
- `fdr_threshold`: the adjusted p-value cutoff used for `significant`, between 0.01 and 0.1
- `fold_change_cutoff`: any minimum |log2fc| you also required, or `null` if none

And these string keys:
- `intensity_columns_used`: which intensity columns you analysed
- `filtering_rule`: how you handled missing values when choosing proteins to test
- `normalization_method`: your normalization and why
- `imputation_method`: your imputation, or "none"
- `test_method`: your statistical test and key settings
- `processing_order`: the order of your steps

## Optional output
**`analysis_report.txt`**: a short report covering data quality, each processing decision and the reason for it, the distribution of fold changes, the number of proteins called, and caveats. This file is recorded but does not affect the score.

## Evaluation
Outputs are checked automatically against the known composition of the samples:
- **Format and consistency:** files and columns as specified, manifest consistent with the input and your results.
- **Data cleaning:** whether proteins that should be removed before analysis were removed.
- **Detection:** how many truly changed proteins you find, and how many unchanged proteins you call by mistake.
- **False discovery control:** whether the fraction of wrong calls is consistent with your stated threshold.
- **Ranking:** how well your p-values separate truly changed from unchanged proteins, compared with the published analysis of this dataset.
- **Fold changes:** whether your estimated fold changes match the known sample composition.

## Constraints
- Significance calls and fold changes must be computed from the measured intensities. You may use the known sample composition and protein annotations to guide processing decisions (for example quality control or normalization), but not to assign significance directly.
- Do not search for, request, or use the original publication's results, hidden evaluation files, or reference data.
- Use only this task description and the provided input file.
