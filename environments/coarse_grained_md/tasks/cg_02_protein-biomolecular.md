# Task: cg_02_protein-biomolecular

**Task family:** protein and biomolecular CG MD. **Status:** specification;
execution and qualification are case-specific.

## Description and target

Assess mapped protein or complex simulations for drift, unfolding,
secondary-structure retention, oligomer stability, and sampling sufficiency.
The specialist is CG Protein Structure Validation (`CG-11`). Preserve mapping,
model, topology, trajectories, replicas, and analysis settings.

## Required execution and output

Freeze inputs and thermodynamic state, run the declared adapter, independently
validate structural observables, and return a `cg_task_bundle` with status,
metrics, units, hashes, runtime, limitations, and stop reason.

## Acceptance and limitations

PASS requires a supported protein model and reference observables. A bead
chain proxy is smoke evidence only; it is not protein qualification.
