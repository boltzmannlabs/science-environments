# FEP-ENV-13 — Simulation Execution and Recovery

**Purpose:** Diagnose crashes, NaNs, constraint failures, and failed lambda replicas with bounded recovery.

**Inputs:** immutable run manifest, logs, checkpoints, window/replica status, and retry policy.

**Procedure:** preserve evidence, identify the first failure, propose one justified correction, retry within limits, and independently validate the restart.

**Acceptance:** PASS requires a traceable recovery without silent scientific-setting changes; unresolved failures stop safely.
