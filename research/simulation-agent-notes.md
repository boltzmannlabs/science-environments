# Simulation-agent research notes

## Scope

Boltsim treats an agent as qualified only when its executable adapter, frozen
inputs, independent evaluator, failure cases, provenance, and reproducibility
evidence are present. A successful process exit is not a scientific PASS.

## Evidence states

- **Specification:** contract and exact inputs are documented.
- **Implemented:** executable logic and an engine adapter exist.
- **Tested:** baseline, recoverable-failure, adversarial, and stop cases run.
- **Qualified:** independent scientific checks and reference comparisons pass.

The environment reports `REVIEW` when trajectories, reference observables,
sampling statistics, or provenance are incomplete. Synthetic fixtures are
diagnostic tests and must not be presented as published scientific results.

## Cross-module workflow

SPE/Geo-Opt/HOMO–LUMO establish electronic-structure inputs; QM/MM validates
coupled regions; FEP/TI and MD execute and analyse molecular simulations; CG-MD
extends sampling to reduced-resolution systems. Inputs remain immutable and
repairs are written as new, provenance-linked artifacts.
