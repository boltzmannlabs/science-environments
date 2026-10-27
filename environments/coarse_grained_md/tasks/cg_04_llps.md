# Task: cg_04_llps

**Task family:** liquid-liquid phase separation. **Status:** specification;
execution and qualification are case-specific.

## Description and target

Measure dense/dilute phases and concentration-dependent assembly while checking
finite-size effects, equilibration, and parameter artifacts. The specialist is
CG Phase Separation (`CG-13`).

## Required execution and output

Freeze composition, box, model, replicas, and state; analyse density and
clusters independently; return a `cg_task_bundle` with evidence and uncertainty.

## Acceptance and limitations

PASS requires phase-boundary references and converged replicas. The current
polymer/LLPS proxy only exercises the execution path.
