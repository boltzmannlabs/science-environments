# FEP-ENV-04 — Sampling and Free-Energy Convergence

**Purpose:** Determine whether trajectories provide adequate sampling for a stable free-energy estimate.

**Inputs:** window trajectories, independent replicas, block estimates, autocorrelation/ESS diagnostics, and convergence thresholds.

**Procedure:** compare time blocks and replicas, assess state coverage, hysteresis, and uncertainty; request targeted additional sampling where justified.

**Acceptance:** PASS requires stable block estimates, sufficient ESS, replica agreement, and calibrated uncertainty. Longer runtime without evidence remains REVIEW.
