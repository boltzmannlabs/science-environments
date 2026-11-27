# Task 04 — saved blind-optimization results

[Task and inputs](../../tasks/task-04-pdnhc-suzuki-miyaura-optimization/README.md) · [Literature benchmark](../../benchmarks/task-04-pdnhc-suzuki-miyaura-optimization/README.md) · [Focused comparison](comparison_report.md) · [Comprehensive summary](comprehensive_summary.md)

> **Start here for the full overview:** [comprehensive_summary.md](comprehensive_summary.md) consolidates every run, comparison table, metric, gap and next step.

## Output inventory

| File | Content | Provenance |
|---|---|---|
| [task_record.json](task_record.json) | Schema version, task ID, linked definitions, evidence scope and artifact list | Session-generated from recorded tool trace |
| [prediction_summary.json](prediction_summary.json) | Sanitized product, route, condition, side-product, Parrot and loading-run summaries | Derived from frozen report; no credentials or signed URLs |
| [pdnhc_loading_candidates.csv](pdnhc_loading_candidates.csv) | Pd-NHC candidates, bases, loadings, temperatures and frozen-model yields | Loading-aware local optimizer run |
| [comparison_report.md](comparison_report.md) | Structured predictions-vs-expectation tables and quantitative metrics | Post hoc, blind-stage data only |
| [achievements_and_comparison.md](achievements_and_comparison.md) | Objective-by-objective achievements and limitations | Post hoc |
| [gaps_and_improvement_plan.md](gaps_and_improvement_plan.md) | Performance gaps, reasons and next steps | Post hoc |
| [run_log.md](run_log.md) | Ordered tool-call log with validation and failure statuses | Derived from tool trace |
| [comprehensive_summary.md](comprehensive_summary.md) | Consolidated outcomes, comparisons, metrics, gaps and next steps | Post-hoc synthesis of all recorded outputs |

## Actual achievements

The top-ranked forward prediction matched the structural target exactly (model score 1.0, feasibility 0.9934). Five route proposals and nine canonical side-product classes were retained. Ten internal conditions were returned after three HTTP 429 failures; the selected high-temperature aqueous-dioxane condition had a native predicted yield of 32.338% and feasibility 0.78. A reversed-order probe was rejected as chemically invalid despite higher nominal yields. The local optimizer produced eight Pd-NHC design candidates; a loading-aware rerun encoded 0.5/2/5 mol% loading and yielded nine frozen-model predictions. A persistent campaign was created with one six-experiment reservation, but no measurements were entered.

## Limitations

No experimental yield, matched literature yield, MAE, loading-retention value or best-catalyst validation exists. The frozen yield advisor ignores loading, so it cannot support reduced-loading retention claims. Parrot predictions lacked Pd and were not adopted. Model scores are not experimental probabilities. Raw service exports, personal paths and signed URLs are not redistributed.
