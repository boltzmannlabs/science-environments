# Task: geo_opt_13_hessian-minimum-verification

## Description

Distinguish a local minimum from a saddle point using Hessian or frequency evidence.

## Target

- Agent ID: `13`
- Task ID: `minimum_verification`
- Input: `tasks/agent_inputs/agent_13_minimum_verification.json`

## System input

- Method/basis: `B3LYP/6-31G*`
- Charge/multiplicity: `0/1`
- Backend: `PySCF + GPU4PySCF` when live execution is available
- Frozen packet: `tasks/agent_inputs/agent_13_minimum_verification.json`

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
- Execution: `live_hessian_engine`
- Energy: `-76.399135351468 Hartree`; max gradient: `0.000e+00 Hartree/Bohr`; backend: `PySCF CPU Hessian`.

Detailed evidence: [`geo_opt_13_hessian-minimum-verification.md`](../geo_opt_results/geo_opt_13_hessian-minimum-verification.md)
