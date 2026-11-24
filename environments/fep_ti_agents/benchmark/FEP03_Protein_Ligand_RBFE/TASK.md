# FEP03 — published protein–ligand RBFE reconstruction

**Task family:** FEP/TI paper benchmark  
**Reference:** Ross et al. 2023 public protein–ligand RBFE benchmark  
**Status:** CDK2 `17 → 1h1q` is implemented at `tasks/fep_paper_001/`; a
second additional edge remains catalogued.

## Objective

The current implementation uses the CDK2 `17 → 1h1q` transformation at
`tasks/fep_paper_001/`. It evaluates paper-to-environment reconstruction using
frozen inputs, mapping, configuration matrix, endpoint readiness checks and
tests. A future second edge must have identifiable endpoint structures,
mapping, protocol metadata and reference evidence before execution.

## Stop condition

No additional edge may report topology, lambda trajectory or free-energy
results until its source revision and concrete transformation are frozen.
