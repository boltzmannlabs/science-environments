# Task: fep_ag10_adaptive_sampling

## Description

Allocate additional replicas, windows, or trajectory length to the measured sources of uncertainty under a fixed compute budget.

## Dataset and inputs

- Overlap/convergence reports, window costs, available budget, and immutable baseline manifest

## Tools to use

Evidence-ranked prioritizer, budget checker, provenance logger, and before/after evaluator.

## Expected outputs

`sampling_plan.json` with ranked actions, expected diagnostic benefit, budget, and stopping rules.

## Acceptance and limitations

PASS requires an auditable allocation rationale and no silent protocol changes. Predicted benefit is not evidence until rerun.
