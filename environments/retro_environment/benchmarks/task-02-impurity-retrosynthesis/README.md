# Task 02 — impurity and parent ibuprofen benchmark evidence

[Task and targets](../../tasks/task-02-impurity-retrosynthesis/README.md) · [Results](../../results/task-02-impurity-retrosynthesis/README.md) · [Canonical benchmark](../../benchmark/task-02-impurity-retrosynthesis/README.md)

## Literature and reference dataset

The existing [paper and patent catalog](../../benchmark/task-02-impurity-retrosynthesis/papers.md) identifies sources, exact-product versus class-level matches, examples and unresolved references. Direct literature descriptions for impurity A include CN108794319B and WO2003043625A1; source and translation limitations are documented there. M-related analogies do not establish an OH-retaining exact route.

The [recovered parent comparison](../../results/task-02-impurity-retrosynthesis/racemic_ibuprofen_comparison.md) maps seven historical computational routes to US3385886A Example 4, EP0337803A1 and US5166418A. It reports one analogous and one indirect multi-operation comparison among 25 step comparisons; the remaining 23 were not assessed across the full literature. These are distinct from impurity A/M.

## Method and comparison criteria

Use the same molecular identity, stereochemical/form definition, starting-material boundary, isolation and analytical specification before comparing performance. [A/M metrics](../../benchmark/task-02-impurity-retrosynthesis/achieved_metrics.json), [screening summary](../../results/task-02-impurity-retrosynthesis/screening_summary.json) and [route inventory](../../results/task-02-impurity-retrosynthesis/screening_routes.csv) preserve available counts and missing evidence. [Recovered parent data](../../results/task-02-impurity-retrosynthesis/racemic_ibuprofen_recovered.json) preserve route/step records. Class overlap, model scores and patent yields from different substrates or boundaries do not establish route success or superiority. No project-measured yield, purity or defensible INR cost is available.

See the [structured comparison](../../results/task-02-impurity-retrosynthesis/comparison_report.md) and [improvement plan](../../results/task-02-impurity-retrosynthesis/gaps_and_improvement_plan.md).
