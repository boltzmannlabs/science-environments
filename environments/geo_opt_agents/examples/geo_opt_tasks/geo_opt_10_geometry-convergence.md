# Task: geo_opt_10_geometry-convergence

## Description

Classify energy, gradient, displacement, and stopping-criterion evidence.

## Target

- Agent ID: `10`
- Task ID: `live_convergence`
- Input: `tasks/agent_inputs/agent_10_live_convergence.json`

## System input

- Method/basis: `B3LYP/6-31G*`
- Charge/multiplicity: `0/1`
- Backend: `PySCF + GPU4PySCF` when live execution is available
- Frozen packet: `tasks/agent_inputs/agent_10_live_convergence.json`

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
- Execution: `live_gpu_engine`
- Energy: `-76.407024051240 Hartree`; max gradient: `2.588e-05 Hartree/Bohr`; backend: `GPU4PySCF+SciPy-BFGS`.

Detailed evidence: [`geo_opt_10_geometry-convergence.md`](../geo_opt_results/geo_opt_10_geometry-convergence.md)
