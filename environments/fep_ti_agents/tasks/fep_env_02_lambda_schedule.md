# FEP-ENV-02 — Lambda Schedule and Window Management

**Purpose:** Construct and audit lambda windows for a specified alchemical transformation.

**Inputs:** endpoint topology, initial schedule, soft-core/coupling settings, pilot diagnostics, and compute budget.

**Procedure:** inspect energy/derivative variance and adjacent-window overlap; identify missing or unstable windows; propose changes without silently changing chemistry.

**Acceptance:** Every proposed window has a reproducible lambda value and provenance. PASS requires bounded variance and overlap at the frozen threshold; unresolved gaps are REVIEW.
