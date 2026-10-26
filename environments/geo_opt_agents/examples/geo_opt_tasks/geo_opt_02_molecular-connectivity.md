# Task: geo_opt_02_molecular-connectivity

## Description

Detect incorrect bonds, unusual valence, missing connectivity, and inconsistent bond orders.

## Target

- Agent ID: `02`
- Task ID: `connectivity_valence`
- Input: `tasks/agent_inputs/agent_02_connectivity_valence.json`

## System input

- Method/basis: `B3LYP/6-31G*`
- Charge/multiplicity: `0/1`
- Backend: `PySCF + GPU4PySCF` when live execution is available
- Frozen packet: `tasks/agent_inputs/agent_02_connectivity_valence.json`

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

Detailed evidence: [`geo_opt_02_molecular-connectivity.md`](../geo_opt_results/geo_opt_02_molecular-connectivity.md)
