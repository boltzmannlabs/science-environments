# Task: geo_opt_08_constraints-boundaries

## Description

Validate fixed atoms, distances, restraints, and symmetry requirements.

## Target

- Agent ID: `08`
- Task ID: `constraint_validation`
- Input: `tasks/agent_inputs/agent_08_constraint_validation.json`

## System input

- Method/basis: `B3LYP/6-31G*`
- Charge/multiplicity: `0/1`
- Backend: `PySCF + GPU4PySCF` when live execution is available
- Frozen packet: `tasks/agent_inputs/agent_08_constraint_validation.json`

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
- Fixture decision target: `accept`; deterministic checks recorded.

Detailed evidence: [`geo_opt_08_constraints-boundaries.md`](../geo_opt_results/geo_opt_08_constraints-boundaries.md)
