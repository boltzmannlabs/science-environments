# Task: task_023_abagym_antibody_interface_mutation_scoring

## Description

Assess the effects of supplied antibody-interface mutations on recognition of the specified human protein antigen. Score each antibody variant against its verified parent, identify mutations predicted to preserve the interaction, and return a ranked candidate assessment. Evaluate the computational ranking against independently held measurements using each assay’s documented interpretation.

## Target

**Target:** Supplied human protein antigen and exact construct\
**Reference Antibody:** Verified parent VH/VL pair and mapped antigen complex\
**Candidate Set:** Supplied antibody-side interface mutations\
**Antibody Format:** Conventional paired variable domains\
**Objective:** Computational antibody-interface mutation-effect assessment

## Design Constraints

- Verify mutation partner, VH/VL pairing and residue correspondence before scoring; retain antibody-side mutations in the candidate panel.
- Preserve the source interface definition and assay-specific score direction. Keep raw DMS values and documented normalizations separately identified.
- Freeze computational predictions before joining evaluation labels. Retain the parent complex and assay identity for every mutation.
- Use a consistently defined disruptive-mutation class and threshold population across compared methods; report the corresponding candidate counts.

## Evaluation Metrics

| Criterion | Measurements and Evidence | Evaluation Rule |
| --- | --- | --- |
| Mutation ordering | Per-assay Spearman ρ | Compare consistently oriented computational scores and assay measurements. |
| Disruption classification | Per-assay ROC-AUC | Use the source assay’s top-5% disruptive-mutation definition and tie rule. |
| Aggregate performance | Equal-assay means of Spearman ρ and ROC-AUC | Identify the evaluated assays and report each contributing population. |
| Candidate assessment | Mutation mapping, predicted effect and rank | Retain complete candidate identities and traceable parent-relative evidence. |

Source references: [AbAgym, mAbs 2025](https://doi.org/10.1080/19420862.2025.2592421), [3BioCompBio/AbAgym @ `87af82ad68bb`](https://github.com/3BioCompBio/AbAgym/tree/87af82ad68bb90921e15fb8b79c7bcb1d05b23d3).

Computational reference: [task-specific benchmark](../../benchmark/monoclonal_antibody_design/task_023_abagym_antibody_interface_mutation_scoring.md).

## Expected Output

**Format:** `antibody_assessment_bundle`\
**Directory:** `interface_mutation_results/`

- `predictions.csv`: computational scores for every supplied candidate, with method, score direction and evaluation status.
- `shortlist.csv`: ranked candidate pairs, selection criteria, parent differences and exclusion reasons.
- `metrics.json`: actual computational values, metric definitions, structural scope, units, candidate hashes and provenance.
- `benchmark_comparison.csv`: published computational reference values and executed results, with their respective scopes.
- `report.md`: scientific rationale, supported conclusions and candidate-specific evidence; include structures, chain/residue maps and raw scoring outputs.

## Important Instructions

- Select methods independently within the user's access and computational constraints; no particular workflow is required.
- Report missing essential inputs as `NEEDS_INPUT`. Record the exact target construct, reference sequence, editable regions or candidate panel, methods and evaluation settings used.
- Retain the experimental meaning of each DMS endpoint when interpreting computational agreement.
- Mutation-effect ranking does not establish equilibrium affinity or therapeutic activity.
