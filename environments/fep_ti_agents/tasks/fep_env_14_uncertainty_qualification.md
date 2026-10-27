# FEP-ENV-14 — Uncertainty and Benchmark Qualification

**Purpose:** Compare predictions to frozen references while checking uncertainty calibration and reproducibility.

**Inputs:** repeated runs, reference free energies, confidence intervals, methods, seeds, hashes, and scoring thresholds.

**Procedure:** independently score error, uncertainty coverage, replicate agreement, and provenance completeness.

**Acceptance:** Return PASS, REVIEW, or FAIL with the evidence table; never convert a missing reference into a pass.
