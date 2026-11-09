# Boltsim scientific subagent catalog

This catalog packages the implemented scientific agents for contribution to the
Science-Environments repository. Each package follows the contribution starter
layout: `manifest.yaml`, `instructions.md`, `README.md`, `skills/`, and `tests/`.

Packages are portable definitions. They reference engines by name and version
constraints; they do not include credentials, installed environments, private
datasets, generated trajectories, or machine-specific paths.

## Packages

- `spe` — single-point-energy agents
- `geo-opt` — geometry-optimization agents
- `homo-lumo` — frontier-orbital analysis agents
- `qm-mm` — coupled QM/MM agents
- `fep-ti` — free-energy perturbation and thermodynamic-integration agents
- `md` — molecular-dynamics execution and analysis agents
- `coarse-grained-md` — coarse-grained mapping, simulation, and validation agents
- `shared-qualification` — cross-module audit and provenance agents

Each package records its local fixture checks in `tests/validation.json`.
Integrated SCI CLI installation and profile authorization remain pending
maintainer-side testing.
