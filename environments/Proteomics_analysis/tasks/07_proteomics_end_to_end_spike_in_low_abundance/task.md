# Task 7: proteomics_end_to_end_spike_in_low_abundance

## Description
Run a complete label-free proteomics analysis, from a raw MaxQuant protein table to lists of differentially abundant proteins, on a real benchmark experiment with low-abundance spiked proteins.

You decide every processing step, its order, and its settings. Inspect the data before deciding. Document what you did and why.

## Experiment
This is a published benchmark experiment (LC-MS/MS on an LTQ Orbitrap, data-dependent acquisition, processed with MaxQuant with label-free quantification).

- Every sample contains the **same amount of yeast (*Saccharomyces cerevisiae*) protein**.
- Each sample is also spiked with the **UPS1 standard**: 48 human proteins mixed in equal amounts. The UPS1 proteins are marked with `_UPS` in the `Fasta headers` column.
- UPS1 was spiked at **nine different amounts**: 50, 125, 250, 500, 2500, 5000, 12500, 25000 and 50000 amol. Each amount was measured in **triplicate**, giving 27 samples. Sample columns are named by amount and replicate, e.g. `LFQ intensity 5000amol_2`.

The biological question is asked for **three comparisons** (higher amount vs lower amount):

| Contrast | Higher | Lower |
|---|---|---|
| `C1` | 25000amol | 2500amol |
| `C2` | 5000amol | 500amol |
| `C3` | 2500amol | 500amol |

For each contrast: **which proteins differ in abundance between the two amounts, and by how much?**

You may use any of the 27 samples you consider helpful (for example for quality control, normalization or variance estimation), but each contrast compares only its two amounts.

## Input
- **File:** `/home/boltzmann6/.sci/profiles/prot_7/workspace/inputs/proteinGroups.txt`
- **Format:** tab-separated MaxQuant `proteinGroups.txt`, one row per protein group, with MaxQuant's standard columns (identifiers, FASTA headers, peptide counts, several kinds of intensity per sample, quality flags, and others).

## Suggested tools
| Tool | Possible use |
|---|---|
| pandas / NumPy | Reading and filtering the table |
| SciPy / statsmodels | Statistical testing, multiple-testing correction |

These are options, not requirements. Other Python libraries, including ports of established proteomics methods, are fine if justified.

## Required outputs
Write all outputs to `results/`.

### 1. `de_results.csv`
One row **per protein group per contrast** that you assessed, with these columns:

| Column | Description |
|---|---|
| `contrast` | `C1`, `C2` or `C3` |
| `protein_id` | The protein group's `Protein IDs` value, copied exactly from the input |
| `log2fc` | Estimated log2 fold change, **higher amount minus lower amount**. May be empty only if `call_basis` is `presence_absence` |
| `p_value` | Unadjusted p-value. May be empty only if `call_basis` is `presence_absence` |
| `adj_p_value` | p-value adjusted for multiple testing within the contrast. May be empty only if `call_basis` is `presence_absence` |
| `significant` | `True` if you call the protein differentially abundant in this contrast, otherwise `False` |
| `call_basis` | `test` if the call comes from a statistical test, or `presence_absence` if it comes from a rule based on where the protein was or was not detected |

### 2. `run_manifest.json`
A JSON object with these keys.

Integer keys:
- `total_protein_groups`: rows in the input table
- `removed_reverse`: rows flagged as reverse (decoy) hits
- `removed_contaminant`: rows flagged as potential contaminants
- `removed_only_identified_by_site`: rows flagged as only identified by a modification site
- `protein_groups_after_cleaning`: rows remaining after removing all flagged rows

Object keys, each with entries `C1`, `C2`, `C3`:
- `proteins_assessed`: rows in `de_results.csv` for that contrast, e.g. `{"C1": 900, "C2": 850, "C3": 840}`
- `n_significant`: rows with `significant = True` for that contrast

Number keys:
- `fdr_threshold`: the adjusted p-value cutoff used for test-based calls, between 0.01 and 0.1
- `fold_change_cutoff`: any minimum |log2fc| you also required for test-based calls, or `null` if none

String keys:
- `intensity_columns_used`, `filtering_rule`, `missing_value_strategy`, `normalization_method`, `test_method`, `presence_absence_rule` (or "none"), `processing_order`

## Optional output
**`analysis_report.txt`**: a short report covering data quality, the missing-value pattern, each processing decision and the reason for it, the number of proteins called per contrast, and caveats. This file is recorded but does not affect the score.

## Evaluation
Outputs are checked automatically against the known composition of the samples, separately for each contrast:
- **Detection:** how many truly changed proteins you find, and how many unchanged proteins you call by mistake.
- **False discovery control:** whether the fraction of wrong calls is consistent with your stated threshold.
- **Fold changes:** whether your estimated fold changes match the known spike-in amounts.
- **Data cleaning, format and consistency:** files and keys as specified, manifest consistent with the input and your results.

The three contrasts differ in difficulty, and the harder ones carry more weight.

## Constraints
- Significance calls and fold changes must be computed from the measured intensities and detection patterns. You may use the known sample composition and protein annotations to guide processing decisions (for example quality control or normalization), but not to assign significance directly.
- Do not search for, request, or use the original publication's results, hidden evaluation files, or reference data.
- Use only this task description and the provided input file.
