# MD-54 — Production MD Execution Failure Scenarios

Handle crashes, NaNs, excessive timestep, inconsistent restarts, disk exhaustion, scheduler interruption, and machine restart. Preserve the first failing log/checkpoint; recovery passes only after post-restart scientific checks.
