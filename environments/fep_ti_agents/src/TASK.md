# Task: fep_ti_environment_001

**Task family:** paper-based free-energy environment reconstruction  
**Module:** FEP/TI  
**Status:** In progress; setup evidence is available, scientific FEP qualification remains `REVIEW`.

## Description

Translate a published FEP methodology into a traceable, executable setup for
one selected molecular system. The agent must preserve the paper reference,
separate evaluator-only values from agent inputs, generate required molecular
artifacts, compare configurations and stop when production evidence is absent.

## Required execution

1. Read the selected paper and pinned source manifest.
2. Validate molecular identities, transformation direction and input hashes.
3. Extract reported parameters and label exact, inferred, deviating and missing values.
4. Generate endpoint parameters/topologies using approved tools.
5. Run reference, agent, alternative and perturbed setup configurations.
6. Independently validate artifacts, provenance and failure handling.
7. Report setup fidelity separately from production FEP metrics.

## Required output

Return the task bundle under `tasks/<task>/`, the benchmark description under
`benchmark/`, and execution/evaluation evidence under the task's `execution/`
and `evaluation/` directories. Missing trajectories, overlap, convergence or
uncertainty must remain `REVIEW`, never be replaced by a fabricated result.
