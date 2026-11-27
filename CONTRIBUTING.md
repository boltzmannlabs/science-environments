# Contributing to Science Environments

This guide defines the contribution workflow for the `science-environments` repository. It applies to scientific research, environment specifications, task definitions, configuration, workflows, code, tests, benchmarks, results, and documentation.

> **Core principle:** Every contribution must be understandable, traceable, appropriately validated, and reviewed before it is merged into `main`.

For the repository architecture and recommended file formats, see the root [`README.md`](README.md).

## Contents

- [Contribution principles](#contribution-principles)
- [Choose the contribution type](#choose-the-contribution-type)
- [Repository architecture](#repository-architecture)
- [Standard workflow](#standard-workflow)
- [Examples by contribution type](#examples-by-contribution-type)
- [Task, run, and result traceability](#task-run-and-result-traceability)
- [Mandatory file and artifact naming rules](#mandatory-file-and-artifact-naming-rules)
- [Commit message convention](#commit-message-convention)
- [Pull Request requirements](#pull-request-requirements)
- [Review and merge](#review-and-merge)
- [Definition of done](#definition-of-done)

## Contribution principles

1. Keep research, task definitions, configuration, execution records, results, and benchmark definitions logically separate.
2. Prefer small, focused Pull Requests that address one coherent change.
3. Preserve scientific provenance. Never fabricate metrics, model versions, dataset versions, or validation outcomes.
4. Distinguish planned work, completed computation, technical validation, scientific evaluation, and experimental validation.
5. Do not delete or overwrite historical evidence as part of routine cleanup.
6. Document intentional deviations from the recommended structure.
7. Do not commit credentials, tokens, private keys, personal data, or unapproved restricted datasets.

## Choose the contribution type

| Contribution | Typical location | Required evidence |
|---|---|---|
| Research / literature review | `research/<topic>/` | Sources, methodology, findings, limitations |
| New environment | `environments/<name>/` | Environment README/specification, status, task catalogue |
| New or updated task | `environments/<name>/tasks/` | Objective, inputs, workflow, outputs, acceptance criteria |
| Configuration change | `environments/<name>/config/` | Valid schema/config and explanation of impact |
| Workflow or source change | `scripts/` or `src/` | Tests or reproducible validation |
| Benchmark change | `benchmark/` | Protocol, dataset provenance, metric definitions |
| Execution/result publication | `runs/` and `results/` | Run record, input/config provenance, artifacts, report |
| Documentation-only change | Relevant `.md` file | Correct links, examples, and consistency |

## Repository architecture

The following is the recommended logical layout. Not every environment requires every directory.

```text
science-environments/
├── README.md
├── CONTRIBUTING.md
├── research/
│   └── <topic>/
├── environments/
│   └── <environment-name>/
│       ├── README.md
│       ├── ENVIRONMENT_SPEC.md
│       ├── STATUS.md
│       ├── MODELS_AND_TOOLS.md
│       ├── config/
│       │   ├── schemas/
│       │   ├── shared/
│       │   └── tasks/
│       ├── tasks/
│       ├── runs/
│       ├── results/
│       ├── tests/
│       ├── scripts/
│       ├── src/
│       └── benchmark/
└── docs/
    └── decisions/
```

### Separation of responsibilities

- `research/`: scientific background, literature review, feasibility findings.
- `tasks/`: what the scientific workflow must accomplish.
- `config/`: reusable settings, schemas, and task configuration.
- `runs/`: each execution event, including failed or partial executions.
- `results/`: artifacts produced by a specific run.
- `benchmark/`: benchmark definitions, reference data, evaluation protocols, and metric definitions.

Do not store run-specific historical outputs under `config/`. Do not use `benchmark/` as an unstructured alternative to `results/`. Benchmark executions still need identifiable run records and provenance.

## Standard workflow

### Step 1 — Create or identify an Issue

Create an Issue for significant work, or link an existing Issue. The Issue should explain:

- Problem or objective.
- Scope and affected environment/research topic.
- Expected outcome.
- Acceptance criteria.
- Dependencies, references, and risks.
- Whether scientific execution or validation is expected.

For a small typo or similarly trivial documentation correction, an Issue may be unnecessary if repository maintainers permit it.

### Step 2 — Update your local `main` and create a branch

```bash
git checkout main
git pull origin main
git checkout -b <type>/<short-description>
```

Branch naming:

| Type | Prefix | Example |
|---|---|---|
| Feature / new capability | `feat/` | `feat/add-enzyme-task` |
| Documentation | `docs/` | `docs/add-task-format-examples` |
| Bug fix | `fix/` | `fix/task-result-path` |
| Configuration | `config/` | `config/update-task-schema` |
| Tests | `test/` | `test/add-provenance-validation` |
| Maintenance | `chore/` | `chore/normalize-result-layout` |
| Research | `research/` | `research/review-enzyme-design-methods` |

Use lowercase kebab-case, avoid spaces, and keep the branch focused.

### Step 3 — Make the change in the correct location

Before adding files, inspect the environment's existing structure and documentation. Reuse established task IDs and conventions. Do not introduce a second naming system without documenting the migration.

Update the relevant README, task index, environment status, model/tool inventory, or benchmark registry when the change affects them.

### Step 4 — Validate locally

Run the checks relevant to the contribution. Record the commands and outcomes in the PR.

Examples:

```bash
# Inspect the change
git status --short
git diff --check
git diff --stat

# Validate JSON
python -m json.tool path/to/file.json

# Validate YAML (if PyYAML is installed)
python -c "import yaml; yaml.safe_load(open('path/to/file.yaml'))"

# Run the environment's documented tests
pytest -q
```

Use the actual test command documented by the environment. Do not report a command as passed if it was not executed.

If execution is not applicable, state `Not run` and explain why. If execution is blocked by missing compute, credentials, data, or dependencies, record the blocker and the checks that were still completed.

### Step 5 — Commit and push

Stage only the intended files:

```bash
git status --short
git add path/to/changed-file path/to/related-file
git diff --cached
git commit -m "docs: add task and run format examples"
git push -u origin <type>/<short-description>
```

Avoid `git add .` when unrelated or generated files may be present. Inspect the staged diff before committing.

### Step 6 — Open a Pull Request

Open a PR from your branch into `main`. Use `.github/PULL_REQUEST_TEMPLATE.md` if present.

A PR should include:
- What changed and why.
- Related Issue.
- Contribution type.
- Important files/directories changed.
- Validation performed and actual outcome.
- Evidence or artifact links, where relevant.
- Known limitations and follow-up work.

Link the Issue using `Closes #<issue-number>` when the PR fully resolves it. Do not use `Closes` for an Issue that is only partially addressed.

### Step 7 — Review and respond

Reviewers should check:
- Scientific accuracy and source quality.
- Task/config/run/result consistency.
- Folder and naming conventions.
- Schema validity and dependency changes.
- Tests and validation evidence.
- Provenance, licensing, and sensitive data.
- Whether claims match the evidence.

Respond to review comments and push updates to the same branch. Resolve conversations only after the requested change has been made or the reviewer agrees it is addressed.

### Step 8 — Merge and update records

After required approvals and checks:
- Merge using the repository's permitted merge strategy.
- Confirm the PR is merged into `main`.
- Update relevant indexes and status documents if they were not part of the PR.
- Close the associated Issue when resolved.
- Delete the merged branch when appropriate.
- Communicate material changes to affected contributors.

Do not merge a PR merely because its code executes. Scientific claims and evidence must also be represented accurately.

## Mandatory file and artifact naming rules

**Every contributor is responsible for naming files in the prescribed order before committing
or raising a Pull Request.** Do not rely on maintainers to rename files after submission.

This rule applies to task definitions, configurations, run records, reports, result artifacts,
benchmark files, and generated scientific outputs. Existing legacy names should be migrated
through a reviewed mapping rather than renamed silently.

### 1. General filename rules

- Use lowercase for directory names and normalized filename components.
- Use underscores (`_`) between components in generated artifact filenames.
- Do not use spaces in filenames.
- Never use Windows-invalid characters: `< > : " / \ | ? *`.
- Avoid trailing spaces and trailing periods.
- Preserve the correct original file extension.
- Do not truncate, round, or alter scientific parameter values just to make a filename shorter.
- Do not invent artifact IDs, run IDs, timestamps, model versions, or parameter values.
- Check for duplicate names and case-only collisions before committing.

### 2. Required generated artifact component order

Use this exact order:

```text
<artifact_id>_<tool_name>_<timestamp_utc>_<run_reference>_<model_identifier>_<parameters>.<extension>
```

| Position | Component | Example | Requirement |
|---:|---|---|---|
| 1 | Artifact ID | `6afb145e239a6b9f38bf435f` | Use verified artifact/source ID |
| 2 | Tool name | `antibmpnn` | Normalized lowercase tool name |
| 3 | UTC timestamp | `20261116T143406Z` | Format: `YYYYMMDDTHHMMSSZ` |
| 4 | Run reference | `2465ae` | Must map to the full run ID |
| 5 | Model identifier | `model020` | Use the actual model/checkpoint identity |
| 6 | Parameters | `n0.0_t0.1` | Keep parameter names and order consistent |
| 7 | Extension | `.fa` | Preserve the actual file type |

**Do not change this order between environments or contributors.**

### 3. Before-and-after example

Raw tool-generated filename:

```text
6afb145e239a6b9f38bf435f_AntiBMPNN - 20261116-143406Z - 2465ae|antibmpnn_020|N-0.0|T-0.1.fa
```

Required normalized repository filename:

```text
6afb145e239a6b9f38bf435f_antibmpnn_20261116T143406Z_2465ae_model020_n0.0_t0.1.fa
```

The normalized example is illustrative. Contributors must derive every component from the actual execution metadata. If a component is unavailable, do not fabricate it; use a documented fallback agreed by the environment maintainer and record the deviation in metadata.

### 4. Task, run, and result directory names

Use stable identifiers and descriptive slugs:

```text
tasks/
└── TASK-014-il36r-antibody-redesign/
    └── task.md

runs/
└── TASK-014/
    └── RUN-20261116-001/
        └── run_metadata.json

results/
└── TASK-014/
    └── RUN-20261116-001/
        ├── provenance.json
        ├── REPORT.md
        └── artifacts/
            └── <normalized-artifact-filename>
```

A task can have multiple runs. Every run must point to one stable task ID. Every result and artifact must point to the run that produced it. Do not infer this relationship from a descriptive folder name alone.

### 5. Preserve original tool names for provenance

Sanitize the on-disk filename, but preserve the original tool-generated filename in the run manifest or artifact metadata when it is scientifically or operationally relevant.

Example metadata:

```json
{
  "task_id": "TASK-014",
  "run_id": "RUN-20261116-001",
  "artifact_id": "6afb145e239a6b9f38bf435f",
  "tool": "AntiBMPNN",
  "model_identifier": "antibmpnn_020",
  "original_filename": "6afb145e239a6b9f38bf435f_AntiBMPNN - 20261116-143406Z - 2465ae|antibmpnn_020|N-0.0|T-0.1.fa",
  "stored_filename": "6afb145e_antibmpnn_20261116T143406Z_2465ae_model020_n0.0_t0.1.fa",
  "parameters": {
    "N": 0.0,
    "T": 0.1
  }
}
```

This keeps the original provenance without placing an unsupported character in the repository path.

### 6. Mandatory pre-commit checklist

Before committing or opening a PR, the contributor must verify:

- [ ] Filename components follow the prescribed order.
- [ ] No spaces or Windows-invalid characters exist in any path component.
- [ ] UTC timestamps use `YYYYMMDDTHHMMSSZ`.
- [ ] Tool and model identifiers match the execution record.
- [ ] Parameter names, values, and ordering are accurate.
- [ ] File extensions and file contents are preserved.
- [ ] Artifact paths are inside the correct task/run result directory.
- [ ] `task_id`, `run_id`, and artifact metadata agree.
- [ ] No duplicate names or case-only path collisions exist.
- [ ] Original tool filenames are retained in metadata when needed.
- [ ] Filename validation has been run and its outcome is reported in the PR.

A PR containing newly added or renamed generated artifacts that violate these rules should be
corrected before merge.

### 7. Automated validation

Contributors should run a repository filename check before committing. The repository should
also enforce this check in CI so that invalid paths are caught before merge.

Example local check:

```python
from pathlib import Path
import re
import sys

INVALID_CHARS = re.compile(r'[<>:"/\\\\|?*]')

def find_invalid_paths(root: Path) -> list[str]:
    invalid = []
    for path in root.rglob("*"):
        # Check each path component, not only the final filename.
        if any(INVALID_CHARS.search(part) for part in path.parts):
            invalid.append(str(path))
    return invalid

if __name__ == "__main__":
    root = Path("environments")
    failures = find_invalid_paths(root)

    if failures:
        print("Invalid paths found:")
        for item in failures:
            print(f" - {item}")
        sys.exit(1)

    print("All checked paths are compatible with Windows filename rules.")
```

Run the validator from the repository root. A clean result means the checked paths do not contain
the listed prohibited characters; it does not replace checks for naming order, duplicate IDs,
metadata consistency, or artifact provenance.

## Examples by contribution type

The examples below show the expected scope and file placement. They are templates, not claims that an execution or validation has taken place.

### Example A — Documentation-only contribution

**Scenario:** Clarify the task execution instructions for an existing environment.

Branch:

```bash
git checkout -b docs/clarify-enzyme-task-instructions
```

Possible changed files:

```text
environments/<environment-name>/
├── README.md
└── tasks/
    └── TASK-001/
        └── task.md
```

Validation:
- Check Markdown headings and code fences.
- Verify relative links and file paths.
- Confirm examples match the current implementation.
- Confirm no scientific claim was added without a source.

Example commit:

```bash
git commit -m "docs: clarify enzyme task execution instructions"
```

No scientific run is required for a documentation-only change unless the documentation change alters or asserts execution behavior.

### Example B — New research topic

**Scenario:** Add a literature review on a scientific method.

Branch:

```bash
git checkout -b research/review-protein-design-methods
```

Suggested structure:

```text
research/
├── README.md
└── protein-design-methods/
    ├── research-notes.md
    └── references.md
```

`research-notes.md` should include:

```markdown
# Research Notes — <Topic>

## Research question
What question is this review intended to answer?

## Scope
What methods, systems, time period, or evidence are included/excluded?

## Methodology
How were sources identified and assessed?

## Findings
Summarize findings and distinguish source-reported results from interpretation.

## Evidence quality
Discuss dataset relevance, baselines, limitations, and reproducibility.

## Open questions
List unresolved questions and missing evidence.

## Conclusion
State what the evidence supports and what it does not establish.
```

`references.md` should include complete citations and stable DOI/URLs. Include publication details and a brief relevance note. Update `research/README.md` with the new topic.

### Example C — Add a new scientific task

**Scenario:** Add a new task to an existing environment.

Suggested files:

```text
environments/<environment-name>/
├── config/
│   ├── schemas/
│   │   └── request.schema.json
│   └── tasks/
│       └── TASK-002.yaml
├── tasks/
│   ├── README.md
│   └── TASK-002/
│       └── task.md
└── README.md
```

The task definition should state:
- Stable task ID and title.
- Objective and scientific rationale.
- Required/optional inputs and their formats.
- Method and workflow steps.
- Constraints, assumptions, and unsupported cases.
- Expected outputs and schemas.
- Acceptance criteria and references.

Update the task index and environment README. If the task has not been executed, mark its status as planned or active; do not create placeholder results that look like completed evidence.

### Example D — Add or update task configuration

**Scenario:** Introduce a task-specific model parameter.

Suggested files:

```text
environments/<environment-name>/
└── config/
    ├── schemas/
    │   └── request.schema.json
    └── tasks/
        └── TASK-002.yaml
```

Validation should include:
- Schema or syntax validation.
- Documentation of each non-obvious parameter.
- Defaults and allowed ranges where known.
- Compatibility impact.
- Confirmation that secrets are not committed.

When a run executes, preserve the resolved configuration or its hash with the run record. Do not edit an old run's configuration in place.

### Example E — Publish an execution and its results

**Scenario:** Execute `TASK-002` and publish the outputs.

Suggested structure:

```text
environments/<environment-name>/
├── runs/
│   └── TASK-002/
│       └── RUN-20261127-001/
│           ├── run.json
│           ├── input/
│           │   └── manifest.json
│           └── execution.log
└── results/
    └── TASK-002/
        └── RUN-20261127-001/
            ├── REPORT.md
            ├── metrics.json
            ├── artifacts/
            └── provenance.json
```

Required traceability:
- `run.json` contains `task_id`, `run_id`, configuration identity/hash, input manifest, code revision, model identity, timestamps, and status.
- `provenance.json` contains the same task/run identity and lists actual output artifacts.
- The report explains the method actually executed, results, validation, limitations, and interpretation.
- Failed or partial executions remain recorded under `runs/`; do not publish incomplete outputs as successful results.

### Example F — Add a benchmark

**Scenario:** Define a benchmark protocol and evaluate a model.

Suggested structure:

```text
environments/<environment-name>/benchmark/
├── definitions/
│   └── BM-001/
│       ├── benchmark.yaml
│       └── README.md
├── reference_data/
├── evaluation/
└── benchmark_registry.json
```

Document dataset source/version/checksum, inclusion and exclusion criteria, split strategy, baseline, metric formulas, aggregation method, and acceptance criteria before interpreting results.

Store actual benchmark executions with run IDs and result provenance. Clearly label whether evidence is published reference data, a reproduced result, a synthetic fixture, a component-level test, a computational evaluation, or an experimental result.

## Task, run, and result traceability

Every execution should be reconstructable through explicit identifiers, not inferred from directory names.

| Record | Must identify |
|---|---|
| Task definition | `task_id` |
| Configuration | `config_id`, version, and resolved hash where used |
| Run record | `task_id`, `run_id`, configuration, inputs, code revision, model identity, status |
| Result provenance | `task_id`, `run_id`, configuration/input identity, actual artifacts |

A task can have multiple runs. A run belongs to one task. Results must reference the run that generated them.

Suggested run statuses: `queued`, `running`, `completed`, `failed`, `cancelled`, `partial`.

Suggested evidence labels: `synthetic`, `literature_reported`, `reproduced`, `computational_evaluation`, `experimental`, `not_evaluated`.

Preserve historical IDs and paths during migrations. If a legacy folder is renamed, include a migration map or clear cross-reference.

## Commit message convention

Use:

```text
<type>: <short imperative description>
```

Recommended types:

| Type | Use |
|---|---|
| `feat` | New functionality or environment capability |
| `fix` | Correct a defect |
| `docs` | Documentation-only changes |
| `research` | Research notes or literature review |
| `config` | Configuration/schema changes |
| `test` | Test additions or corrections |
| `bench` | Benchmark definitions or evaluation changes |
| `chore` | Maintenance and repository organization |
| `refactor` | Code restructuring without intended behavior change |

Examples:

```bash
git commit -m "feat: add enzyme variant task"
git commit -m "docs: add task and run format examples"
git commit -m "research: document protein design literature review"
git commit -m "config: add task request schema"
git commit -m "test: validate task result provenance"
git commit -m "bench: define held-out evaluation protocol"
git commit -m "chore: normalize result directory naming"
```

Avoid vague messages such as `update`, `changes`, `final`, or `new files`.

## Pull Request requirements

Every PR should provide:

1. Summary and motivation.
2. Related Issue.
3. Contribution type.
4. Files/directories changed.
5. Validation performed, with commands and outcomes.
6. Evidence links, where relevant.
7. Known limitations, deviations, and follow-up work.

A suggested PR description:

```markdown
## Summary
Describe what changed and why.

## Related Issue
Closes #<issue-number>

## Contribution type
- [ ] Research
- [ ] New environment
- [ ] Task definition
- [ ] Configuration/schema
- [ ] Source/workflow
- [ ] Tests
- [ ] Benchmark
- [ ] Results/provenance
- [ ] Documentation
- [ ] Maintenance

## Files and structure
List the important files and directories changed.

## Validation
| Check | Command / evidence | Outcome |
|---|---|---|
| Markdown/link review | ... | Pass / Not run |
| Schema validation | ... | Pass / Not applicable |
| Tests | ... | Pass / Fail / Not run |
| Scientific evaluation | ... | Completed / Not applicable / Blocked |

## Scientific and technical notes
Describe assumptions, evidence type, and interpretation limits.

## Known limitations / follow-up
List unresolved items and explain any checks not performed.
```

## Review and merge

At least one relevant reviewer should approve the PR, subject to repository branch protection and team policy. Reviewers should request changes when the task/result mapping is unclear, scientific claims are unsupported, provenance is missing, or validation is misrepresented.

Use the merge strategy configured by repository maintainers. Squash merge may be used when permitted and appropriate. Do not assume that a contributor can bypass branch protection or required checks.

## Definition of done

- [ ] Issue created or identified where appropriate.
- [ ] Branch created from the latest `main`.
- [ ] Changes placed in the correct directory.
- [ ] Naming and identifiers follow repository conventions.
- [ ] Generated artifact filenames follow the mandatory component order and pass filename validation.
- [ ] Relevant documentation and indexes updated.
- [ ] Configuration/schema checks completed where applicable.
- [ ] Tests and scientific validation run where applicable, with outcomes recorded.
- [ ] No credentials, private data, or unintended generated files included.
- [ ] PR description and evidence are complete.
- [ ] Required review comments addressed and approvals obtained.
- [ ] PR merged into `main`.
- [ ] Related Issue and status records updated where applicable.

## Final guideline

The `main` branch should represent the reviewed and traceable state of the repository. Contributions may be research-only, documentation-only, configuration-only, or implementation-focused; the required validation should be appropriate to the change, and must be reported honestly.

**Every contribution should be traceable, reproducible where applicable, documented, and reviewed.**
