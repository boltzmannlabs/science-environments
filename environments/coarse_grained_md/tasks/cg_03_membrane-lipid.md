# Task: cg_03_membrane-lipid

**Task family:** CG membrane and lipid systems. **Status:** specification;
execution and qualification are case-specific.

## Description and target

Validate lipid composition, embedding, thickness, area per lipid, mixing,
defects, and protein compatibility. The specialist is CG Membrane Validation
(`CG-12`). Preserve model, composition, topology, trajectory, and state.

## Required execution and output

Run the declared adapter, independently compute membrane observables, and
return a `cg_task_bundle` with metrics, units, hashes, runtime, limitations,
and status.

## Acceptance and limitations

PASS requires a supported lipid model and reference tolerances. The current
membrane patch is a smoke proxy, not production membrane qualification.
