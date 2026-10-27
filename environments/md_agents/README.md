# Molecular Dynamics Specialist Agents

**Status: Specification.** This package defines a reusable MD specialist-agent
core and online-resource discovery contracts. It does not claim that 50 MD
environments, production trajectories, or the Langevin Flow Maps method have
been implemented or scientifically qualified.

## Scope

The package contains 20 reusable MD execution/analysis specialists, 10 online
literature/model/dataset provenance specialists, 20 domain-specific
specialists, and 12 scenario specialists covering preparation, parameter,
runtime, analysis, sampling, online-resource, infrastructure, validation and
orchestration failures. The same contracts can support protein-ligand,
membrane, free-energy, coarse-grained, materials, QM/MM and learned-potential
environments.

## Read in this order

1. [Environment specification](ENVIRONMENT_SPEC.md)
2. [Configuration](config/environment.yaml), [request schema](config/request.schema.json), and [protocol schema](config/protocol.schema.json)
3. [Task registry](tasks/)
4. [Agent contracts](agents/contracts.json)
5. [Acceptance plan](tests/ACCEPTANCE.md) and [validation evidence](tests/specification-validation.json)

## Current maturity

The contracts and package validator are implemented. The 12 scenario
specialists are task contracts; they are not yet independently qualified. A
first actual OpenMM
CUDA core case (water-box minimization plus short NVT production) is recorded
under `results/core_openmm/`. GROMACS/AMBER/LAMMPS adapters, production
trajectory references, long-timescale sampling, online downloads, and domain
qualification remain follow-up work. Online resources must be versioned,
licensed, hashed and compatibility-checked before execution.

The reusable troubleshooting package in
[recovery_agents/](recovery_agents/) contains 10 executable recovery agents
with frozen failure fixtures and a separate harness. Its results are recovery
fixture evidence, not a replacement for production engine qualification.

## GPU backend availability

The host has an NVIDIA GeForce RTX 3060. The system `/usr/bin/gmx` is a
CPU-only build, but the Conda environment `gromacs-gpu` provides GROMACS
2024.2 built with CUDA support. Use the GPU build explicitly:

```bash
conda run -n gromacs-gpu gmx --version
conda run -n gromacs-gpu gmx mdrun -nb gpu -pme gpu -bonded gpu -gpu_id 0
```

This verifies backend capability only. A GROMACS production case, repeat
records, and scientific evaluator are still required before GROMACS results
are counted as a qualified benchmark profile.
