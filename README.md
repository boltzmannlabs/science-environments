# Science Environments

Scientific environment specifications, research, workflows, and implementations for the Agent Scientist ecosystem.

Research notes and sources are organized by environment in `research/`. Environment requirements, configuration, tasks, and applicable tests are organized in `environments/`.

## Repository structure

```text
science-environments/
├── README.md
├── CONTRIBUTING.md
├── LICENSE
├── research/
│   ├── README.md
│   ├── scRNAseq-environment/
│   │   ├── research-notes.md
│   │   └── references.md
│   ├── synthesis-route-gym/
│   │   ├── research-notes.md
│   │   └── references.md
│   ├── sirna-designing-harness/
│   │   ├── research-notes.md
│   │   └── references.md
│   ├── enzyme-variant-engineering/
│   │   ├── research-notes.md
│   │   └── references.md
│   └── small-molecule-lead-optimization/
│       ├── research-notes.md
│       └── references.md
├── environments/
│   ├── scRNAseq-environment/
│   │   ├── README.md
│   │   ├── ENVIRONMENT_SPEC.md
│   │   ├── config/
│   │   ├── tasks/
│   │   └── tests/
│   ├── synthesis-route-gym/
│   │   ├── README.md
│   │   ├── ENVIRONMENT_SPEC.md
│   │   ├── STATUS.md
│   │   ├── config/
│   │   ├── tasks/
│   │   └── tests/
│   ├── sirna-designing-harness/
│   │   ├── README.md
│   │   ├── ENVIRONMENT_SPEC.md
│   │   ├── STATUS.md
│   │   ├── config/
│   │   ├── tasks/
│   │   ├── tests/
│   │   ├── scripts/
│   │   ├── skills/
│   │   ├── benchmark/
│   │   └── results/
│   ├── enzyme-variant-engineering/
│   │   ├── README.md
│   │   ├── ENVIRONMENT_SPEC.md
│   │   ├── STATUS.md
│   │   ├── tasks/
│   │   ├── tests/
│   │   ├── specialist/
│   │   └── results/
│   └── small-molecule-lead-optimization/
│       ├── README.md
│       ├── ENVIRONMENT_SPEC.md
│       ├── STATUS.md
│       ├── pyproject.toml
│       ├── config/
│       ├── tasks/
│       ├── tests/
│       ├── src/
│       ├── scripts/
│       └── results/
├── docs/
│   └── decisions/
└── .github/
    └── PULL_REQUEST_TEMPLATE.md
```

Each environment has its own folder. Research notes and references are maintained in the matching `research/<environment-name>/` directory and linked from its README.

Start with the [research index](research/README.md), [scRNA-seq environment](environments/scRNAseq-environment/README.md), [synthesis route environment](environments/synthesis-route-gym/README.md), or [siRNA Designing Harness](environments/sirna-designing-harness/README.md). The siRNA contribution is In Progress: portable technical checks are implemented; scientific deployment, independent efficacy validation and maintainer review remain separate requirements.

The [Enzyme Variant Optimization environment](environments/enzyme-variant-engineering/README.md) is a minimal native-SCI contribution: a process specification, a real BglB activity/stability case, task-specific scientific evaluation, and a saved failure-focused specialist. It reuses Agent-Scientist's existing tool calls, enzyme input validations, sessions and delegation; no replacement runner is included. Base/assisted scientific runs, comparison evidence and maintainer review remain outstanding.

The [Small-Molecule Lead Optimization environment](environments/small-molecule-lead-optimization/README.md) is In Progress: a general environment with a local Agent-Scientist plugin, versioned records, advisory checks, persistent campaigns, an offline evaluator, and synthetic/native integration tests. Live scientific qualification, the real case study, issue linkage, and a matched base-agent comparison remain outstanding.

Follow [CONTRIBUTING.md](CONTRIBUTING.md) and the [pull request template](.github/PULL_REQUEST_TEMPLATE.md) for contributions. License selection is pending in [LICENSE](LICENSE).

The [Formulation Dissolution environment](https://github.com/boltzmannlabs/science-environments/tree/Rebolt/environments/formulation_dissolution) and its [research notes and references](https://github.com/boltzmannlabs/science-environments/tree/Rebolt/research/formulation_dissolution) are maintained on the `Rebolt` branch. The environment is In Progress: it reuses the existing evidence-first investigation, six empirical dissolution models, synthetic grouped-holdout checks and a bounded assumption-conditional research grid. Controlled lot measurements, calibrated product prediction, experimental formulation validation and maintainer review remain outstanding. See its model/tool inventory and execution receipts for the implemented scope.

Reserved empty directories use `.gitkeep` files so they appear on GitHub. Environment status and evidence should match the linked documents.
