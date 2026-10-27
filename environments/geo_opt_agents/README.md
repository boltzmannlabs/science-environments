# Specialist Geometry-Optimisation Agents

**Status: Implemented/validated evidence package.** This environment contains
18 geometry-optimisation specialist contracts, frozen task inputs, engine
fixtures, qualification reports and benchmark evidence.

## Read in this order

1. [Environment specification](ENVIRONMENT_SPEC.md)
2. [Environment configuration](config/environment.yaml), [request schema](config/request.schema.json), and [protocol schema](config/protocol.schema.json)
3. [Task cards and results](examples/geo_opt_tasks/)
4. [Qualification evidence](reports/agent_qualification/)
5. [Acceptance plan](tests/ACCEPTANCE.md) and [validation evidence](tests/specification-validation.json)

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
