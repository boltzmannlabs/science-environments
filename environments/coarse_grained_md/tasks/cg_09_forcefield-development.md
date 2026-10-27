# Task: cg_09_forcefield-development

**Task family:** CG force-field development and parameterization. **Status:**
specification; execution and qualification are case-specific.

## Description and target

Evaluate force matching, relative entropy, or iterative Boltzmann inversion
with held-out data, transferability, stability, and uncertainty. Specialists
are Parameterization (`CG-04`), Force-Field Selection (`CG-03`), and
Transferability (`CG-05`).

## Required execution and output

Freeze training/held-out splits, units, optimizer, model version, and seeds;
independently score errors and stability; return a `cg_task_bundle`.

## Acceptance and limitations

PASS requires held-out evidence and transfer tests. Training-set agreement
alone is not qualification.
