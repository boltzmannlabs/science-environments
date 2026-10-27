# Task: qmmm_ps01_region-selection

**Task family:** QM-region selection. **Status:** fixture-qualified; production
execution is case-specific.

## Description and target

Check catalytic residues, ligand, cofactors, and boundary context. Specialist:
QMMM-PS01. Preserve coordinates, topology, charge, and region provenance.

## Acceptance

PASS requires chemically justified region evidence and a versioned topology;
missing evidence is REVIEW. Return a `qmmm_task_bundle` with hashes and stop
reason.
