# Task: task_020_flab_antibody_developability_ranking

## Description

Prioritize paired monoclonal antibody candidates for the specified developability or fitness property. Calculate candidate-level computational scores, preserve the relevant sequence and assay context, and return a ranked shortlist with property-specific evidence. Evaluate predictions against independently held measurements for each endpoint.

## Target

**Target:** Specified property such as expression, thermostability, aggregation, polyreactivity or binding\
**Candidate Antibodies:** Supplied complete VH/VL pairs with source-study and construct identities\
**Reference Antibody:** Dataset-specific parent or supplied panel control\
**Antibody Format:** Declared Fab, scFv or IgG construct with verified variable-domain pairing\
**Objective:** Computational developability/fitness assessment and candidate prioritization

## Design Constraints

- Verify paired sequences, parent lineage, construct, property definition, assay units and beneficial score direction before evaluation.
- Score the supplied candidates without altering their sequences. Keep individual properties and measurement contexts separately identified.
- Freeze computational predictions and shortlist ordering before exposing evaluation measurements. For trained predictors, keep related parents and studies together in data partitions.
- Retain raw and transformed score values with the transformation definition. Use matched sequence/construct records when considering more than one property.

## Evaluation Metrics

| Criterion | Measurements and Evidence | Evaluation Rule |
| --- | --- | --- |
| Linear agreement | Pearson r for each method–assay pair | Match finite candidate scores and measurements in the declared direction. |
| Rank agreement | Spearman ρ and Kendall τ | Preserve the source tie convention and report signed correlations. |
| Property-specific selection | Candidate scores, ranks and measured property outcomes | Assess each property in its own assay context. |
| Generalization | Study/parent partition identities and per-assay sample counts | Keep independent evaluation records and report the evaluated population. |

Source references: [FLAb preprint, 2024](https://doi.org/10.1101/2024.01.13.575504), [FLAb2 preprint, 2025](https://doi.org/10.64898/2025.12.27.696706), [Graylab/FLAb @ `e05e3f013578`](https://github.com/Graylab/FLAb/tree/e05e3f0135783ffb7de412df6a1467e7a0031911).

Computational reference: [task-specific benchmark](../../benchmark/monoclonal_antibody_design/task_020_flab_antibody_developability_ranking.md).

## Expected Output

**Format:** `antibody_assessment_bundle`\
**Directory:** `developability_results/`

- `predictions.csv`: computational scores for every supplied candidate, with method, score direction and evaluation status.
- `shortlist.csv`: ranked candidate pairs, selection criteria, parent differences and exclusion reasons.
- `metrics.json`: actual computational values, metric definitions, structural scope, units, candidate hashes and provenance.
- `benchmark_comparison.csv`: published computational reference values and executed results, with their respective scopes.
- `report.md`: scientific rationale, supported conclusions and candidate-specific evidence; include structures, chain/residue maps and raw scoring outputs.

## Important Instructions

- Select methods independently within the user's access and computational constraints; no particular workflow is required.
- Report missing essential inputs as `NEEDS_INPUT`. Record the exact target construct, reference sequence, editable regions or candidate panel, methods and evaluation settings used.
- Keep computational predictions and experimental property measurements separately identified.
- Property ranking does not establish clinical safety, immunogenicity or therapeutic readiness.
