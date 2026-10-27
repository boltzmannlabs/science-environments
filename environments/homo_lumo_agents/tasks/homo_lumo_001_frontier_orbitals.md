# HOMO-LUMO-001 — Frontier orbital gap

## Objective

Calculate and validate the orbital-eigenvalue HOMO–LUMO gap for a declared
molecular state. This is not an optical excitation energy or a fundamental gap.

## Inputs

Use the closed-shell RHF/STO-3G prototype request in `request.example.json`.
The calculation must preserve atom ordering, charge, multiplicity and units.

## Expected output

Report HOMO/LUMO indices and energies, gap in Hartree and eV, SCF status,
engine/version, wall time and input hash.

## Acceptance

SCF convergence, finite orbitals, consistent occupied/virtual indexing,
independent gap arithmetic and complete provenance.
