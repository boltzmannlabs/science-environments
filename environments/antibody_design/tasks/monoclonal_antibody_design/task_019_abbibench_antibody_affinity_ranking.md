# Task: task_019_abbibench_antibody_affinity_ranking

## Description

Prioritize the supplied paired monoclonal antibody variants for binding to a defined human protein antigen. Score every variant under matched target and reference conditions, then return a ranked shortlist with candidate-level computational evidence. Assess ranking quality using independently held experimental labels after scores and selections are frozen.

## Target

**Target:** Defined human protein antigen; supplied panels may include VEGF, ANG2 or integrin-α1\
**Reference Antibody:** Verified parent VH/VL pair for the selected antigen and assay\
**Candidate Set:** Supplied variants with complete paired sequences and stable identifiers\
**Antibody Format:** Paired variable domains in the declared assay construct\
**Objective:** Computational affinity ranking and improved-variant prioritization

## Design Constraints

- Verify every variant sequence, parent assignment, antigen construct and structural template before scoring.
- Preserve supplied candidate sequences and evaluate all variants under the same preparation and scoring definitions.
- Declare score direction, candidate eligibility and shortlist size before evaluation. Freeze computational scores before joining experimental labels.
- Evaluate each assay independently and retain its measurement units, transformations and matched parent. Keep Kd and enrichment endpoints separately identified.

## Evaluation Metrics

| Criterion | Measurements and Evidence | Evaluation Rule |
| --- | --- | --- |
| Affinity ranking | Within-assay Spearman ρ | Use consistently oriented computational scores and the assay-specific experimental label. |
| Improvement selection | Fivefold Precision@k at k=10,20,50,100 for eligible panels | Define a hit by measured Kd ≤ matched-parent Kd / 5 and retain the declared selected population. |
| Aggregate performance | Equal-assay correlation/precision summaries and confidence intervals | Identify contributing assays, evaluated counts and the uncertainty procedure. |
| Evidence completeness | Per-candidate scores, method and scoring status | Retain every scheduled variant and its evaluation outcome. |

Source references: [AbBiBench manuscript v3, 3 November 2026](https://arxiv.org/html/2506.04235v3), [released data](https://huggingface.co/datasets/AbBibench/Antibody_Binding_Benchmark_Dataset), [MSBMI-SAFE/AbBiBench @ `85645eaa9441`](https://github.com/MSBMI-SAFE/AbBiBench/tree/85645eaa94418034ee6ef6e21666b683c142fa02).

Computational reference: [task-specific benchmark](../../benchmark/monoclonal_antibody_design/task_019_abbibench_antibody_affinity_ranking.md).

## Expected Output

**Format:** `antibody_assessment_bundle`\
**Directory:** `affinity_ranking_results/`

- `predictions.csv`: computational scores for every supplied candidate, with method, score direction and evaluation status.
- `shortlist.csv`: ranked candidate pairs, selection criteria, parent differences and exclusion reasons.
- `metrics.json`: actual computational values, metric definitions, structural scope, units, candidate hashes and provenance.
- `benchmark_comparison.csv`: published computational reference values and executed results, with their respective scopes.
- `report.md`: scientific rationale, supported conclusions and candidate-specific evidence; include structures, chain/residue maps and raw scoring outputs.

## Important Instructions

- Select methods independently within the user's access and computational constraints; no particular workflow is required.
- Report missing essential inputs as `NEEDS_INPUT`. Record the exact target construct, reference sequence, editable regions or candidate panel, methods and evaluation settings used.
- Use source experimental labels only to evaluate the frozen ranking.
- Predictive ranking performance does not assign a measured affinity to a newly generated sequence.
