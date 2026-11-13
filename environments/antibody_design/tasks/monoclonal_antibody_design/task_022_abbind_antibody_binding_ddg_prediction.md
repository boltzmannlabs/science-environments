# Task: task_022_abbind_antibody_binding_ddg_prediction

## Description

Predict the effects of supplied antibody mutations on binding to a defined human protein antigen. Calculate mutation-associated binding-energy changes relative to the verified parent and prioritize variants predicted to improve the interaction. Return candidate-level scores and a ranked shortlist, with prediction quality evaluated against independently held measured mutation effects.

## Target

**Target:** Supplied human protein antigen and exact construct\
**Reference Antibody:** Complete parent VH/VL pair and mapped antibody–antigen complex\
**Candidate Set:** Supplied single- or multiple-substitution antibody variants\
**Antibody Format:** Conventional paired variable domains in the declared reference context\
**Objective:** Binding ΔΔG prediction and improved-variant prioritization

## Design Constraints

- Verify parent identity, complete paired sequences, mutation notation, structure mapping and measurement units before scoring.
- Define ΔΔG = ΔG_mutant − ΔG_parent and retain its sign convention; negative measured values indicate stronger binding.
- Keep single and multiple substitutions separately summarized. Evaluate reference and variants with matched target and scoring preparation.
- Freeze model scores before joining evaluation labels. Keep parent/complex families together in training and test partitions for supervised methods.

## Evaluation Metrics

| Criterion | Measurements and Evidence | Evaluation Rule |
| --- | --- | --- |
| Energy-change agreement | Pearson r between predicted and measured ΔΔG | Match source rows, sign convention and energy units. |
| Improvement classification | ROC-AUC for improved versus weakened binding | Use −predicted ΔΔG as the improvement score and measured ΔΔG < 0 as the positive label. |
| Effect-size assessment | ROC-AUC on declared \|ΔΔG\| subsets | Keep strict >0.5 and >1 kcal/mol subsets separately identified. |
| Candidate prioritization | Mutation identity, parent differences and computational rank | Return complete eligible pairs with traceable scoring artifacts. |

Source references: [AB-Bind original study](https://pmc.ncbi.nlm.nih.gov/articles/PMC4815335/), [DOI](https://doi.org/10.1002/pro.2829), [sarahsirin/AB-Bind-Database @ `f5af13df8000`](https://github.com/sarahsirin/AB-Bind-Database/tree/f5af13df80000ad9e438a6ccf1147bd5f9d55dba).

Computational reference: [task-specific benchmark](../../benchmark/monoclonal_antibody_design/task_022_abbind_antibody_binding_ddg_prediction.md).

## Expected Output

**Format:** `antibody_assessment_bundle`\
**Directory:** `binding_ddg_results/`

- `predictions.csv`: computational scores for every supplied candidate, with method, score direction and evaluation status.
- `shortlist.csv`: ranked candidate pairs, selection criteria, parent differences and exclusion reasons.
- `metrics.json`: actual computational values, metric definitions, structural scope, units, candidate hashes and provenance.
- `benchmark_comparison.csv`: published computational reference values and executed results, with their respective scopes.
- `report.md`: scientific rationale, supported conclusions and candidate-specific evidence; include structures, chain/residue maps and raw scoring outputs.

## Important Instructions

- Select methods independently within the user's access and computational constraints; no particular workflow is required.
- Report missing essential inputs as `NEEDS_INPUT`. Record the exact target construct, reference sequence, editable regions or candidate panel, methods and evaluation settings used.
- Retain the score definition and units supplied by the computational method; identify calibrated energies and ranking scores explicitly.
- Predicted mutation effects do not establish experimentally improved affinity of an unmeasured variant.
