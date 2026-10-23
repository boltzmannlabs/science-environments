# GeoOpt-Bench v0.1 specification

## Evaluation arms

1. General workflow baseline
2. General workflow with the declared specialist
3. Conditional specialist routing based on diagnostics

The same frozen task cards, input hashes, scoring rules, resource limits, and
repeats must be used in all arms. No arm may access reference answers or the
grader internals.

## Scoring

Scientific correctness is scored independently for structure validity,
convergence classification, finite energy and gradients, stopping-criterion
compliance, constraint compliance, and stationary-point evidence. Reliability
records completion, recovery, and repeat agreement. Efficiency records wall
time, retries, tokens, API calls, and compute cost. A pass requires all
mandatory scientific checks; lower energy alone is never sufficient.

## Failure categories

`input_invalid`, `connectivity_invalid`, `electronic_state_invalid`,
`method_unsupported`, `scf_failure`, `optimizer_stagnation`,
`geometry_unconverged`, `gradient_invalid`, `constraint_violation`,
`not_a_minimum`, `resource_failure`, `reporting_error`, and `review_required`.

## Reproducibility

Each submission records the task hash, settings hash, initial/final geometry
hashes, engine/version, random seed, repeat index, wall time, token/API usage,
retry trace, and artifact hashes. Historical SPE evidence is outside this
benchmark and is not modified.
