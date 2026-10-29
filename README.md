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
│   └── sirna-designing-harness/
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
│   └── sirna-designing-harness/
│       ├── README.md
│       ├── ENVIRONMENT_SPEC.md
│       ├── STATUS.md
│       ├── config/
│       ├── tasks/
│       ├── tests/
│       ├── scripts/
│       ├── skills/
│       ├── benchmark/
│       └── results/
├── docs/
│   └── decisions/
└── .github/
    └── PULL_REQUEST_TEMPLATE.md
```

Each environment has its own folder. Research notes and references are maintained in the matching `research/<environment-name>/` directory and linked from its README.

Start with the [research index](research/README.md), [scRNA-seq environment](environments/scRNAseq-environment/README.md), [synthesis route environment](environments/synthesis-route-gym/README.md), or [siRNA Designing Harness](environments/sirna-designing-harness/README.md). The siRNA environment implements portable technical validation and candidate-property reporting, including a source-bound recorded KRAS14 case that passes the declared technical gates. Its repository lifecycle remains In Progress pending separately configured backend deployment and maintainer review; technical and biological evaluation scopes remain distinct.

Follow [CONTRIBUTING.md](CONTRIBUTING.md) and the [pull request template](.github/PULL_REQUEST_TEMPLATE.md) for contributions. License selection is pending in [LICENSE](LICENSE).

Reserved empty directories use `.gitkeep` files so they appear on GitHub. Environment status and evidence should match the linked documents.
