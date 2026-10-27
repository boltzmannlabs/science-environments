# Task: cg_06_nanoparticle-colloid

**Task family:** nanoparticle and colloidal assembly. **Status:** specification;
execution and qualification are case-specific.

## Description and target

Assess interaction ranges, surface functionalization, cluster formation, and
finite-size artifacts. Preserve particle model, solvent representation,
trajectory, replicas, and analysis.

## Required execution and output

Run the supported adapter, independently validate clusters and finite-size
controls, and return a `cg_task_bundle` with evidence and limitations.

## Acceptance and limitations

PASS requires a validated particle model and reference observables. Artificial
aggregation or a stable trajectory alone is not a pass.
