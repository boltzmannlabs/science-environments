# Task 05 — saved microwave catalytic amidation results

[Task and inputs](../../tasks/task-05-microwave-catalytic-amidation/README.md) · [Literature benchmark](../../benchmarks/task-05-microwave-catalytic-amidation/README.md) · [Focused comparison](comparison_report.md)

## Output inventory

| File | Content | Provenance |
|---|---|---|
| [task_record.json](task_record.json) | Schema version, task ID, linked definitions, evidence scope and artifact list | Session-generated from recorded tool trace |
| [condition_summary.json](condition_summary.json) | Ten sanitized condition recommendations and constraint audit | Derived from completed internal job |
| [optimizer_campaigns.json](optimizer_campaigns.json) | Catalytic campaign, persistent reservation and QC-flagged prior-yield seed | Local `reaction-optimize` executions |
| [comparison_report.md](comparison_report.md) | Criteria audit and contextual literature comparison | Post hoc, blind-stage data only |
| [achievements_and_comparison.md](achievements_and_comparison.md) | Objective-by-objective achievements and limitations | Post hoc |
| [gaps_and_improvement_plan.md](gaps_and_improvement_plan.md) | Performance gaps, reasons and next steps | Post hoc |
| [run_log.md](run_log.md) | Ordered tool-call log with validation and rejection statuses | Derived from tool trace |
| [validation_receipt.md](validation_receipt.md) | Structure, link and hygiene checks | Packaging-time validation |
| [summary.md](summary.md) | Comprehensive all-outcomes summary, consolidated literature comparison, metrics, gaps and improvements | Consolidated post hoc from all artifacts above |

## Actual achievements

One internal condition job was submitted once and polled to completion, returning ten conditions with native predicted yields of 53.52–60.67%. Every candidate had an empty catalyst name and no microwave mode or time, so the output fails the catalytic requirement. Five contextual literature sources were retrieved and verified. The local optimizer compiled 192 catalytic candidates, selected eight diverse designs, created a persistent campaign with four reserved experiments and zero measurements, then seeded earlier predicted yields as `excluded`, QC-flagged priors and selected eight further untested conditions. No Bayesian fit occurred.

## Limitations

No experimental yield, matched literature yield, MAE, optimum retrieval, solvent ranking, steric-class floor, time objective or impurity match exists. The designated 2025 HTE paper remains unidentified. The optimizer's heuristic scores are not calibrated yields; model predictions are not measurements. Raw service exports, signed URLs, credentials and personal paths are not redistributed.
