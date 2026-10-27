# Coarse-Grained Molecular Dynamics Environment

**Status: Specification with a toy executable profile.** This environment
defines reusable contracts for multiple coarse-grained (CG) resolutions and
engines. It does not claim that all CG force fields, membranes, phase
separation systems, or parameterization workflows are qualified.

## Environment families

The task registry covers mapping/preparation, biomolecular CG MD, membranes,
liquid-liquid phase separation, polymers/soft matter, colloids, lipid
nanoparticles, atomistic-to-CG validation, force-field development, and
trajectory qualification.

## Specialist agents

The package defines 20 executable contract roles in
[agents/contracts.json](agents/contracts.json): mapping and topology
(`CG-01`–`CG-02`), force-field and parameterization (`CG-03`–`CG-05`), system
setup and execution (`CG-06`–`CG-10`), family-specific analysis
(`CG-11`–`CG-14`), validation (`CG-15`–`CG-17`, `CG-19`), reconstruction
(`CG-18`), and benchmarking/orchestration (`CG-20`). The runtime implementation
is in [cg_agents/](cg_agents/) and is exercised by the harness below.

## Read in this order

1. [Environment specification](ENVIRONMENT_SPEC.md)
2. [Configuration](config/environment.yaml) and [example request](tasks/request.example.json)
3. [Agent contracts](agents/contracts.json)
4. [Task cards](tasks/)
5. [Executable runtime](cg_agents/) and [harness](scripts/run_agent_harness.py)
6. [Harness evidence](results/agent_harness/results.json)
7. [Tests](tests/)

The related MD contracts are in
[`../md_agents`](../md_agents/), while benchmark comparison reports are
maintained in the separate
[`science-benchmarking/benchmarking/md_agents`](https://github.com/boltzmannlabs/science-benchmarking/tree/main/benchmarking/md_agents)
package. CG results must not be mixed with atomistic MD results without an
explicit mapping and compatible observable definition.

## Package structure

```text
coarse_grained_md/
├── README.md / ENVIRONMENT_SPEC.md
├── agents/                 # 20 CG contracts
├── cg_agents/              # executable deterministic checks
├── config/                 # environment settings
├── tasks/                  # 10 uniform CG task cards
├── scripts/                # toy runner and agent harness
├── results/                # versioned smoke evidence
└── tests/                  # registry/runtime validation
```

## Executable profile

`scripts/run_toy_cg.py` runs a deliberately small bead-spring chain with
OpenMM using custom harmonic bonds and a repulsive nonbonded interaction. It
tests that the adapter can build, minimize, run, and validate a CG system. It
is not a protein, membrane, LLPS, or production force-field qualification.

The executable `scripts/run_agent_harness.py` invokes all 20 deterministic
specialist checks against three OpenMM CUDA smoke systems: a bead-chain
protein proxy, a membrane-patch proxy, and a polymer/LLPS proxy. Results are
stored under `results/agent_harness/`. Family-specific checks pass only when
the corresponding proxy is present; reference-dependent checks remain REVIEW.

## Evidence rules

Every real CG result must record resolution, mapping, force-field/model and
version, topology and parameter hashes, engine/platform, seed, replicas,
observables, reference conditions, and limitations. CG and atomistic results
must not be compared across incompatible thermodynamic states or observables.
