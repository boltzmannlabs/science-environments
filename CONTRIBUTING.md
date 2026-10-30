# Contributing to Science-Environments

## 1. Purpose

This document defines the standard contribution workflow for the Science-Environments repository.

It applies to all contributors working on:
- Scientific research and feasibility studies.
- Environment specifications and design.
- Scientific tasks and workflows.
- Configuration and dependencies.
- Source code, scripts and tests.
- Benchmarks and evaluation.
- Documentation and repository structure.

Every contribution must follow the same GitHub workflow to ensure consistency, traceability, reproducibility and maintainability.

**Core principle:** Every contribution must be documented, validated and reviewed before merging into `main`.

---

## 2. Repository Architecture

The repository maintains a separation between research activities and environment implementation.

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

The above represents the general organization. Not every environment must contain every directory or document.

### 2.1 Research Directory

Location: `research/`

The research directory contains scientific investigations and preparatory work required to understand and design an environment.

Expected documents:

| File | Purpose |
|---|---|
| `research-notes.md` | Research findings, problem definition, methodology, observations and feasibility |
| `references.md` | Scientific papers, publications, datasets, documentation and external resources |

**Guidelines:**
- Keep research findings separate from implementation.
- Include references for scientific claims.
- Document assumptions and limitations.
- Record relevant findings and unresolved questions.
- Update research documentation when significant findings change.

### 2.2 Environments Directory

Location: `environments/`

This directory contains the actual scientific environments and their supporting components.

Expected documentation:

| File | Purpose |
|---|---|
| `README.md` | Environment overview, setup and usage instructions |
| `ENVIRONMENT_SPEC.md` | Detailed technical and scientific environment specification |
| `STATUS.md` | Current development status, completed work, blockers and pending activities |
| `MODELS_AND_TOOLS.md` | Models, tools, versions and their roles, where applicable |

Expected directories, where applicable:

| Directory | Purpose |
|---|---|
| `config/` | Environment and execution configurations |
| `tasks/` | Scientific task definitions and execution workflows |
| `tests/` | Validation and testing resources |
| `scripts/` | Utility and execution scripts |
| `src/` | Environment implementation and source code |
| `benchmark/` | Benchmark definitions and evaluation resources |
| `results/` | Relevant experimental results and evaluation outputs |
| `skills/` | Agent skills and reusable capabilities, where applicable |

**Guidelines:**
- Maintain a clear separation between environment components.
- Document dependencies and required versions.
- Provide reproducible execution instructions.
- Keep task definitions and expected outputs understandable.
- Avoid committing temporary files, caches and unnecessary generated artifacts.

### 2.3 Documentation and Decisions

Location: `docs/decisions/`

This directory maintains important decisions related to repository architecture, scientific methodology and environment design.

Decision records should include:

- Decision title and date.
- Context and problem statement.
- Options considered.
- Final decision.
- Reasoning behind the decision.
- Consequences and trade-offs.
- Relevant references.

Create a decision record when a change has long-term architectural, scientific or organizational implications. Routine updates do not require a decision record.

---

## 3. Standard Contribution Workflow

All contributors must follow the eight stages below.

### Step 1: Create or Select a GitHub Issue

Before starting work, create a new Issue or identify an existing Issue.

Every Issue should define:

- Objective and problem statement.
- Scope of work.
- Expected outcome.
- Acceptance criteria.
- Affected research topic or environment.
- Dependencies and references, where applicable.

Examples:
- Add research documentation for retrosynthesis.
- Update the enzyme variant optimization specification.
- Introduce a new scientific task.
- Update environment dependencies.
- Add benchmark evaluation criteria.

### Step 2: Create a Working Branch

Always create a separate branch from the latest `main`.

```bash
git checkout main
git pull origin main
git checkout -b <branch-name>
```

Branch naming conventions:

| Type | Prefix | Example |
|---|---|---|
| New feature/environment | `feat/` | `feat/add-new-environment` |
| Documentation | `docs/` | `docs/update-research-notes` |
| Bug fix | `fix/` | `fix/configuration-error` |
| Configuration | `config/` | `config/update-dependencies` |
| Repository maintenance | `chore/` | `chore/update-folder-structure` |

Rules:
- Use descriptive branch names.
- Avoid spaces.
- Keep branches focused on one task.
- Do not make direct commits to `main`.

### Step 3: Make the Changes

Implement the changes within the appropriate repository directory.

**For research contributions:**
- Update the relevant `research/<topic>/` directory.
- Maintain `research-notes.md`.
- Update `references.md`.
- Document findings, assumptions and limitations.
- Update the research index if a new topic is introduced.

**For environment contributions:**
- Update the appropriate `environments/<environment-name>/` directory.
- Maintain `README.md`.
- Update `ENVIRONMENT_SPEC.md`.
- Update `STATUS.md`.
- Update configurations, tasks, tests and supporting files as required.
- Update `MODELS_AND_TOOLS.md` when relevant.

**For repository-level contributions:**
- Follow the established root-level structure.
- Update relevant documentation.
- Record significant architectural decisions in `docs/decisions/`.

### Step 4: Validate Locally

Before creating a Pull Request, contributors must verify their changes.

