# Science Environments

Scientific environment specifications, research, workflows, and implementations for the Agent Scientist ecosystem.

Research notes and sources live in `research/`. Environment requirements and implementations live in `environments/`. The enzyme-optimization and protein-stability entries are proposed outlines; no implementation or validation is claimed.

## Structure

```text
science-environments/
├── README.md
├── CONTRIBUTING.md
├── LICENSE
├── research/
│   ├── README.md
│   ├── enzyme-optimization/
│   │   ├── research-notes.md
│   │   └── references.md
│   └── protein-stability/
│       ├── research-notes.md
│       └── references.md
├── environments/
│   ├── enzyme-optimization/
│   │   ├── README.md
│   │   ├── ENVIRONMENT_SPEC.md
│   │   ├── config/
│   │   ├── tasks/
│   │   └── tests/
│   └── protein-stability/
│       ├── README.md
│       └── ENVIRONMENT_SPEC.md
├── docs/
│   └── decisions/
└── .github/
    └── PULL_REQUEST_TEMPLATE.md
```

Start with the [research index](research/README.md), [enzyme-optimization outline](environments/enzyme-optimization/README.md), or [protein-stability outline](environments/protein-stability/README.md).

Follow [CONTRIBUTING.md](CONTRIBUTING.md) and the [pull request template](.github/PULL_REQUEST_TEMPLATE.md) for contributions. License selection is pending in [LICENSE](LICENSE).

Empty directories use `.gitkeep` files so they appear on GitHub. Existing project contributions are retained alongside this base structure.
