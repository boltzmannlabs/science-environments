# FEP-ENV-06 — Thermodynamic Cycle and Leg Consistency

**Purpose:** Verify complex/solvent legs, signs, units, reference states, and cycle closure.

**Inputs:** leg results, lambda direction, units, endpoint identities, restraints/corrections, and cycle references.

**Procedure:** independently recompute the combined ΔΔG and test leg completeness and closure.

**Acceptance:** PASS requires a closed, unit-consistent cycle within the frozen tolerance; missing legs or sign ambiguity are FAIL/REVIEW.
