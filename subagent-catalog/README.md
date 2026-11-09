# Boltsim simulation-agent catalog

This branch is intentionally scoped to simulation agents. It does not contain
the SPE, geometry-optimization, HOMO–LUMO, QM/MM, or shared pod packages. Those
modules remain in their owning repositories. The packages correspond to the
simulation environments maintained under
`MLIPs/science-environments-agents/environments/` and follow the contribution
starter layout: `manifest.yaml`, `instructions.md`, `README.md`, `skills/`, and
`tests/`.

Packages are portable definitions. They reference engines by name and version
constraints; they do not include credentials, installed environments, private
datasets, generated trajectories, or machine-specific paths.

## Packages

- `fep-ti` — free-energy perturbation and thermodynamic-integration agents
- `md` — molecular-dynamics execution and analysis agents
- `coarse-grained-md` — coarse-grained mapping, simulation, and validation agents

Each package records its local fixture checks in `tests/validation.json`.
Executable source environments, concrete inputs, adapters, trajectories, and
benchmark evidence remain in the MLIPs environment tree; this catalog does not
copy installed environments, credentials, private datasets, generated
trajectories, or machine-specific paths.
