# Science Environments

Scientific environment specifications, research, workflows, and implementations for the **Agent Scientist ecosystem**.

This repository maintains a structured collection of scientific environments. Each environment contains its documentation, specifications, configuration, tasks, tests, scripts, source code, benchmarks, and results, as applicable.

## Repository Structure

```text
science-environments/
│
├── README.md
├── CONTRIBUTING.md
├── LICENSE
│
├── research/
│   ├── README.md
│   └── <research-topic>/
│       ├── research-notes.md
│       └── references.md
│
├── environments/
│   └── <environment-name>/
│       ├── README.md
│       ├── ENVIRONMENT_SPEC.md
│       ├── STATUS.md
│       ├── MODELS_AND_TOOLS.md
│       ├── config/
│       ├── tasks/
│       ├── tests/
│       ├── scripts/
│       ├── src/
│       ├── benchmark/
│       └── results/
│
├── docs/
│   └── decisions/
│
└── .github/
    └── PULL_REQUEST_TEMPLATE.md
```

## Directory Guide

### 1. `research/`

Contains scientific research and background information relevant to the environments.

Each research topic should have its own directory containing:

| File | Purpose |
|---|---|
| `research-notes.md` | Research findings, scientific background, methodology, assumptions, and observations. |
| `references.md` | Research papers, publications, datasets, documentation, and other source references. |

The `research/README.md` file provides an index of the available research topics.

### 2. `environments/`

Contains the actual scientific environment implementations and their associated documentation.

Each environment must follow the same standard structure.

| File / Directory | Purpose |
|---|---|
| `README.md` | Overview, purpose, capabilities, usage, and environment-specific instructions. |
| `ENVIRONMENT_SPEC.md` | Detailed environment specification, objectives, inputs, outputs, constraints, and expected behavior. |
| `STATUS.md` | Current development status, completed work, pending tasks, known limitations, and validation progress. |
| `MODELS_AND_TOOLS.md` | Models, tools, libraries, dependencies, and their respective roles within the environment. |
| `config/` | Configuration files, parameters, settings, and environment-specific configurations. |
| `tasks/` | Scientific tasks, task definitions, scenarios, and execution requirements. |
| `tests/` | Test cases, validation scripts, test data, and expected results. |
| `scripts/` | Utility scripts, execution scripts, and supporting automation. |
| `src/` | Environment implementation and source code. |
| `benchmark/` | Benchmark definitions, evaluation methods, metrics, and comparison criteria. |
| `results/` | Experiment outputs, benchmark results, execution records, and evaluation reports. |

Include only the files and components relevant to the environment. Do not create empty or placeholder documentation that has no meaningful content.

### 3. `docs/decisions/`

Contains important technical and architectural decisions made during environment development.

Decision documents should explain:

- The problem or requirement behind the decision.
- The options considered.
- The selected approach and its justification.
- The expected impact and trade-offs.
- Any relevant follow-up actions.

### 4. `.github/`

Contains GitHub-specific contribution and review resources.

- `PULL_REQUEST_TEMPLATE.md` – Standard format for documenting changes, implementation details, testing evidence, and review requirements.

## Environment Documentation Requirements

Every environment should maintain clear and consistent documentation.

Before considering an environment ready for review, ensure the following are addressed:

- [ ] Environment overview is documented in `README.md`.
- [ ] Scientific objectives and requirements are documented in `ENVIRONMENT_SPEC.md`.
- [ ] Development progress and pending work are updated in `STATUS.md`.
- [ ] Models and tools are documented in `MODELS_AND_TOOLS.md`.
- [ ] Required configurations are maintained in `config/`.
- [ ] Scientific tasks and scenarios are documented in `tasks/`.
- [ ] Relevant test cases are maintained in `tests/`.
- [ ] Supporting scripts and source code are organized appropriately.
- [ ] Benchmarking methodology and evaluation criteria are documented.
- [ ] Relevant execution results and validation evidence are recorded.

## Validation and Evidence

Environment validation should distinguish between technical correctness and scientific validity.

**Technical validation** should cover:

- Environment setup and configuration.
- Dependency and compatibility checks.
- Task execution and workflow completion.
- Input/output validation.
- Automated tests and reproducibility checks.

**Scientific validation** should cover:

- Scientific correctness of the methodology.
- Relevance and reliability of selected models and tools.
- Evaluation against appropriate datasets or reference results.
- Benchmark performance and comparison criteria.
- Independent validation where required.

Passing technical tests does not automatically establish scientific validity. The current status and supporting evidence must be documented in the environment's `STATUS.md`.

## Contribution Guidelines

All repository contributions must follow the workflow documented in [`CONTRIBUTING.md`](CONTRIBUTING.md).

The expected workflow is:

1. Create or identify a GitHub issue describing the task, improvement, or bug.
2. Create a separate branch for the work.
3. Make changes within the appropriate directory.
4. Update relevant documentation and validation evidence.
5. Commit changes with a meaningful commit message.
6. Raise a Pull Request against the `main` branch.
7. Include the related issue, implementation summary, and testing evidence.
8. Address review comments and required changes.
9. Merge only after the required reviews and checks are completed.

Use the repository's [Pull Request template](.github/PULL_REQUEST_TEMPLATE.md) when raising a PR.

## Important Notes

- Maintain the defined directory structure across all scientific environments.
- Keep research documentation separate from environment implementation.
- Update documentation whenever implementation, models, tools, or workflows change.
- Do not report an environment as complete solely because its code or technical tests are available.
- Record known limitations, pending validations, and outstanding requirements transparently.
- Avoid duplicating common research or implementation documentation across environments; use clear references where appropriate.

## License

Refer to the repository's `LICENSE` file for licensing information.
