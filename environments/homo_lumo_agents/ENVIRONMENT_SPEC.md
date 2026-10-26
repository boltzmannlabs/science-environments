# Environment specification

## Objective

Compute `gap = epsilon_LUMO - epsilon_HOMO` from converged molecular-orbital
eigenvalues, with explicit provenance and independent validation.

## Frozen prototype contract

- Backend: PySCF 2.x, RHF
- Basis: STO-3G
- Units: Hartree and eV (`1 Eh = 27.211386245988 eV`)
- Convergence: `mf.converged` must be true; finite orbital energies required
- Closed-shell inputs only in this prototype (`multiplicity=1`)
- Cases: water, methane, benzene

## Required output

Each result records task id, geometry hash, method, basis, charge,
multiplicity, SCF status, HOMO/LUMO indices and energies, gap in both units,
wall time, engine version, and failure category when unsuccessful.

## Failure taxonomy

`invalid_input`, `unsupported_state`, `scf_nonconvergence`,
`orbital_index_error`, `nonfinite_result`, `provenance_error`, `runtime_error`.

## Scientific caveat

The reported quantity is a Kohn–Sham/HF orbital-eigenvalue gap. It is not an
optical excitation energy and is not automatically the fundamental gap.
