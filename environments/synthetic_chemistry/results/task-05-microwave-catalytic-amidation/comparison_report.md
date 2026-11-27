# Task 05 — prediction versus literature comparison

[Task](../../tasks/task-05-microwave-catalytic-amidation/README.md) · [Benchmark](../../benchmarks/task-05-microwave-catalytic-amidation/README.md) · [Results inventory](README.md)

## Comparison basis

The internal condition tool produced ten recommendations for the illustrative hindered pair (2,6-dimethylaniline + 2-methylbenzoic acid). These were compared with five verified contextual literature sources (L1–L5) and with the task's own catalytic-microwave constraints. The designated 2025 HTE paper is not identified; therefore this is a criteria audit plus contextual comparison, not a scored paper-specific evaluation.

## Constraint and criterion comparison

| Criterion | Task requirement | Tool output | Status |
|---|---|---|---|
| Reaction identity | aryl amine + aryl acid to amide | illustrative pair preserved | PARTIAL — illustrative, not designated matrix |
| Catalyst | `catalyst_required: true` | `catalyst_name: []` in all ten candidates | FAIL |
| Heating mode | microwave | not returned | NOT EVALUABLE / FAIL |
| Reaction time | explicit microwave time | not returned | NOT EVALUABLE |
| Solvents | rank top three under comparable settings | pyridine, dioxane, DCM reagent sets | NOT EVALUABLE — no catalytic basis |
| Yield | comparable predicted yields | 53.52–60.67%, five repeated values across ten rows | NOT EVALUABLE — condition-invariant estimates |
| Side products | at least one reported product predicted | none returned | NOT EVALUABLE |
| Optimum in top 5 | designated experimental optimum | ground truth withheld | NOT EVALUABLE |

## Literature comparison

- The top-ranked bare-pyridine, room-temperature, catalyst-free direct amidation is not the approach used by the verified catalytic literature. L1 uses CAN in an open microwave reactor under solvent-free conditions; L2 uses a borate ester in tert-butyl acetate (thermal, 20 h) and explicitly addresses poorly nucleophilic/hindered anilines; L3 uses borane–pyridine at 5 mol%. [1][2][3]
- The product class is chemically precedented: anilides of 2,6-dimethylaniline appear in a Cu-coupling ligand paper and in the stable anticonvulsant D2624, which hydrolyses to 2,6-dimethylaniline. These confirm a sensible target structure, not a viable route under the tool's rank-1 conditions.[6][7]
- Several returned candidates are chemically questionable (HCl with amines/pyridine; K2CO3 + HCl in one pot). Their "validation_reason" strings are model self-justifications, not literature evidence.
- The predicted yields cannot be validated: no retrieved source reports a yield for this exact pair. The repetition of identical yields across chemically different conditions indicates substrate-typical estimation rather than condition-resolved prediction.

## Local optimizer comparison

A catalytic design campaign compiled 192 candidates from verified catalyst families and solvent/temperature/time grids; eight diverse initial designs were selected, a persistent campaign was created and four experiments reserved with zero measurements. Earlier model-predicted yields were then seeded as `excluded`, QC-flagged priors — logged and blocked from re-selection, but never treated as reviewed measurements. Eight further untested conditions were selected. No Bayesian fit occurred because zero reviewed measured candidates exist; no candidate can be called optimal.

## Quantitative metrics

All experimental comparison fields are `null` in [achieved_metrics.json](../../benchmarks/task-05-microwave-catalytic-amidation/achieved_metrics.json): no project-measured yield, matched literature yield, MAE, optimum retrieval, solvent ranking, steric-class floor, time comparison or impurity match. Model scores are not percentages; heuristic design scores are not yields.

## Sources

[1] https://doi.org/10.3390/molecules25081761
[2] https://doi.org/10.1039/d4sc07744j
[3] https://doi.org/10.3390/molecules29010268
[4] https://doi.org/10.1039/D3RA03300G
[5] https://pmc.ncbi.nlm.nih.gov/articles/PMC13449423
[6] https://pubmed.ncbi.nlm.nih.gov/29786439
[7] https://pubmed.ncbi.nlm.nih.gov/9010628
