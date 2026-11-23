# Task 03 — blind forward prediction for indole skeletal editing

[Original supplied task and all reactant SMILES](original_request.md) · [Literature benchmark](../../benchmarks/task-03-indole-forward-prediction/README.md) · [Results and comparisons](../../results/task-03-indole-forward-prediction/README.md)

## Objective and inputs

Predict a major product for each of ten related indole amide substrates, then independently evaluate the saved predictions against subsequently supplied literature products. The original task provides exact reactant and solvent SMILES for IDs 1a–1g and 1j–1l. The reference products were withheld during the blind prediction and are stored only in the benchmark folder.

## Execution actually performed

Ten separate historical `forward_reaction` jobs received each substrate as `target_mol`. The tool submission did not encode the supplied solvent or the published conditions. No subsequent prediction rerun was performed after the references were disclosed. The agent's originally selected products must be distinguished from model-ranked candidates: the original 1d selection was an agent extrapolation, not a returned candidate. Full raw service records were not archived here.

## Expected outcomes and evaluation

Return one product per reaction and measure exact molecular-graph matches to the corresponding literature product; separately examine candidate lists and structural resemblance. Model rank, assistant selection and similarity are distinct. Record evidence and missing conditions; do not treat similarity as a probability, yield or proof of feasibility.

## Observed status

The ten initial assistant-selected products did not match their references. RDKit comparison of 297 manually transcribed candidate entries also found no exact matches, conditional on faithful and complete transcription; the full lists have not been machine-reconciled with original service outputs. SI chemical names and assignments support the reaction/product pairings, but graphical structures were not independently digitized. [Comparison and limitations](../../results/task-03-indole-forward-prediction/comparison_report.md).
