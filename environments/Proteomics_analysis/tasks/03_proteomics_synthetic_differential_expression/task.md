# Task 3: proteomics_synthetic_differential_expression

## Description
Identify proteins whose abundance differs between Control and Treated samples in a simulated Label-Free Quantification (LFQ) proteomics experiment.

The data have already been log2-transformed and normalized, and contain no missing values. Your goal is to estimate the change for every protein, test whether each change is statistically supported, control for testing many proteins at once, and report which proteins you consider differentially abundant.

The experiment has only three replicates per condition. Choose a statistical approach you can justify for this design, and examine the data before deciding.

Do not filter out proteins, re-normalize the data, or build classification models in this task.

## Dataset
- **Name:** Simulated LFQ proteomics matrix, Control vs Treated (yeast background)
- **Modality:** LFQ LC-MS/MS protein abundance matrix (log2, normalized)
- **Input file:** `/home/boltzmann6/.sci/profiles/prot_03/workspace/inputs/protein_log2_normalized.csv`

## Input data structure
`protein_log2_normalized.csv` contains log2-scale, normalized abundances for 500 proteins:
- `Protein_ID`: protein accession (e.g. `YAL001C`)
- `Control_Rep1`, `Control_Rep2`, `Control_Rep3`: control replicates
- `Treated_Rep1`, `Treated_Rep2`, `Treated_Rep3`: treated replicates

## Suggested tools
| Tool | Possible use |
|---|---|
| pandas / NumPy | Loading data, group summaries |
| SciPy / statsmodels | Statistical tests, multiple-testing correction |

These are options, not required steps. Other Python libraries are fine, including Python ports of established proteomics or genomics statistical methods, if justified.

## Required outputs
Write all outputs to `results/`.

### 1. `de_results.csv`
One row for **every** protein in the input (500 rows), with these columns:

| Column | Description |
|---|---|
| `protein_id` | Accession exactly as in the input |
| `log2fc` | Estimated log2 fold change, **Treated minus Control** (positive = higher in Treated) |
| `p_value` | Unadjusted p-value from your test |
| `adj_p_value` | p-value adjusted for multiple testing |
| `significant` | `True` if you call the protein differentially abundant, otherwise `False` |

### 2. `run_manifest.json`
A JSON object with these keys:
- `total_proteins` (integer): number of proteins tested
- `n_significant` (integer): number of rows with `significant = True`
- `n_up` (integer): significant proteins with `log2fc > 0`
- `n_down` (integer): significant proteins with `log2fc < 0`
- `fdr_threshold` (number): the adjusted p-value cutoff you used for `significant`, between 0.01 and 0.1 (e.g. `0.05`)
- `test_method` (string): the statistical test and key settings
- `multiple_testing_correction` (string): the correction method
- `fold_change_cutoff` (number or null): any minimum |log2fc| you also required, or `null` if none

## Optional output
**`analysis_report.txt`**: a short report on the data (e.g. the spread of protein variances), your choice of test and why, the number of proteins called, and any caveats. This file is recorded but does not affect the score.

## Evaluation
Outputs are checked automatically against hidden reference data:
- **Format and consistency:** files and columns as specified; `significant` matches your stated threshold; manifest counts match the results file.
- **Detection:** how many truly changed proteins you find, and how many unchanged proteins you call by mistake.
- **False discovery control:** whether the fraction of your calls that are wrong is consistent with the FDR threshold you state.
- **Ranking:** whether your p-values rank truly changed proteins above unchanged ones, independent of the cutoff.
- **Fold changes:** accuracy and direction of your `log2fc` estimates.

## Constraints
- Do not search for, request, or use hidden evaluation files or reference data.
- Use only this task description and the provided input file.
