# Science Environments

Scientific environment specifications, research, workflows, and implementations for the Agent Scientist ecosystem.

Research notes and sources are organized by environment in `research/`. Environment requirements, configuration, tasks, and applicable tests are organized in `environments/`.

## Structure

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
│   └── synthesis-route-gym/
│       ├── research-notes.md
│       └── references.md
├── environments/
│   ├── scRNAseq-environment/
│   │   ├── README.md
│   │   ├── ENVIRONMENT_SPEC.md
│   │   ├── config/
│   │   ├── tasks/
│   │   └── tests/
│   └── synthesis-route-gym/
│       ├── README.md
│       ├── ENVIRONMENT_SPEC.md
│       ├── STATUS.md
│       ├── config/
│       ├── tasks/
│       └── tests/
├── docs/
│   └── decisions/
└── .github/
    └── PULL_REQUEST_TEMPLATE.md
```

Start with the [research index](research/README.md), [scRNA-seq environment](environments/scRNAseq-environment/README.md), or [synthesis route environment](environments/synthesis-route-gym/README.md).

Follow [CONTRIBUTING.md](CONTRIBUTING.md) and the [pull request template](.github/PULL_REQUEST_TEMPLATE.md) for contributions. License selection is pending in [LICENSE](LICENSE).

Reserved empty directories use `.gitkeep` files so they appear on GitHub. Environment status and evidence should match the linked documents.
