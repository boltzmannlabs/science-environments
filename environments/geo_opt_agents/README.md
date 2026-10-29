# Specialist Geometry-Optimisation Agents

**Lifecycle: In Progress — executable and partially scientifically validated.** This environment contains
18 geometry-optimisation specialist contracts, frozen task inputs, engine
fixtures, qualification reports and benchmark evidence.

## Read in this order

Qualification uses the shared conservative evidence gate in
[`../shared_qualification`](../shared_qualification/).

1. [Environment specification](ENVIRONMENT_SPEC.md)
2. [Status](STATUS.md), [models and tools](MODELS_AND_TOOLS.md), and [implementation report](IMPLEMENTATION_REPORT.md)
3. [Environment configuration](config/environment.yaml), [request schema](config/request.schema.json), and [protocol schema](config/protocol.schema.json)
4. [Task registry](tasks/README.md) and [task cards/results](examples/geo_opt_tasks/)
5. [Benchmark](benchmark/README.md), [provenance](SOURCE_PROVENANCE.json), and [qualification evidence](reports/agent_qualification/)
6. [Acceptance plan](tests/ACCEPTANCE.md) and [validation evidence](tests/specification-validation.json)

The evaluator distinguishes convergence from minimum verification and records
scientific, infrastructure, provenance and reporting failures separately.

## Package structure

```text
geo_opt_agents/
├── README.md
├── ENVIRONMENT_SPEC.md
├── config/
│   ├── environment.yaml
│   ├── request.schema.json
│   └── protocol.schema.json
├── examples/geo_opt_tasks/
├── examples/geo_opt_results/
├── reports/
├── scripts/
└── tests/
    ├── ACCEPTANCE.md
    └── specification-validation.json
```

Problem-solving contracts are in [problem_solving/](problem_solving/), with
shared recovery logic under `../md_agents/recovery_agents/cross_domain/`.
