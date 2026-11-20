# Task 6: proteomics_end_to_end_real_world_qc

## Description
Run a complete label-free proteomics analysis, from a raw MaxQuant protein table to a list of differentially abundant proteins, on a real benchmark experiment.

The data were received from a proteomics core facility as exported. As in any real project, you are responsible for checking the data before drawing conclusions from it. You decide every processing step, its order, and its settings. Document what you did and why.

## Experiment
This is a benchmark experiment (LC-MS/MS on an LTQ Orbitrap, processed with MaxQuant 1.3 with label-free quantification and match-between-runs enabled).

- Every sample contains the **same amount of human (HeLa) protein**.
- Every sample also contains *E. coli* protein, at two different amounts:
  - **Condition L**: lower amount of *E. coli* protein. Samples as labelled by the facility: `L1`, `L2`, `L3`, `L4`
  - **Condition H**: higher amount of *E. coli* protein. Samples as labelled by the facility: `H1`, `H2`, `H3`, `H4`

The biological question: **which proteins differ in abundance between condition H and condition L, and by how much?**

## Input
- **File:** `/home/boltzmann6/.sci/profiles/prot_6/workspace/inputs/proteinGroups.txt`
- **Format:** tab-separated MaxQuant `proteinGroups.txt`, one row per protein group, with MaxQuant's standard columns (identifiers, FASTA headers, peptide counts, several kinds of intensity per sample, quality flags, and others).

## Suggested tools
| Tool | Possible use |
|---|---|
| pandas / NumPy | Reading and filtering the table |
| SciPy / statsmodels | Statistical testing, multiple-testing correction |
| matplotlib / seaborn | Quality-control plots |

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
A JSON object with these keys.

Sample handling:
- `samples_used` (object): the samples you actually used for each condition in the final test, e.g. `{"L": ["L1", "L2"], "H": ["H1", "H2"]}`. Use the sample names as they appear in the input. A sample placed under a condition different from its label means you concluded it belongs to that condition.
- `samples_excluded` (list of strings): samples you did not use, e.g. `["L2"]`, or `[]`.
- `sample_qc_notes` (object): for every sample you excluded or reassigned, a short reason, e.g. `{"L2": "..."}`. Use `{}` if none.

Integer keys:
- `total_protein_groups`: rows in the input table
- `removed_reverse`: rows flagged as reverse (decoy) hits
- `removed_contaminant`: rows flagged as potential contaminants
- `removed_only_identified_by_site`: rows flagged as only identified by a modification site
- `protein_groups_after_cleaning`: rows remaining after removing all flagged rows
- `proteins_tested`: rows in `de_results.csv`
- `n_significant`: rows with `significant = True`

Number keys:
- `fdr_threshold`: the adjusted p-value cutoff used for `significant`, between 0.01 and 0.1
- `fold_change_cutoff`: any minimum |log2fc| you also required, or `null` if none

String keys:
- `intensity_columns_used`, `filtering_rule`, `normalization_method`, `imputation_method`, `test_method`, `processing_order`

## Optional output
**`analysis_report.txt`**: a short report covering the quality checks you performed and what they showed, each processing decision and its reason, the number of proteins called, and caveats. This file is recorded but does not affect the score.

## Evaluation
Outputs are checked automatically against the known composition of the samples:
- **Sample handling:** whether each sample was used appropriately in the final analysis.
- **Data cleaning, detection, false discovery control, ranking and fold changes:** as for a standard differential abundance analysis of this design.
- **Format and consistency:** files and keys as specified, manifest consistent with the input and your results.

## Constraints
- Significance calls and fold changes must be computed from the measured intensities. You may use the known sample composition and protein annotations to guide processing decisions (for example quality control or normalization), but not to assign significance directly.
- Do not search for, request, or use the original publication's results, hidden evaluation files, or reference data.
- Use only this task description and the provided input file.
