# Task: cg_08_multiscale-validation

**Task family:** atomistic-to-CG multiscale validation. **Status:**
specification; execution and qualification are case-specific.

## Description and target

Compare only compatible states and observables between CG and atomistic
trajectories. The specialists are Structural Observable Matching (`CG-15`) and
CG-to-Atomistic Reconstruction (`CG-18`).

## Required execution and output

Freeze mapping, state, model, trajectory, and observable definitions; perform
independent reconstruction/comparison; return a `cg_task_bundle` with metrics,
uncertainty, hashes, and limitations.

## Acceptance and limitations

PASS requires compatible thermodynamic conditions and atomistic references.
Cross-resolution comparison without mapping evidence is REVIEW.
