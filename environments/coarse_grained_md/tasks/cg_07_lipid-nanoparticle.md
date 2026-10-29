# Task: cg_07_lipid-nanoparticle

**Task family:** lipid nanoparticle and drug-delivery CG. **Status:**
specification; execution and qualification are case-specific.

## Description and target

Evaluate morphology, cargo interactions, encapsulation, membrane interactions,
and nonphysical aggregation under a declared model. Preserve composition,
protonation, force field, and state.

## Required execution and output

Run bounded replicas, independently assess morphology and interactions, and
return a `cg_task_bundle` with units, hashes, uncertainty, and stop reason.

## Acceptance and limitations

PASS requires validated lipid/cargo parameters and references. No delivery or
biological claim follows from morphology alone.
