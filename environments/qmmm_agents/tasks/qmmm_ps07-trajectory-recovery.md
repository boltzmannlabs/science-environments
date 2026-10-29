# Task: qmmm_ps07-trajectory-recovery

**Task family:** QM/MM trajectory recovery. **Status:** fixture-qualified.

## Description and target

Inspect the first failed step, checkpoint, timestep, QM convergence, and safe
restart. Specialist: QMMM-PS07.

## Acceptance

PASS requires a compatible checkpoint and post-restart QM/MM checks; otherwise
return REVIEW without overwriting original evidence.
