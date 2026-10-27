# GEO-OPT-001 — Geometry optimisation

## Objective

Validate, optimise and independently assess a molecular geometry under a
declared electronic-structure protocol.

## Inputs

Use `request.example.json` with the structure, charge, multiplicity, method,
basis, iteration limit and constraints. Preserve constraints and atom order.

## Expected output

Return final coordinates, energy, gradient/displacement metrics, convergence
classification, constraint checks, engine/version, runtime and provenance.

## Acceptance

Finite coordinates and energy; independently verified convergence; preserved
constraints; gradient evidence; and Hessian/frequency evidence when claiming a
local minimum. A successful process exit alone is insufficient.
