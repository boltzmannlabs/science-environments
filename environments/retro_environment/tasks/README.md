# Tasks: objectives, expected outcomes and actual results

Target: `CC1=C(C=C2C=CC(=C(C2=N1)F)F)OC3=C(C(=CC=C3)F)C(C)(C)O`.

| Task | Work requested | Expected outcome | Actual status |
|---|---|---|---|
| [T001 Route generation](task_001_route_generation.md) | Generate and reconstruct candidate synthetic routes | Traceable reactants, intermediates, products and step counts | 16 model routes and 56 reaction occurrences archived; no actual synthesis |
| [T002 Selected-route validation](task_002_step_validation.md) | Evaluate top0 using forward, mapping, impurity and condition tools | Chemically supportable steps, or explicit failures | Three steps checked; central coupling unsupported; protection conditions contradictory |
| [T003 Literature benchmark](task_003_literature_benchmark.md) | Compare chemistry, selectivity, yields and practical evidence with public sources | Matched same-target route if available; otherwise evidence-tiered comparisons | Reaction-family references and an unrelated 32% yield example only; no same-target comparison established |

Success is an honest, reproducible audit including failures. The separate synth-test cinnamic-acid/diaminouracil reaction is outside these tasks. [Observed metrics](../benchmark/achieved_metrics.json) and [comparison tables](../results/achievements_and_comparison.md) record the outcomes.
