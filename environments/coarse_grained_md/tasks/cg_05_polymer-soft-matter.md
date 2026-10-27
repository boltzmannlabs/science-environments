# Task: cg_05_polymer-soft-matter

**Task family:** polymer and soft-matter CG MD. **Status:** specification;
execution and qualification are case-specific.

## Description and target

Evaluate chain statistics, relaxation, aggregation, self-assembly, and chain
crossing artifacts. The specialists are CG Self-Assembly (`CG-14`) and CG
Kinetics/Dynamics (`CG-17`).

## Required execution and output

Freeze bead model, box, state, replicas, and analysis settings; independently
validate observables and uncertainty; return a `cg_task_bundle`.

## Acceptance and limitations

PASS requires a declared polymer model and reference statistics. A short toy
chain is not a production polymer result.
