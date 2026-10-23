# Task: geo_opt_15_protein-ligand-geometry

## Description

Check ligand clashes, binding-site geometry, coordination, and interaction preservation.

## Target

- Agent ID: `15`
- Task ID: `protein_ligand`
- Input: `tasks/agent_inputs/agent_15_protein_ligand.json`

## System input

- Method/basis: `B3LYP/6-31G*`
- Charge/multiplicity: `0/1`
- Backend: `PySCF + GPU4PySCF` when live execution is available
- Frozen packet: `tasks/agent_inputs/agent_15_protein_ligand.json`

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
- Execution: `live_qmmm_engine`
- Fixture decision target: `accept`; deterministic checks recorded.

Detailed evidence: [`geo_opt_15_protein-ligand-geometry.md`](../geo_opt_results/geo_opt_15_protein-ligand-geometry.md)
