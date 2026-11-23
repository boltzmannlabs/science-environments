# Task 01 — evidence-tiered route comparison

[Task and target](../../tasks/task-01-fluorinated-quinoline-retrosynthesis/README.md) · [Benchmark and primary references](../../benchmarks/task-01-fluorinated-quinoline-retrosynthesis/README.md) · [All-route and stepwise data](README.md)

## Recorded output and evidence classes

The existing historical computation returned 16 model route proposals with 56 reaction-node occurrences; top0 alone received a separate three-step model review. [All steps and structures](route_summary.json) and [top0 audit](top0_validation.json) are sanitized derivatives, not raw service exports. No new platform job or laboratory synthesis was run for workspace organization. Literature sources supply reaction-family context; no exact complete target route was established in the limited search. No project-experimental target route is validated.

## Side-by-side assessment

| Aspect | Predicted / checked outcome | Literature or evidence comparison | Assessment |
|---|---|---|---|
| Selected-route product agreement | Expected product ranked first for 2 of 3 checked steps | Model-to-model check only, not a matched experiment | Better agreement on two steps; not a demonstrated literature improvement. |
| Central aryl ether | Expected protected product ranked last with model score zero; suggested conditions lacked a suitable coupling catalyst | Diaryl-ether family reference, not the exact substrate pair | Under-supported central transformation; rank/condition disagreement requires further evidence, not a claim of experimental failure. |
| Silyl protection and removal | Formation suggestion included fluoride; deprotection also used fluoride | Different-substrate TBS-deprotection example | Fluoride can oppose TBS retention, so the protection recommendation is internally inconsistent; class analogy does not validate the full route. |
| Other route proposals | Fifteen additional model trees are preserved | No exact-target complete literature route established in screened sources | Alternatives are computational proposals; feasibility, selectivity and conditions remain unverified. |

[Detailed original comparison](achievements_and_comparison.md) supplies all model-only numbers and source links. Predicted step yields or their illustrative product cannot be compared as measured target yield against another substrate's 32% reported deprotection yield.

## Reasons, limitations and next evidence

Protecting-group incompatibility and lack of a specified coupling catalyst are concrete issues in the saved condition suggestions. Substrate-dependent reactivity and competing pathways could affect selectivity, but the current evidence does not establish their magnitude. Search coverage, available starting materials, model version and ranking calibration are incomplete; no causal claim about the model's search algorithm is supported. Improve the audit with an exact-structure literature search, independently checked precursor identity and condition compatibility, then qualified prospective experimental evaluation if authorized. No measured yield, selectivity, cost advantage or superiority is demonstrated.
