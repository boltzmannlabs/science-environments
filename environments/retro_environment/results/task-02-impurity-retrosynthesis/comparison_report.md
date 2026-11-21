# Task 02 — evidence-tiered route comparison

[Task and target scope](../../tasks/task-02-impurity-retrosynthesis/README.md) · [Benchmark and references](../../benchmarks/task-02-impurity-retrosynthesis/README.md) · [Result inventory](README.md)

## Recorded output and evidence classes

Historical computational screening covers impurity A: 12 paths/38 reaction nodes; impurity M: 7 paths/21 nodes. The separately recovered parent racemic-ibuprofen run has seven paths/25 reaction-node comparisons. These are distinct targets; do not pool their counts. [A/M summary and route inventory](screening_summary.json) and [recovered parent records](racemic_ibuprofen_recovered.json) are sanitized derived evidence, not raw account exports. The original osimertinib proposal was held for identity reconciliation and has no generated route export in this snapshot.

## Comparisons and limitations

| Case | Model outcome | Literature comparison | Assessment |
|---|---|---|---|
| Impurity A | 12/12 provisional root matches; no traceable citation or procedure fields in 38 nodes | CN108794319B and WO2003043625A1 describe direct product syntheses; some model routes share reaction families or topology but differ in substrates or operations | Root matching is useful structural screening, not route validation. No demonstrated better or experimentally validated model route. |
| Impurity M | 7/7 provisional root matches; no traceable citation or procedure fields in 21 nodes | Cyanohydrin and related analogies do not prove formation of the OH-retaining target | Functional-group retention and selectivity remain unresolved; no validated lead or measured performance advantage. |
| Parent ibuprofen | Seven recovered model routes, 25 step comparisons | Inspected sources yielded one analogous and one indirect multi-operation analogy; 23 steps were not assessed across the full literature | No complete exact comparator or experimentally established advantage. Model alternatives remain unvalidated. |
| Across cases | No project-measured isolated yield, purity or INR cost | Patent-reported yields are external evidence and may not share substrate, scale or boundary | Better/underperformed experimental performance is not assessable; a numerical winner would be unsupported. |

Sources and detailed findings: [A/M comparison](achievements_and_comparison.md), [parent comparison](racemic_ibuprofen_comparison.md) and [paper catalog](../../benchmarks/task-02-impurity-retrosynthesis/papers.md). The parent recovery supersedes older unlinked-artifact statements in historical records.

## Scientific interpretation and next evidence

The saved audit identifies missing listed element sources in some model nodes; absent reactants or reagents in an incomplete record do not alone prove impossibility. Incomplete conditions, exact precursor identity, functional-group compatibility and impurity fate limit feasibility and selectivity assessment. Route rankings are uncalibrated model outputs; the available records do not establish why a particular route ranked higher or whether the search explored a literature route. Use a structure- and stereochemistry-matched literature review, resolve missing inputs, and independently test candidate reactions and analytics under appropriate authorization. The [gap plan](gaps_and_improvement_plan.md) records additional controls and cost-evidence requirements. No synthesis or claim of superiority is implied.
