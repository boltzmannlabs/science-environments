# Task: geo_opt_18_geo-opt-orchestrator

## Description

Route cases conditionally, manage retries, and consolidate an auditable workflow trace.

## Target

- Agent ID: `18`
- Task ID: `orchestration`
- Input: `tasks/agent_inputs/agent_18_orchestration.json`

## System input

- Method/basis: `B3LYP/6-31G*`
- Charge/multiplicity: `0/1`
- Backend: `PySCF + GPU4PySCF` when live execution is available
- Frozen packet: `tasks/agent_inputs/agent_18_orchestration.json`

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

Detailed evidence: [`geo_opt_18_geo-opt-orchestrator.md`](../geo_opt_results/geo_opt_18_geo-opt-orchestrator.md)
