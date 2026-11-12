# Task: task_021_abdesign_antibody_binding_retention

## Description

Prioritize single-point HCDR3 variants that retain binding to the supplied human protein antigen. Calculate mutation-effect scores relative to each verified parent antibody, then return a ranked shortlist with matched structural evidence. Evaluate predictions against independently held, parent-normalized binding-retention measurements.

## Target

**Target:** Supplied human protein antigen and exact construct\
**Reference Antibody:** Verified parent VH/VL pair and corresponding complex\
**Candidate Set:** Supplied single-point HCDR3 variants\
**Antibody Format:** Paired variable domains in the study IgG1 assay context\
**Objective:** Computational prediction of mutation-associated binding retention

## Design Constraints

- Verify each mutation against the complete parent sequence and reference complex; preserve all unedited antibody residues.
- Keep experimental, predicted and side-chain-remodelled structural preparations separately identified. Score each preparation consistently across the candidate panel.
- Freeze computational scores before reading parent-normalized evaluation labels. Orient the score toward greater binding retention.
- Evaluate each parent system independently and preserve its assay normalization. Compare candidate panels using the same parent/mutant population.

## Evaluation Metrics

| Criterion | Measurements and Evidence | Evaluation Rule |
| --- | --- | --- |
| Linear prediction agreement | Per-parent and pooled Pearson r | Evaluate computational mutation scores against the normalized binding-retention endpoint. |
| Rank prediction agreement | Per-parent and pooled Spearman ρ | Retain score direction, parent identity and structural preparation. |
| Preparation sensitivity | Changes in r/ρ across structural preparations | Use identical mutant records when comparing preparation methods. |
| Candidate prioritization | Frozen scores, ranks and reference differences | Return the highest-ranked eligible variants with their supporting evidence. |

Source references: [AbDesign, mAbs 2025](https://doi.org/10.1080/19420862.2025.2567319), [data provider](https://naturalantibody.com/ab-design/).

Computational reference: [task-specific benchmark](../../benchmark/monoclonal_antibody_design/task_021_abdesign_antibody_binding_retention.md).

## Expected Output

**Format:** `antibody_assessment_bundle`\
**Directory:** `binding_retention_results/`

- `predictions.csv`: computational scores for every supplied candidate, with method, score direction and evaluation status.
- `shortlist.csv`: ranked candidate pairs, selection criteria, parent differences and exclusion reasons.
- `metrics.json`: actual computational values, metric definitions, structural scope, units, candidate hashes and provenance.
- `benchmark_comparison.csv`: published computational reference values and executed results, with their respective scopes.
- `report.md`: scientific rationale, supported conclusions and candidate-specific evidence; include structures, chain/residue maps and raw scoring outputs.

## Important Instructions

- Select methods independently within the user's access and computational constraints; no particular workflow is required.
- Report missing essential inputs as `NEEDS_INPUT`. Record the exact target construct, reference sequence, editable regions or candidate panel, methods and evaluation settings used.
- Use the source normalized ELISA values as binding-retention labels; retain their original assay meaning.
- A predicted favorable mutation remains a computational hypothesis until independently measured.
