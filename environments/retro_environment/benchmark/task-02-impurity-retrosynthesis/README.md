# Task 02 benchmark — literature and achieved metrics

Task: [complete test case](../../tasks/task-02-impurity-retrosynthesis/README.md). Outputs: [result inventory](../../results/task-02-impurity-retrosynthesis/README.md).

## Comparator data

[Papers and patents](papers.md) lists all supplied references with URLs, verification status, exact-versus-analogue relevance, reported experiments and corresponding generated paths. It includes CN108794319B, WO2003043625A1, ACS Catalysis 2014, Synthesis 1983 fragment, Kuchar 1984 fragment, Bellezza 2005, Ramesh/Reddy 2007 fragment, Aramini 2009, WO2013014448A1 and Cross 2014. Unresolved references are not experimental ground truth.

CN108794319B reports example yields 82.3%, 60.3%, 95% and claimed final purity 99.8%; English-rendered examples have substrate-name and missing-reagent inconsistencies. WO2003043625A1 Example 8 names the racemic *meta-isobutyl* acid (impurity A), not parent para-isobutyl ibuprofen. Do not transfer Example 5's isopropyl result. WO2013014448A1 Example 59 reports 76 mg/27% for the name-matched AZ5104 N-H-indole product; not an independently established Impurity A designation and not a 100 g result. All are **literature-reported**, not measured in this project.

## Achieved computational metrics

| Metric | Impurity A | Impurity M |
|---|---:|---:|
| Paths reviewed | 12 | 7 |
| Reaction-labelled nodes | 38 | 21 |
| Provisional target root matches | 12/12 | 7/7 |
| Nodes with exported traceable citation | 0/38 | 0/21 |
| Nodes with exported procedure | 0/38 | 0/21 |
| Nodes missing element source among listed inputs | 9 | 1 |
| Experimentally validated lead routes | 0 | 0 |
| Measured yield, purity, INR/100 g | Unavailable | Unavailable |

[achieved_metrics.json](achieved_metrics.json) preserves the counts and separately labels patent-reported values. Racemic parent metrics are null because its owner-confirmed run artifacts are not linked. These counts are inventory/structure checks, not success rates of synthesis.

## Evaluation rule

Compare the same product/form/stereochemical definition at the same starting-material boundary and isolated output specification. Class overlap (A top5 Suzuki, A top3 hydrogenation/hydrolysis, M top4 cyanohydrin) does not establish exact reaction precedent or performance superiority. No matched measured yield error, cost reduction, safe scale-up advantage or literature win is available. Prespecify performance goals and collect reproducible measured data as set out in the [improvement plan](../../results/task-02-impurity-retrosynthesis/gaps_and_improvement_plan.md).
