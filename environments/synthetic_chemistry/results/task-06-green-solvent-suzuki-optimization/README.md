# Task 06 — saved green-solvent Suzuki optimization results

[Task and inputs](../../tasks/task-06-green-solvent-suzuki-optimization/README.md) · [Literature benchmark](../../benchmarks/task-06-green-solvent-suzuki-optimization/README.md) · [Focused comparison](comparison_report.md) · [Comprehensive summary](summary.md)

## Comprehensive summary

[summary.md](summary.md) consolidates all executed stages, comparison tables against literature, improvements, gaps, reasons for underperformance, key metrics, limitations and next steps.

## Output inventory

| File | Content | Provenance |
|---|---|---|
| [task_record.json](task_record.json) | Schema, task ID, linked definitions, evidence scope and artifact list | Session-generated from recorded tool trace |
| [run_log.md](run_log.md) | Ordered tool-call log with job IDs, statuses and errors | Derived from tool trace |
| [structure_validation.json](structure_validation.json) | RDKit parse/canonicalization of 17 structures | Local RDKit |
| [forward_predictions.json](forward_predictions.json) | Boltzmann forward top candidates and scores | Job `6b058889c45f4015f0eb48b3` |
| [condition_candidates.json](condition_candidates.json) | Condition recommendation attempts including failed job | Jobs `6b0588c27fb17f3eac9cb206`, `6b07cb3fb5e9e7e2abe1fade` |
| [impurity_candidates.json](impurity_candidates.json) | Impurity candidates | Job `6b058ae6c45f4015f0eb48e1` |
| [optimizer_campaigns.json](optimizer_campaigns.json) | Local 480-candidate design batch and solvent-blind finding | `reaction-optimize` executions |
| [condition_recommendations.csv](condition_recommendations.csv) | 12 selected conditions with yield basis | Local optimizer |
| [solvent_predictions.csv](solvent_predictions.csv) | Available yield estimates and comparability status | Combined tool outputs |
| [green_tradeoffs.csv](green_tradeoffs.csv) | Yield, hazard, E-factor and duration trade-offs | Literature + scenario |
| [impurity_shifts.csv](impurity_shifts.csv) | Qualitative directions with reference IDs | Model candidates + evidence boundary |
| [comparison_report.md](comparison_report.md) | Quantitative comparison with literature | Post hoc, after freeze |
| [achievements_and_comparison.md](achievements_and_comparison.md) | Objective-by-objective achievements and limitations | Post hoc |
| [gaps_and_improvement_plan.md](gaps_and_improvement_plan.md) | Gaps, reasons and next steps | Post hoc |
| [summary.md](summary.md) | Consolidated outcomes, comparison tables, improvements, gaps and future work | Post hoc, all stages |

## Actual achievements

Seventeen structures validated; 55 retrosynthesis routes with the correct top route; exact forward target-string match (score ~1.0); local optimizer compiled 480 candidates and a 12-run diverse batch covering DES 1:2/1:4/1:8, all greener media and conventional controls; 13 frozen yield estimates generated; E-factor scenario computed (22.54 at 0% recovery, 3.29 at 95%). No solvent ranking, matched MAE, green-vs-conventional yield claim, impurity direction, selected protocol or measured E-factor was obtained.

## Limitations

Available yield models do not encode solvent, temperature or time; the Boltzmann condition tool accepts only SMILES; no curated experimental recipe matched the exact pair; no reviewed laboratory measurements exist for Bayesian fitting; hazard classification and mass-balance data are incomplete; full blinding was compromised by user-reported yields disclosed before the runs. Raw service exports, signed URLs, credentials and personal paths are not redistributed.
