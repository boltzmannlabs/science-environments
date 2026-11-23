# Task 4: proteomics_synthetic_protein_quantification

## Description
Infer protein-level abundances from peptide-level measurements in a simulated Label-Free Quantification (LFQ) proteomics experiment.

In bottom-up proteomics, proteins are digested into peptides, and the mass spectrometer measures the peptides, not the proteins. Each protein's abundance in each sample must therefore be estimated from its peptides. Peptides of the same protein ionize very differently, so their raw intensities can differ several-fold even though they come from the same protein. Some peptides are missing in some samples, and some peptides may not reflect their protein reliably.

Your goal is to inspect the peptide table, decide which peptides to use, and estimate a log2 abundance for every protein in every sample with a method you can justify. Examine the data before deciding.

The samples are already normalized against each other. Do not apply further sample normalization, imputation of protein values, differential expression testing, or classification in this task.

## Dataset
- **Name:** Simulated peptide-level LFQ table, Control vs Treated (yeast background)
- **Modality:** LFQ LC-MS/MS peptide intensities
- **Input file:** `/home/boltzmann6/.sci/profiles/prot_4/workspace/inputs/peptide_intensities.csv`

## Input data structure
`peptide_intensities.csv` has one row per peptide:
- `Peptide_ID`: peptide identifier (e.g. `PEP00001`)
- `Sequence`: peptide amino-acid sequence
- `Proteins`: the protein(s) the peptide matches. A single ID (e.g. `YBR001W`) means the peptide is unique to that protein. Several IDs separated by `;` (e.g. `YBR001W;YBR117W`) mean the peptide matches more than one protein.
- `Control_Rep1` … `Treated_Rep3`: raw, linear-scale (not logged) peptide intensities. Empty cells are missing values.

## Suggested tools
| Tool | Possible use |
|---|---|
| pandas / NumPy | Loading, grouping peptides by protein, log transformation |
| SciPy / statsmodels | Robust summaries, linear models |

These are options, not required steps. Other Python libraries, including ports of established protein-quantification algorithms, are fine if justified.

## Required outputs
Write all outputs to `results/`.

### 1. `protein_matrix_log2.csv`
- First column `protein_id`, followed by the six sample columns **in the same order as the input**.
- One row for **every individual protein** that has at least one peptide unique to it (single protein IDs only; do not output combined IDs such as `YBR001W;YBR117W`).
- Values are estimated protein abundances on the **log2 scale**.
- No missing values. Every protein has at least one observed peptide in every sample.
- The absolute level of each protein is not evaluated, only how its abundance changes across samples.

### 2. `run_manifest.json`
A JSON object with these integer keys:
- `total_peptides`: number of peptide rows in the input
- `unique_peptides`: peptides that match exactly one protein
- `shared_peptides`: peptides that match more than one protein
- `quantified_proteins`: number of rows in `protein_matrix_log2.csv`

And these string keys:
- `quantification_method`: your method and key settings
- `shared_peptide_handling`: how you treated peptides that match more than one protein

## Optional output
**`analysis_report.txt`**: a short report on the peptide data (peptides per protein, missingness, how consistent peptides of the same protein are), your choice of method and why, and any caveats. This file is recorded but does not affect the score.

## Evaluation
Outputs are checked automatically against hidden reference protein abundances:
- **Format:** files, columns and protein rows as specified, values on the log2 scale.
- **Profile accuracy:** how closely each protein's estimated pattern across the six samples matches the true pattern (each protein's overall level is ignored).
- **Fold-change accuracy:** how closely each protein's Treated-vs-Control difference matches the true difference.
- **Bookkeeping:** manifest counts are consistent with the input and your output.

## Constraints
- Do not search for, request, or use hidden evaluation files or reference data.
- Use only this task description and the provided input file.
