# FEP-ENV-10 — Protein Mutation Free Energy

**Purpose:** Evaluate a supported residue mutation using a consistent alchemical protocol.

**Inputs:** mapped residue endpoints, protonation states, complex/solvent legs, parameters, and replica protocol.

**Procedure:** audit residue mapping and topology, run the two legs, and assess overlap, convergence, and cycle consistency.

**Acceptance:** PASS requires chemically valid endpoints and reproducible leg estimates; unresolved protonation or topology changes are REVIEW.
