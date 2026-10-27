# FEP-ENV-15 — Adaptive Sampling and Compute Allocation

**Purpose:** Prioritize additional windows, replicas, or trajectory length using measured uncertainty and overlap gaps.

**Inputs:** window metrics, replica diagnostics, compute budget, and immutable baseline manifest.

**Procedure:** rank evidence-supported sampling needs, propose bounded allocation, and re-evaluate only changed evidence.

**Acceptance:** PASS requires an auditable allocation rationale and improved diagnostics; budget exhaustion is REVIEW with explicit unavailable conclusions.
