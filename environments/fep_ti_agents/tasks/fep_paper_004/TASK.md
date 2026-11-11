# Task: fep_paper_004

**Task family:** Paper-based FEP environment reconstruction  
**Status:** reference-ready / review

## Research source

Ross et al. public protein–ligand binding-free-energy benchmark, PTP1B PDB
`2QBS`, second edge **23477 → 23479** at source revision
`a65d86b782a678c75388566ce00446e45283ee63`.

## Objective

Validate a second, distinct PTP1B RBFE transformation using frozen published
structures, the edge CSV and a four-configuration matrix. This tests that the
FEP environment does not depend on the original 23477 → 23482 edge.

## Acceptance

- Validate protein and ligand SHA-256 values and the edge `23477 → 23479`.
- Confirm the evaluator-only experimental ΔΔG of `-0.29 kcal/mol`.
- Reject a reversed-edge configuration before execution.
- Return `REVIEW` until endpoint parameterization, hybrid topology, lambda
  trajectories, overlap, convergence and uncertainty evidence exists.
