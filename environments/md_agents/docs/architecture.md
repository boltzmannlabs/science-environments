# Architecture

The MD environment is organized as contracts → exact task packets → native
engine adapters → independent evaluators → evidence records. Original inputs
remain immutable; derived repairs, checkpoints, logs, trajectories, and
reports are written under `results/`.

The packet harness supports normal cases, recoverable failures, adversarial
cases, online-resource cases, domain specialists, and orchestration scenarios.
The same execution layer can be reused by OpenMM, GROMACS, and future engine
adapters, while acceptance criteria remain task-specific.
