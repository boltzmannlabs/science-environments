# Result: geo_opt_09_scf-convergence

## Description

Diagnose SCF failures and propose bounded recovery settings without changing the state silently.

## System input

- Task ID: `09` / `scf_failure`
- Input fixture: `tasks/agent_inputs/agent_09_scf_failure.json`
- Method/basis: `B3LYP/6-31G*`
- Charge/multiplicity: `0/1`
- Backend: `PySCF + GPU4PySCF` when live execution was used
- Acceptance criteria: finite coordinates, finite energy, verified convergence where applicable

## Expected output

- decision
- scientific checks
- evidence references
- failure category
- cost and reproducibility fields

## Observed result

- Status: **pass**
- Execution: `deterministic_fixture`
- Fixture decision target: `review`; deterministic checks recorded.

## Limitations and review notes

This is a deterministic contract/fixture evaluation, not a completed production optimization.
The result is scoped to this frozen input packet and does not claim capabilities outside the agent contract.