**Research validation:**
- [ ] Research notes are complete and understandable.
- [ ] Scientific claims have appropriate references.
- [ ] References are accessible and correctly cited.
- [ ] Assumptions and limitations are documented.
- [ ] Research findings are placed in the correct directory.

**Environment validation:**
- [ ] Folder structure follows repository conventions.
- [ ] Required documentation is present.
- [ ] Configuration files have valid syntax.
- [ ] Dependencies and versions are documented.
- [ ] Setup instructions are accurate.
- [ ] Tasks and input/output specifications are documented.
- [ ] Environment execution has been tested, where applicable.
- [ ] Tests and benchmark definitions are verified, where applicable.
- [ ] Expected results and known limitations are documented.

**Repository validation:**
- [ ] No unrelated files are included.
- [ ] No credentials or sensitive information are committed.
- [ ] No unnecessary generated files or caches are included.
- [ ] Relevant README and index documents are updated.

If execution is not applicable or cannot be performed, document the reason and indicate which validation checks were completed.

### Step 5: Open a Pull Request

After local validation, push the working branch.

```bash
git add .
git commit -m "docs: update retrosynthesis research notes"
git push origin <branch-name>
```

Create a Pull Request targeting `main`.

Every PR must include:

1. Summary of changes.
2. Related GitHub Issue.
3. Contribution type.
4. Files and directories modified.
5. Validation performed.
6. Validation evidence, where applicable.
7. Known limitations or pending work.

Use the existing `.github/PULL_REQUEST_TEMPLATE.md`.

Link the relevant Issue:

`Closes #ISSUE_NUMBER`

### Step 6: Review and Approval

Every Pull Request must undergo manual review.

Reviewers should verify:

- Scientific correctness and relevance.
- Repository structure and naming conventions.
- Completeness of documentation.
- Dependency and configuration correctness.
- Reproducibility, where applicable.
- Task definitions and input/output specifications.
- Validation evidence.

For research contributions, the reviewer should assess the quality of scientific findings and references.

For environment contributions, the reviewer should assess the implementation, execution requirements and reproducibility.

At least one relevant reviewer must approve the PR.

All required review comments must be resolved before merging.

### Step 7: Merge and Close the Issue

Once approval is obtained:

- Verify that review comments are resolved.
- Ensure the PR targets `main`.
- Resolve merge conflicts.
- Use Squash and Merge as the recommended merge strategy.
- Confirm the changes are available in `main`.
- Close the associated Issue.
- Delete the merged working branch.

Only reviewed and approved contributions should enter `main`.

### Step 8: Update Repository Records

After merging:

- Update the root README when repository-level changes affect navigation or overview.
- Update `research/README.md` when new research topics are introduced.
- Update the relevant environment documentation.
- Update environment status.
- Record significant decisions in `docs/decisions/`.
- Update the changelog or version information when a meaningful release warrants it.
- Communicate important changes to the team.

Not every contribution requires a release or version increment.

---

## 4. Commit Message Convention

Use the following format:

```text
<type>: <short description>
```

Examples:

```bash
git commit -m "feat: add new scientific environment"
git commit -m "docs: update research findings"
git commit -m "fix: correct environment configuration"
git commit -m "config: update dependency versions"
git commit -m "chore: reorganize repository structure"
```

Avoid generic messages such as:

- update
- changes
- final
- new files
- modifications

Commit messages must clearly communicate the purpose of the change.

---

## 5. Pull Request Requirements

All contributors must use the existing Pull Request template.

The following information is mandatory:

- Summary and purpose.
- Related Issue.
- Type of contribution.
- Files changed.
- Validation performed.
- Evidence, where applicable.
- Known limitations.

Pull Requests must be focused and should not combine unrelated changes.

---

## 6. Repository Governance Rules

| Area | Standard |
|---|---|
| Default branch | `main` |
| Direct push to main | Not permitted |
| Issue tracking | Required for significant changes |
| Branch creation | Mandatory |
| Commit messages | Meaningful and descriptive |
| Research documentation | Required for research contributions |
| Environment documentation | Required for environment contributions |
| Local validation | Required before PR |
| Pull Request | Mandatory |
| Manual review | Mandatory |
| Approval | Minimum one relevant approval |
| Merge strategy | Squash and Merge recommended |
| Branch cleanup | After successful merge |

---

## 7. Definition of Done

A contribution is considered complete only when:

- [ ] Associated Issue is created or identified.
- [ ] Working branch is created.
- [ ] Changes follow repository structure.
- [ ] Relevant documentation is updated.
- [ ] Local validation is completed.
- [ ] Pull Request is created.
- [ ] Required review and approval are completed.
- [ ] Review comments are resolved.
- [ ] Changes are merged into `main`.
- [ ] Associated Issue is closed.
- [ ] Relevant repository records are updated.

---

## 8. Final Guidelines

The `main` branch must always represent the stable and reviewed state of the Science-Environments repository.

All contributors must follow this workflow regardless of whether their contribution involves research, documentation, configuration, scientific workflows or implementation.

No contribution should be merged without appropriate documentation, validation and review.

**Every contribution must be traceable, reproducible, documented and reviewed.**
