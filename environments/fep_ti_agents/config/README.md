# FEP configuration

This directory contains the environment and protocol schemas used by the
FEP/TI task harness. Paper-specific configurations are kept inside each task
under `tasks/<task>/configs/` so the reference, agent, alternative and
perturbed conditions remain isolated and auditable.

Do not copy evaluator-only reference values into agent-generated configurations.
Missing paper parameters must be recorded as unresolved or explicitly inferred.
