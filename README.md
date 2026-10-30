# Science Environments — Rebolt

Scientific environment specifications, research, workflows, and implementations for the Agent Scientist ecosystem.

The `formulation_dissolution` environment and its matching research were migrated from `main` at commit `693311e`. Every tracked file in those two source directories is retained at its original relative path. Existing Rebolt packages remain available alongside the migrated environment.

## Repository structure

```text
science-environments/
├── README.md
├── CONTRIBUTING.md
├── LICENSE
├── research/
│   ├── README.md
│   ├── formulation_dissolution/
│   │   ├── research-notes.md
│   │   └── references.md
│   └── formulation-optimisation-gym-environments/
├── environments/
│   ├── formulation_dissolution/
│   │   ├── README.md
│   │   ├── ENVIRONMENT_SPEC.md
│   │   ├── STATUS.md
│   │   ├── MODELS_AND_TOOLS.md
│   │   ├── pyproject.toml
│   │   ├── configs/
│   │   ├── tasks/
│   │   ├── tests/
│   │   ├── scripts/
│   │   ├── benchmark/
│   │   ├── results/
│   │   ├── agents/
│   │   ├── data/
│   │   ├── docs/
│   │   ├── environment/
│   │   ├── evaluation/
│   │   ├── models/
│   │   ├── schemas/
│   │   ├── skills/
│   │   └── tools/
│   ├── formulation-optimisation-gym-environments/
│   └── retrosynthesis/
├── synthesis-route-gym/
├── docs/
│   └── decisions/
└── .github/
    └── PULL_REQUEST_TEMPLATE.md
```

The tree shows directories and primary entry points; the environment also retains its top-level Python modules, reports, source provenance, and third-party notices.

Start with the [Formulation Dissolution environment](environments/formulation_dissolution/README.md) or the [research index](research/README.md). The environment is In Progress; its [status](environments/formulation_dissolution/STATUS.md), [model and tool inventory](environments/formulation_dissolution/MODELS_AND_TOOLS.md), and [test instructions](environments/formulation_dissolution/tests/README.md) describe the implemented scope and outstanding validation.

Follow [CONTRIBUTING.md](CONTRIBUTING.md) and the [pull request template](.github/PULL_REQUEST_TEMPLATE.md) for contributions. License selection remains pending in [LICENSE](LICENSE).
