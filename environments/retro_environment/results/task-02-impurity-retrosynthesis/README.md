# Task 02 results — impurity retrosynthesis

## Recovery update — supersedes earlier missing-artifact statements

The prior retro_case execution artifacts have now been recovered: parent racemic ibuprofen has **7 routes and 25 reaction-node comparisons**, distinct from the A/M subset. Comparator patents are US3385886A Example 4, EP0337803A1 and US5166418A; no measured superiority was found. See the recovered parent comparison and JSON linked from the Task-02 results index. Earlier owner-confirmed/unlinked wording below is a historical state, not current availability.


[Task definition](../../tasks/task-02-impurity-retrosynthesis/README.md) · [Literature benchmark](../../benchmarks/task-02-impurity-retrosynthesis/README.md) · [Structured comparison](comparison_report.md)

## Output inventory

| File | Actual content / evidence status |
|---|---|
| [screening_summary.json](screening_summary.json) | Derived A/M counts: 12/7 paths, 38/21 reaction nodes, 12/7 root matches; no exported citations/procedures. No new model run was performed for folder integration. |
| [screening_routes.csv](screening_routes.csv) | Every available original A/M route ID, counts, flags and uncalibrated model ranking field; all paths held pending evidence. |
| [case_studies.json](case_studies.json) | A/M artifact-backed completion; recovered parent-racemate derivative; original osimertinib identity proposal separately held. |
| [achievements_and_comparison.md](achievements_and_comparison.md) | Target-specific observations and comparison with literature, without claiming improved experimental performance. |
| [gaps_and_improvement_plan.md](gaps_and_improvement_plan.md) | Prioritized evidence/chemistry/process gaps and requirements for an actual literature-superiority claim. |
| [recovery_and_comparison_protocol.md](recovery_and_comparison_protocol.md) | Historical recovery protocol; its earlier missing-artifact status is superseded by the linked recovered parent records below. |
| [task_record.json](task_record.json) | Standardized task ID and cross-folder artifact links; expected reproducibility and validation state. |
| [benchmark metrics](../../benchmark/task-02-impurity-retrosynthesis/achieved_metrics.json) | Computational metrics and separately labelled literature-reported values; absent measured metrics are null. |

## What was obtained

19 A/M model paths (59 reaction nodes) were accounted for; provisional target roots matched. The audit exposed missing step evidence, unspecified conditions and listed atom-source gaps. Literature shows direct A syntheses but only class/topology overlap with specific model paths. M cyanohydrin/deoxygenation literature does not prove OH-retaining target synthesis. No measured isolated yield, purity, cost, waste or scale-up improvement was achieved. Separately recovered parent-racemate results contain 7 routes and 25 step comparisons. The parent racemate is not impurity A's racemic meta-isomer.

## Experimental results

No physical synthesis, measured batch outcomes or validated analytical result are present in this evidence package. The benchmark's patent yields are external reported results, not executed experiments. Add future authorized experimental data as a new dated artifact, with protocol, source and comparator linkage; do not overwrite predictions with observations. Credentials, local home paths, signed storage URLs and raw account exports remain excluded.

## Recovered outputs

- [Parent racemic-ibuprofen comparison](racemic_ibuprofen_comparison.md): all seven route lengths and primary-source mapping.
- [Recovered full parent audit JSON](racemic_ibuprofen_recovered.json): seven route records, 25 step comparisons, source fingerprints and explicit missing measured metrics.
