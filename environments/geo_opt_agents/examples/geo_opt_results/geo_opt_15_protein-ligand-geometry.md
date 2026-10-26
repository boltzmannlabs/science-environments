# Result: geo_opt_15_protein-ligand-geometry

## Description

Check ligand clashes, binding-site geometry, coordination, and interaction preservation.

## System input

- Task ID: `15` / `protein_ligand`
- Input fixture: `tasks/agent_inputs/agent_15_protein_ligand.json`
- Method/basis: `B3LYP/6-31G*`
- Charge/multiplicity: `0/1`
- Backend: `PySCF + GPU4PySCF` when live execution was used
- Acceptance criteria: finite coordinates, finite energy, verified convergence where applicable

## Expected output

- decision
- scientific checks
- evidence references
- failure category
- cost and reproducibility fields

## Observed result

- Status: **pass**
- Execution: `live_qmmm_engine`
- Fixture decision target: `accept`; deterministic checks recorded.

## Limitations and review notes

This is a deterministic contract/fixture evaluation, not a completed production optimization.
The result is scoped to this frozen input packet and does not claim capabilities outside the agent contract.
