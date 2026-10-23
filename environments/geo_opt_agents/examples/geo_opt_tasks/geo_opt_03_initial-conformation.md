# Task: geo_opt_03_initial-conformation

## Description

Detect distorted starting geometries, steric clashes, and poor conformers before optimisation.

## Target

- Agent ID: `03`
- Task ID: `distorted_start`
- Input: `tasks/agent_inputs/agent_03_distorted_start.json`

## System input

- Method/basis: `B3LYP/6-31G*`
- Charge/multiplicity: `0/1`
- Backend: `PySCF + GPU4PySCF` when live execution is available
- Frozen packet: `tasks/agent_inputs/agent_03_distorted_start.json`

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
- Fixture decision target: `repair_or_review`; deterministic checks recorded.

Detailed evidence: [`geo_opt_03_initial-conformation.md`](../geo_opt_results/geo_opt_03_initial-conformation.md)
