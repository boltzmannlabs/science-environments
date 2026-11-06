# Achieved outputs and literature comparison

Generated from the checked-in route summary, selected-route audit and reference catalog. No new platform or laboratory runs were performed.

## What we achieved

| Metric | Observed/derived value | Interpretation |
|---|---|---|
| Generated routes | 16 | Model candidates, not validated syntheses |
| Reaction-node occurrences across all routes | 56 | Includes chemistry repeated in different routes |
| Separately checked routes / steps | 1 / 3 | Only top0 |
| Expected product ranked first in top0 | 2/3 (66.67%) | Model agreement only, not experimental accuracy |
| Exact target experimental preparations performed | 0 | No laboratory result |
| Exact target literature routes established | 0 | Search limitation; not proof of absence |
| Measured target yield, selectivity; literature yield error | Not available | No matched comparison possible |

## All-route numerical comparison

The percentage product below multiplies step model yields under an illustrative sequential assumption. Branch topology, stoichiometry, purification losses and calibration are not captured. It must not be called an achieved synthetic yield.

| Route | Explicit steps | Predicted step yields (%) | Illustrative product (%) 
|---|---:|---|---:|---|
| top0 | 3 | 72.83, 58.81, 72.16 | 30.91 |
| top1 | 3 | 75.23, 67.22, 77.41 | 39.15 |
| top2 | 3 | 78.14, 55.25, 78.01 | 33.68 |
| top3 | 4 | 60.19, 82.53, 43.83, 68.44 | 14.90 |
| top4 | 4 | 77.30, 69.41, 67.20, 52.81 | 19.04 |
| top5 | 3 | 77.30, 51.73, 51.08 | 20.43 |
| top6 | 2 | 60.19, 49.44 | 29.76 |
| top7 | 3 | 59.75, 69.51, 75.55 | 31.38 |
| top8 | 5 | 77.30, 70.90, 74.74, 48.42, 61.63 | 12.23 |
| top9 | 4 | 69.41, 69.88, 77.30, 52.63 | 19.73 |
| top10 | 4 | 51.22, 71.82, 72.08, 65.11 | 17.26 |
| top11 | 3 | 73.33, 53.83, 72.57 | 28.64 | 
| top12 | 3 | 68.65, 60.09, 74.79 | 30.85 | 
| top13 | 5 | 66.71, 51.48, 65.95, 70.94, 58.26 | 9.36 |
| top14 | 3 | 62.48, 50.08, 68.73 | 21.51 |
| top15 | 4 | 77.30, 74.51, 76.34, 49.63 | 21.82 |

## Tool versus literature: selected route

| Step | Tool output (model-only) | Literature comparator | Conclusion |
|---|---|---|---|
| 1: TBS protection | Forward score 0.999999812; mapping confidence 0.27964; condition-tool yield 81.26%; TBAF/THF, 20–30 °C | [L1](../benchmark/papers.md): protection class only; no same-substrate yield extracted | Reject fluoride condition for forming/retaining TBS ether. High score did not establish compatible conditions. |
| 2: aryl ether formation | Protected product ranked last, forward score 0; mapping confidence 0.21971; condition-tool yield 77.94%; pyridine/THF, no coupling catalyst | [L2](../benchmark/papers.md): Ullmann-type diaryl-ether class only; exact pairing not established | Unresolved central step; model yield not credible evidence of feasible coupling. |
| 3: deprotection | Forward score 0.999999837; mapping confidence 0.66765; condition-tool yield 62.02%; TBAF/THF, 20–30 °C | [L3](../benchmark/papers.md): TBAF/THF, 0 °C to room temperature, 45 min; 32% isolated yield for a DIFFERENT compound | Plausible class analogy only; 62.02% versus 32% is NOT a matched yield improvement. |

The condition-tool yields above are a different prediction output from the retrosynthesis step-yield fields in the all-route table; they are not substituted into one another.

## What was not achieved

No matched experimental accuracy, yield improvement, selectivity improvement, purity improvement, cost advantage or calibrated uncertainty was established. Literature sources support reaction-family context rather than an exact complete route. Starting-material availability and target-route practicality remain unverified.

## Source files

- [All routes](route_summary.json)
- [Selected-route tool audit](top0_validation.json)
- [Numeric CSV](route_yield_comparison.csv)
- [Metric definitions and values](../benchmark/achieved_metrics.json)
- [Literature catalog](../benchmark/papers.md)
- [Existing DOCX structure report](retro_benchmark_report.docx)
