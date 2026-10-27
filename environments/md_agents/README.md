# Molecular Dynamics Specialist Agents

**Status: Specification.** This package defines a reusable MD specialist-agent
core and online-resource discovery contracts. It does not claim that 50 MD
environments, production trajectories, or the Langevin Flow Maps method have
been implemented or scientifically qualified.

## Scope

The package contains 20 reusable MD execution/analysis specialists, 10 online
literature/model/dataset provenance specialists, and 20 domain-specific
specialists for folding, interfaces, nucleic acids, free energy, QM/MM,
learned potentials, reproducibility and qualification. The same contracts can
support protein-ligand, membrane, free-energy, coarse-grained, materials,
QM/MM and learned-potential environments.

## Read in this order

1. [Environment specification](ENVIRONMENT_SPEC.md)
2. [Configuration](config/environment.yaml), [request schema](config/request.schema.json), and [protocol schema](config/protocol.schema.json)
3. [Task registry](tasks/)
4. [Agent contracts](agents/contracts.json)
5. [Acceptance plan](tests/ACCEPTANCE.md) and [validation evidence](tests/specification-validation.json)

## Current maturity

The contracts and package validator are implemented. GROMACS/OpenMM/AMBER/
LAMMPS adapters, production trajectory references, online downloads, and MD
benchmark results remain follow-up implementation work. Online resources must
be versioned, licensed, hashed and compatibility-checked before execution.
