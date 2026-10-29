# Specialist Single-Point Energy (SPE) Agents

**Lifecycle: In Progress — executable and partially scientifically validated.** This environment defines
specialist single-point-energy tasks, their input/output contracts, and versioned
benchmark evidence. It does not imply that every backend is available on every
machine.

## Read in this order

Qualification uses the shared conservative evidence gate in
[`../shared_qualification`](../shared_qualification/).

1. [Environment specification](ENVIRONMENT_SPEC.md)
2. [Status](STATUS.md), [models and tools](MODELS_AND_TOOLS.md), and [implementation report](IMPLEMENTATION_REPORT.md)
3. [Environment configuration](config/environment.yaml), [request schema](config/request.schema.json), and [protocol schema](config/protocol.schema.json)
4. [Task registry](tasks/README.md) and [example request](tasks/request.example.json)
5. [Benchmark](benchmark/README.md) and [provenance](SOURCE_PROVENANCE.json)
6. [Acceptance plan](tests/ACCEPTANCE.md) and [validation evidence](tests/specification-validation.json)

The environment separates scientific failures (invalid state, unsupported
method, non-convergence) from infrastructure and provenance failures. Results
must retain method, basis, charge, multiplicity, engine/version, runtime and
input hashes.

## Package structure

```text
spe_agents/
├── README.md
├── ENVIRONMENT_SPEC.md
├── config/
│   ├── environment.yaml
│   ├── request.schema.json
│   └── protocol.schema.json
├── tasks/
│   ├── spe_001_single_point_energy.md
│   └── request.example.json
└── tests/
    ├── ACCEPTANCE.md
    ├── specification-validation.json
    └── validate_spec.py
```

The detailed benchmark reports are maintained in the benchmarking repository;
this package documents the executable environment contract and maturity.

Problem-solving contracts are in [problem_solving/](problem_solving/), with
shared recovery logic under `../md_agents/recovery_agents/cross_domain/`.
