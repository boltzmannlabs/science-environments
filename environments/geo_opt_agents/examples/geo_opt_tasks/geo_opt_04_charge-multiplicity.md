# Task: geo_opt_04_charge-multiplicity

## Description

Validate charge, electron count, spin multiplicity, and electronic-state settings.

## Target

- Agent ID: `04`
- Task ID: `charge_multiplicity`
- Input: `tasks/agent_inputs/agent_04_charge_multiplicity.json`

## System input

- Method/basis: `B3LYP/6-31G*`
- Charge/multiplicity: `0/1`
- Backend: `PySCF + GPU4PySCF` when live execution is available
- Frozen packet: `tasks/agent_inputs/agent_04_charge_multiplicity.json`

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

Detailed evidence: [`geo_opt_04_charge-multiplicity.md`](../geo_opt_results/geo_opt_04_charge-multiplicity.md)
