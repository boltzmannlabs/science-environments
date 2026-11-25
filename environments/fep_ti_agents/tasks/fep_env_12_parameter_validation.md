# FEP-ENV-12 — Force-Field and Parameter Validation

**Purpose:** Validate ligand/protein parameters, charges, bonded terms, and engine compatibility before expensive sampling.

**Inputs:** topology/parameter files, atom types, charges, endpoint structures, and engine version.

**Procedure:** perform independent topology checks and reject invented or unapproved parameters.

**Acceptance:** PASS requires zero unresolved parameters and valid bonded/nonbonded consistency. Missing evidence is FAIL/REVIEW.
