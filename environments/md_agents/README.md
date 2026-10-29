# Molecular Dynamics Specialist Agents

**Lifecycle: In Progress — executable / partially scientifically validated.** This package contains executable
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

## Read in this order

1. [Environment specification](ENVIRONMENT_SPEC.md)
2. [Status and maturity](STATUS.md)
3. [Models and tools](MODELS_AND_TOOLS.md)
4. [Implementation report](IMPLEMENTATION_REPORT.md)
5. [Configuration](config/environment.yaml), [request schema](config/request.schema.json), and [protocol schema](config/protocol.schema.json)
6. [Task registry](tasks/README.md)
7. [Benchmark protocol](benchmark/README.md)
8. [Agent contracts](agents/contracts.json)
9. [Acceptance plan](tests/ACCEPTANCE.md) and [validation evidence](tests/specification-validation.json)
10. [Real-system execution results](results/real_system_production/RESULTS.md)
11. [Runtime contracts](runtime/CONTRACTS.md) and [results index](results/README.md)

## Package layout

The package follows the repository environment layout: specification and
configuration at the root, one concrete task packet per agent under `inputs/`,
real public molecular systems under `inputs/real_systems/`, diagnostic fixtures
under `inputs/fixtures/`, task descriptions under `tasks/`, benchmark definitions
under `benchmark/`, documentation and evaluation protocol under `docs/`, runtime facades
under `runtime/`, and versioned evidence under `results/`. The executable
adapters and fixture-generation utilities are under `scripts/`; independent
checks are under `tests/`.

## Explicit per-agent input packets

[`cases/agent_inputs.json`](cases/agent_inputs.json) contains one concrete
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

## Run the environment

From this directory, with OpenMM, MDTraj, PyArrow and the test dependencies
installed:

```bash
python scripts/materialize_agent_fixtures.py
python scripts/run_agent_harness.py --live
python scripts/render_qualification_report.py
python -m pytest -q tests
```

The harness executes all 62 packets. `MD-10` runs the live OpenMM CUDA water
box; the other packets use their declared native adapter and independent
evaluator. Adapter `PASS` means the input was consumed successfully. It does
not by itself establish a scientific result. Use `--strict` to return a
nonzero exit code while any packet remains scientifically unresolved.

Real-system preparation and bounded CUDA execution are reproducible with:

```bash
python scripts/run_real_system_smoke.py
python scripts/run_real_system_production.py
bash scripts/build_benzamidine_complex.sh
python scripts/run_parameterized_complex.py
```

The original public structures remain in `inputs/real_systems/`; derived repairs,
topologies, trajectories and logs are written to `results/`.

## Current maturity

The contracts, packet harness, native fixture adapters, and package validator
are implemented. A real-system batch (villin, DNA, barnase–barstar, and
trypsin–benzamidine) is recorded under `results/real_system_production/`.
The trypsin ligand uses AmberTools GAFF2/AM1-BCC with explicit TIP3P solvation
and counterions. These are bounded execution records; long-timescale sampling,
FEP uncertainty, and independent domain qualification remain follow-up work.

The reusable troubleshooting package in
[recovery_agents/](recovery_agents/) contains 10 executable recovery agents
with frozen failure fixtures and a separate harness. Its results are recovery
fixture evidence, not a replacement for production engine qualification.

## Evidence status

The current report records 62 packet executions, 61 successful native adapter
loads, and one live OpenMM CUDA execution. Qualification is intentionally more
conservative: only independently supported checks are marked `PASS`; unresolved
trajectory, sampling, reference, recovery or provenance requirements remain
`REVIEW`. See [agent qualification report](results/agent_qualification_report.md)
and [real-system results](results/real_system_production/RESULTS.md).

## Limitations

This package does not claim long-timescale MD, converged free energies,
production FEP, enhanced-sampling qualification, QM/MM validation, learned
potential validation, or online-resource reproduction. Synthetic fixtures are
diagnostic inputs and are never treated as published reference systems.
Scientific claims require versioned systems, parameters, seeds, trajectories,
reference observables and independent evaluators.

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
