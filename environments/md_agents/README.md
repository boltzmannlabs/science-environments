# Molecular Dynamics Specialist Agents

An Agent-Scientist environment for literature-grounded molecular-dynamics
setup reconstruction, bounded execution, trajectory analysis, and qualification.

**Status: Implemented / partially validated.** This package contains executable
input harnesses, engine adapters, recovery agents, and bounded OpenMM/CUDA
real-system runs. It does not claim that all 50 MD environments or long-time
production/FEP workflows have been scientifically qualified.

## Scope

The package contains 20 reusable MD execution/analysis specialists, 10 online
literature/model/dataset provenance specialists, 20 domain-specific
specialists, and 12 scenario specialists covering preparation, parameter,
runtime, analysis, sampling, online-resource, infrastructure, validation and
orchestration failures. The same contracts can support protein-ligand,
membrane, free-energy, coarse-grained, materials, QM/MM and learned-potential
environments.

## Environment structure

```text
md_agents/
├── README.md
├── ENVIRONMENT_SPEC.md
├── STATUS.md
├── MODELS_AND_TOOLS.md
├── config/
├── tasks/
├── scripts/
├── src/
├── tests/
├── benchmark/
└── results/
```

| Location | Information |
| --- | --- |
| [ENVIRONMENT_SPEC.md](ENVIRONMENT_SPEC.md) | Scientific scope, evidence rules, and qualification criteria. |
| [STATUS.md](STATUS.md) | Implemented work, limitations, and validation state. |
| [MODELS_AND_TOOLS.md](MODELS_AND_TOOLS.md) | Engine, model, and execution policy. |
| [config/](config/) | Environment policy and request/protocol schemas. |
| [tasks/](tasks/README.md) | Specialist assignments and paper-reconstruction tasks. |
| [scripts/](scripts/) | Packet generation, execution, validation, and reporting entry points. |
| [src/](src/) | Agent contracts, recovery runtime, and shared source code. |
| [tests/](tests/), [benchmark/](benchmark/), [results/](results/) | Acceptance checks, frozen inputs, and evidence. |

## Read in this order

1. [Environment specification](ENVIRONMENT_SPEC.md)
2. [Configuration](config/environment.yaml), [request schema](config/request.schema.json), and [protocol schema](config/protocol.schema.json)
3. [Task registry](tasks/)
4. [Agent contracts](src/agents/contracts.json)
5. [Acceptance plan](tests/ACCEPTANCE.md) and [validation evidence](tests/specification-validation.json)
6. [Real-system execution results](results/real_system_production/RESULTS.md)
7. [Benchmark fixture catalogue](benchmark/README.md)
8. [Research-paper benchmark catalogue](benchmark/PAPER_CATALOGUE.md)

The paper benchmark currently contains three catalogued MD studies. Each
packet tests literature-to-environment reconstruction and independent evidence
handling; it does not treat a short local trajectory as a reproduction.

## Explicit per-agent input packets

[`src/cases/agent_inputs.json`](src/cases/agent_inputs.json) contains one concrete
packet for every registered agent (`MD-01` through `MD-62`). Each packet names
the fixture, gives exact system/protocol/resource values, states the expected
evidence, and defines the acceptance rule. Rebuild it after changing the
registry with:

```bash
python scripts/build_agent_input_manifest.py
```

The packets intentionally include valid, failure, online-resource, domain, and
orchestration cases. A fixture name is a frozen input contract; it is not a
claim that the corresponding production engine run has already succeeded.

## Current maturity

The contracts, packet harness, native fixture adapters, and package validator
are implemented. A real-system batch (villin, DNA, barnase–barstar, and
trypsin–benzamidine) is recorded under `results/real_system_production/`.
The trypsin ligand uses AmberTools GAFF2/AM1-BCC with explicit TIP3P solvation
and counterions. These are bounded execution records; long-timescale sampling,
FEP uncertainty, and independent domain qualification remain follow-up work.

The reusable troubleshooting package in
[src/recovery_agents/](src/recovery_agents/) contains 10 executable recovery agents
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

## Package structure

```text
md_agents/
├── README.md / ENVIRONMENT_SPEC.md
├── src/                    # shared source contracts and agent registry
├── benchmark/              # paper tasks, cases, packets, and frozen fixtures
├── config/                 # environment policy and request/protocol schemas
├── tasks/                  # agent task cards
├── scripts/                # input generation, adapters, and execution entry points
├── results/                # immutable run and qualification evidence
└── tests/                  # package acceptance tests
```

Benchmark fixtures are inputs, not simulation results. Keep derived outputs in
`results/`; add a new frozen input under `benchmark/fixtures/` rather than at
the package root. The original fixture filename remains part of each input
packet for provenance, while its full package-relative path makes the source
unambiguous.

The first-level package layout follows the FEP environment convention:
`benchmark/`, `config/`, `results/`, `scripts/`, `src/`, `tasks/`, and `tests/`.
