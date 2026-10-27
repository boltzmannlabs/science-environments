# SPE-001 — Single-point energy

## Objective

Run one declared single-point-energy calculation and return a reproducible,
independently checkable result.

## Inputs

Use the structure, charge, multiplicity, method, basis, numerical settings and
reference protocol in `request.example.json`. The engine must be selected from
the supported adapter registry; do not silently substitute a method or basis.

## Expected output

Report energy and units, convergence, warnings, engine/version, input hashes,
wall time, resource use and a typed failure status when execution is not valid.

## Acceptance

Finite energy, compatible state/method, required convergence evidence and
complete provenance. Unsupported, incomplete or non-converged work is not a
scientific pass.
