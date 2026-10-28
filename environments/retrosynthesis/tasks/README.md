# Task definitions and outputs

`aspirin-inventory.json` is the public target/inventory example, byte-identical to `examples/aspirin_task.json`. It is a planning input, not an experimentally verified route. The fixture leaves material quantities, prices and supporting evidence unknown. Configure a compatible proposal backend before running local search.

```sh
retrosynthesis plan --task tasks/aspirin-inventory.json --search-policy synthchem_portfolio --repo-root "$REBOLT_ROOT" --chemistry-python "$REBOLT_PYTHON" --output artifacts/reproduction/local-search.json
```

The executable [Task, RouteCandidate and RouteAssessment schemas](../src/synthesis_route_gym/schemas.py) define accepted inputs and outputs. Unknown scientific values are null, predictions remain labelled, and submitted candidates remain pending chemical review. No expected held-out answer or final evaluator label is distributed here.

For a fully offline executable check, run `python examples/base_demo.py` from the environment root. It returns a synthetic import report, validation findings, ranking and explicit submission. `claims_experimental_validation` must be false; assessment `solved` remains false. The inventory/process/biocatalysis replay triples under `examples/applications/` cover additional action contracts.

Budgeted tasks require finite positive aggregate resource limits. For an explicit unbudgeted task set `budget.regime` to `unbudgeted` and each of `max_actions`, `max_expansions`, `max_wall_seconds`, `max_llm_tokens` to null. Keep `top_k` finite. Per-call operational timeouts may still apply and must be recorded.
