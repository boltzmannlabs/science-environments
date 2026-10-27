# Specialist Single-Point Energy (SPE) Agents

**Status: Implemented/validated evidence package.** This environment defines
specialist single-point-energy tasks, their input/output contracts, and versioned
benchmark evidence. It does not imply that every backend is available on every
machine.

## Read in this order

1. [Environment specification](ENVIRONMENT_SPEC.md)
2. [Environment configuration](config/environment.yaml), [request schema](config/request.schema.json), and [protocol schema](config/protocol.schema.json)
3. [Task-facing description](tasks/spe_001_single_point_energy.md) and [example request](tasks/request.example.json)
4. [Task and result evidence](../../benchmarking/spe_agents/README.md)
5. [Acceptance plan](tests/ACCEPTANCE.md) and [validation evidence](tests/specification-validation.json)

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
