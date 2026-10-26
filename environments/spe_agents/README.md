# Specialist Single-Point Energy (SPE) Agents

**Status: Implemented/validated evidence package.** This environment defines
specialist single-point-energy tasks, their input/output contracts, and versioned
benchmark evidence. It does not imply that every backend is available on every
machine.

## Read in this order

1. [Environment specification](ENVIRONMENT_SPEC.md)
2. [Protocol configuration](config/environment.yaml)
3. [Task and result evidence](../../benchmarking/spe_agents/README.md)
4. [Acceptance plan](tests/ACCEPTANCE.md)

The environment separates scientific failures (invalid state, unsupported
method, non-convergence) from infrastructure and provenance failures. Results
must retain method, basis, charge, multiplicity, engine/version, runtime and
input hashes.

## Package structure

```text
spe_agents/
├── README.md
├── ENVIRONMENT_SPEC.md
├── config/environment.yaml
└── tests/
    ├── ACCEPTANCE.md
    └── specification-validation.json
```

The detailed benchmark reports are maintained in the benchmarking repository;
this package documents the executable environment contract and maturity.
