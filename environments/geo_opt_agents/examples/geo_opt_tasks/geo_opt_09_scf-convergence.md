# Task: geo_opt_09_scf-convergence

## Description

Diagnose SCF failures and propose bounded recovery settings without changing the state silently.

## Target

- Agent ID: `09`
- Task ID: `scf_failure`
- Input: `tasks/agent_inputs/agent_09_scf_failure.json`

## System input

- Method/basis: `B3LYP/6-31G*`
- Charge/multiplicity: `0/1`
- Backend: `PySCF + GPU4PySCF` when live execution is available
- Frozen packet: `tasks/agent_inputs/agent_09_scf_failure.json`

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

Detailed evidence: [`geo_opt_09_scf-convergence.md`](../geo_opt_results/geo_opt_09_scf-convergence.md)
