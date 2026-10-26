# Task: geo_opt_16_runtime-resource-recovery

## Description

Diagnose runtime, memory, checkpoint, and resumability failures without silent setting changes.

## Target

- Agent ID: `16`
- Task ID: `resource_recovery`
- Input: `tasks/agent_inputs/agent_16_resource_recovery.json`

## System input

- Method/basis: `B3LYP/6-31G*`
- Charge/multiplicity: `0/1`
- Backend: `PySCF + GPU4PySCF` when live execution is available
- Frozen packet: `tasks/agent_inputs/agent_16_resource_recovery.json`

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

Detailed evidence: [`geo_opt_16_runtime-resource-recovery.md`](../geo_opt_results/geo_opt_16_runtime-resource-recovery.md)
