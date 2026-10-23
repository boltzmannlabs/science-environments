# Task: geo_opt_05_qm-method-selection

## Description

Select supported DFT method, basis, and settings with a reproducible rationale.

## Target

- Agent ID: `05`
- Task ID: `method_selection`
- Input: `tasks/agent_inputs/agent_05_method_selection.json`

## System input

- Method/basis: `B3LYP/6-31G*`
- Charge/multiplicity: `0/1`
- Backend: `PySCF + GPU4PySCF` when live execution is available
- Frozen packet: `tasks/agent_inputs/agent_05_method_selection.json`

## Required inputs

- finite_coordinates
- finite_energy
- convergence_must_be_verified

## Expected output

- decision
- scientific checks
- evidence references
- failure category
- cost and reproducibility fields

## Acceptance criteria

- all mandatory checks are explicit
- no unsupported scientific claim
- settings and artifacts are hashable
- decision is reproducible

## Observed benchmark result

- Status: **pass**
- Execution: `deterministic_fixture`
- Fixture decision target: `review`; deterministic checks recorded.

Detailed evidence: [`geo_opt_05_qm-method-selection.md`](../geo_opt_results/geo_opt_05_qm-method-selection.md)
