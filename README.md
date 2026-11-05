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
│   ├── formulation-optimisation-gym-environments/
│   ├── impurity-retrosynthesis/
│   └── retro_environment/        # target-specific research notes and references
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
│   ├── impurity-retrosynthesis/
│   └── retro_environment/        # target-specific computational route audit
├── synthesis-route-gym/
├── docs/
│   └── decisions/
└── .github/
    └── PULL_REQUEST_TEMPLATE.md
```

The tree shows directories and primary entry points; the environment also retains its top-level Python modules, reports, source provenance, and third-party notices.

Start with the [Formulation Dissolution environment](environments/formulation_dissolution/README.md), the [retro_environment case study](environments/retro_environment/README.md), or the [research index](research/README.md). The retro_environment is a model-output audit, not an experimentally verified synthesis. The formulation environment is In Progress; its [status](environments/formulation_dissolution/STATUS.md), [model and tool inventory](environments/formulation_dissolution/MODELS_AND_TOOLS.md), and [test instructions](environments/formulation_dissolution/tests/README.md) describe its implemented scope and outstanding validation.

The [Impurity Retrosynthesis evidence environment](environments/impurity-retrosynthesis/README.md) provides conservative route-export auditing, synthetic-fixture tests and a [literature benchmark](environments/impurity-retrosynthesis/benchmark/README.md) without publishing profile-scoped raw outputs or claiming experimental validation. Its [research notes](research/impurity-retrosynthesis/research-notes.md), [current status](environments/impurity-retrosynthesis/STATUS.md) and [source review](research/impurity-retrosynthesis/references.md) distinguish model predictions from primary patent reports.

Follow [CONTRIBUTING.md](CONTRIBUTING.md) and the [pull request template](.github/PULL_REQUEST_TEMPLATE.md) for contributions. License selection remains pending in [LICENSE](LICENSE).
