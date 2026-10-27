# FEP-ENV-03 — Alchemical Atom Mapping and Transformation Validation

**Purpose:** Validate atom correspondence, stereochemistry, protonation, bond changes, dummy atoms, and endpoint compatibility before simulation.

**Inputs:** endpoint structures, atom map, formal charges, force-field parameters, and transformation specification.

**Procedure:** check conserved substructure, valence, charge balance, mapping uniqueness, and supported parameterization.

**Acceptance:** PASS only if an independent topology check finds no unresolved mapping or parameter errors. Ambiguous or unsupported transformations must stop with REVIEW/FAIL.
