# Task: geo_opt_01_structure-input-validation

## Description

Validate molecular files, coordinates, elements, missing atoms, duplicates, and malformed structures.

## Target

- Agent ID: `01`
- Task ID: `malformed_structure`
- Input: `tasks/agent_inputs/agent_01_malformed_structure.json`

## System input

- Method/basis: `B3LYP/6-31G*`
- Charge/multiplicity: `0/1`
- Backend: `PySCF + GPU4PySCF` when live execution is available
- Frozen packet: `tasks/agent_inputs/agent_01_malformed_structure.json`

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
- Fixture decision target: `reject`; deterministic checks recorded.

Detailed evidence: [`geo_opt_01_structure-input-validation.md`](../geo_opt_results/geo_opt_01_structure-input-validation.md)
