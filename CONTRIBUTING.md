# Science Environments — Contribution and Workflow Guidelines

## 1. Purpose

This document defines the mandatory workflow for contributing to the `science-environments` repository.

All contributors must follow these guidelines, regardless of whether their contribution involves code, scientific research, environment design, configuration, evaluation, or documentation.

Our goals are to maintain:

- A consistent repository structure.
- Clear ownership and task tracking.
- Reproducible scientific workflows.
- Reviewable and traceable contributions.
- Reliable integration of environments into the Agent Scientist ecosystem.

**Core principle:** Every contribution must have a defined purpose, a documented deliverable, appropriate validation, and a review trail.

---

## 2. Scope of Contributions

The repository accepts the following types of contributions:

1. New scientific environment specifications.
2. Scientific task definitions and workflows.
3. Research notes and scientific references.
4. Environment configurations and dependency definitions.
5. Evaluation criteria and validation protocols.
6. Reproducibility documentation.
7. Executable environment implementations and supporting tests.
8. Bug reports, documentation updates, and improvements.

Code is not mandatory for every contribution. Documentation and scientific specifications must follow the same review and traceability process as code.

---

## 3. Environment Folder Example

Each environment lives under `environments/<environment-name>/`. This example shows one environment folder; research notes and references live under the matching directory in `research/`.

```text
environments/<environment-name>/
├── README.md
├── ENVIRONMENT_SPEC.md
├── config/
├── tasks/
└── tests/
```

### Directory guidelines

- `docs/`: Repository-wide documentation and architectural decisions.
- `research/`: Research notes and references, grouped by environment. Use `research-notes.md` and `references.md` within each environment directory.
- `environments/`: Individual scientific environments and their specifications.
- `config/`: Environment-specific configuration files.
- `tasks/`: Task definitions, input examples and expected output contracts.
- `tests/`: Validation tests for executable environments, where applicable.
- `results/`: Small, necessary, versioned example results or validation summaries. Do not commit large generated datasets or unrestricted experimental outputs.
- `.github/`: Contribution templates, ownership and repository workflow configuration.

Link environment specifications to the corresponding research notes and references. Keep scientific source lists in one place rather than duplicating them across research and environment directories.

The agreed base structure uses `.gitkeep` files for reserved empty directories. Remove a directory's `.gitkeep` when substantive files are added. Create additional directories only when required by the contribution.

---

## 4. Mandatory Contribution Workflow

Every planned contribution must follow these stages.

### Step 1: Create or identify a GitHub Issue

Before starting work, create a GitHub Issue or identify the existing issue associated with the task.

The issue must contain:

- Task title and objective.
- Background and rationale.
- Scope and expected deliverables.
- Acceptance criteria.
- Assigned owner.
- Reviewer or responsible team, where known.
- Dependencies and blockers, if any.

For research or design tasks, specify the document or scientific artifact that must be delivered.

Do not begin duplicate work without checking existing issues and discussions.

### Step 2: Confirm the contribution type

Identify the type of work before choosing the implementation approach.

Examples:

- Documentation-only contribution.
- Scientific research or literature review.
- Environment specification.
- Configuration or dependency change.
- Executable implementation.
- Evaluation or benchmark design.
- Bug fix.

Define acceptance criteria appropriate to the contribution type. Do not require executable tests for a purely editorial change, but do require appropriate factual, structural and reference checks.

### Step 3: Create a working branch

Never make routine contributions directly to `main`.

Use the following naming conventions:

| Contribution | Branch naming pattern |
|---|---|
| New environment | `feat/<environment-name>` |
| Documentation | `docs/<topic>` |
| Scientific research | `research/<topic>` |
| Bug fix | `fix/<issue>` |
| Evaluation design | `feat/<evaluation-topic>` |
| Maintenance | `chore/<task>` |

Examples:

- `feat/scRNAseq-environment`
- `research/synthesis-route-gym`
- `docs/environment-lifecycle`
- `feat/environment-evaluation`

Keep branches focused on one logical contribution.

### Step 4: Prepare the deliverable

Create or modify the files required by the issue.

For a new environment specification, include the following where applicable:

- `README.md`: Environment overview and usage status.
- `ENVIRONMENT_SPEC.md`: Scientific objective, methodology, inputs, outputs, constraints and evaluation criteria.
- `research/<environment-name>/research-notes.md`: Supporting scientific research, findings and open questions.
- `research/<environment-name>/references.md`: Relevant papers, datasets and software references, linked from the environment specification.
- Configuration files: Required settings and dependency definitions.
- Task definitions: Input contracts and expected output formats.
- Tests or validation reports: Evidence that the environment meets its defined requirements.

For research-only contributions, submit a structured research document with sources, findings, uncertainties and recommended next steps.

For documentation-only contributions, edit the appropriate Markdown file and explain the change in the PR.

Label specifications as proposed or in progress until their requirements and evidence support a later status. Replace drafting prompts with supported content before treating a document as a finished deliverable. A `.gitkeep` file does not provide scientific evidence, an implementation or validation.

### Step 5: Validate the contribution

Before opening a PR, verify the deliverable against its acceptance criteria.

**Documentation and research contributions:**

- Check spelling, clarity and Markdown formatting.
- Verify that referenced links and citations are relevant and accessible.
- Distinguish established facts from hypotheses and proposed methods.
- Record limitations and unresolved questions.
- Confirm that the document is stored in the correct location.

**Environment specifications:**

- Confirm that objectives, inputs, outputs and evaluation criteria are defined.
- Identify dependencies and relevant version constraints where known.
- Document assumptions, failure cases and reproducibility requirements.
- Make clear whether the environment is specified, implemented or validated.

**Executable contributions:**

- Run applicable tests and validation checks.
- Check dependency installation and configuration.
- Record relevant test results and reproduction instructions.
- Do not claim successful validation if the checks have not been performed.

Validation requirements must match the type and maturity of the contribution.

### Step 6: Commit changes

Use clear, descriptive commit messages.

Recommended format:

`<type>: <short description>`

Examples:

- `docs: add scRNA-seq environment specification`
- `research: document synthesis route evidence`
- `feat: add environment task definition`
- `test: add environment validation checks`
- `fix: correct configuration validation`

Keep commits focused. Do not include unrelated changes, secrets, credentials, private data or unapproved large files.

### Step 7: Open a Pull Request

Open a PR against `main` and link the associated GitHub Issue.

Every PR must include:

1. Summary of the change.
2. Reason for the change.
3. Contribution type.
4. Files and deliverables added or modified.
5. Validation performed and evidence obtained.
6. Known limitations or open questions.
7. Related issue reference.
8. Confirmation that applicable acceptance criteria have been met.

Use the repository's PR template.

A documentation-only PR is valid. Mark it as documentation-only when appropriate and explain how its quality and accuracy were checked.

### Step 8: Review and address feedback

The assigned reviewer must verify that:

- The contribution addresses the original issue.
- The deliverables meet the acceptance criteria.
- Scientific claims are appropriately supported.
- Documentation and file placement follow repository conventions.
- Required validation has been completed.
- No critical unresolved issues remain.

Scientific content should receive review from an appropriate scientific or domain expert when needed.

The contributor must address review comments and push updates to the same branch. Request re-review when the changes are ready.

### Step 9: Merge and close the task

A PR may be merged when:

- Required approvals are obtained.
- Applicable automated checks pass.
- Acceptance criteria are satisfied.
- Blocking review comments are resolved.

Use the repository's approved merge strategy and branch-protection rules.

After merging, ensure the linked issue is closed and the deliverable's status is updated accurately.

---

## 5. Pull Request Requirements

Every PR must answer the following questions:

1. What is changing?
2. Why is the change necessary?
3. Which issue does it address?
4. What files or artifacts are being delivered?
5. How was the contribution validated?
6. What limitations remain?
7. Who reviewed the contribution?

Do not submit PRs containing unrelated changes or work that cannot be meaningfully reviewed.

Keep PRs as small and focused as practical.

---

## 6. Workflow for Contributors Who Do Not Write Code

Code is not required for scientific research, workflow planning or environment design.

Non-code contributors must follow the same issue, branch, PR and review workflow.

### Example: Scientific environment proposal

A contributor is assigned to develop a scRNA-seq environment specification.

**Expected workflow:**

1. Create or update the GitHub Issue.
2. Create a branch such as `feat/scRNAseq-environment`.
3. Add or update `environments/scRNAseq-environment/README.md`.
4. Add or update `environments/scRNAseq-environment/ENVIRONMENT_SPEC.md`.
5. Add or update `research/scRNAseq-environment/research-notes.md` and `research/scRNAseq-environment/references.md`, and link them from the environment documents.
6. Document the objective, scientific rationale, input and output contracts, evaluation criteria, assumptions and limitations.
7. Validate the documentation and references.
8. Open a PR and link the issue.
9. Obtain the required review.
10. Merge after approval.

No Python implementation is required for this specification-only contribution.

However, the environment must not be described as executable or validated until the corresponding implementation and validation have actually been completed.

---

## 7. Environment Lifecycle and Status

Use explicit statuses to prevent confusion about implementation maturity.

| Status | Meaning |
|---|---|
| Proposed | The idea has been identified but not fully specified. |
| Specification | The scientific requirements and expected behaviour are documented. |
| In Progress | Implementation or other required work is underway. |
| Implemented | The required implementation exists. |
| Validated | The defined validation criteria have been satisfied and evidence is available. |
| Deprecated | The environment is no longer recommended for new use. |

Do not mark an environment as validated based solely on documentation review or successful execution of an unverified example.

Status changes should be reflected in the environment's README or the repository's agreed tracking mechanism.

---

## 8. GitHub Issues, Labels and Ownership

Use existing repository labels where available. Standard labels should include:

- `environment`
- `documentation`
- `research`
- `evaluation`
- `bug`
- `enhancement`
- `needs-review`
- `blocked`

Each issue must have a clear owner or responsible team.

Use CODEOWNERS or explicit reviewer assignments to route contributions to the appropriate maintainers. Scientific review and software review may require different reviewers.

If a contributor encounters a blocker, they must update the issue with the problem, its impact and the support required rather than leaving the task silently incomplete.

---

## 9. Reproducibility and Scientific Integrity

Every environment must document reproducibility requirements appropriate to its maturity.

Where applicable, record:

- Software and dependency versions.
- Model names and versions.
- Dataset sources and versions.
- Configuration parameters.
- Random seeds.
- Hardware and runtime requirements.
- Execution instructions.
- Expected outputs and evaluation metrics.
- Known limitations and sources of uncertainty.

Do not commit credentials, API keys, restricted datasets or sensitive information.

Do not fabricate experimental measurements, benchmark scores or validation results. Clearly distinguish predicted results, observed results and illustrative examples.

When exact reproducibility is not possible, document the reason and the steps needed to approximate the original conditions.

---

## 10. Definition of Done

A task is complete only when the applicable criteria below have been satisfied.

- [ ] A GitHub Issue exists and describes the task.
- [ ] The deliverable is available in the correct repository location.
- [ ] The contribution follows the relevant documentation and naming conventions.
- [ ] Acceptance criteria have been checked.
- [ ] Supporting references and evidence are included where required.
- [ ] Applicable validation has been performed.
- [ ] A PR has been opened and linked to the issue.
- [ ] Required reviewers have approved the changes.
- [ ] Applicable automated checks have passed.
- [ ] The PR has been merged.
- [ ] The issue and environment status have been updated accurately.

Not every checkbox applies to every contribution. Validation and review requirements must reflect the actual scope of the task.

---

## 11. Rules for All Contributors

1. Do not push routine changes directly to `main`.
2. Do not submit work without a defined purpose and deliverable.
3. Do not create duplicate environments without checking existing work.
4. Do not claim implementation or validation that has not occurred.
5. Do not commit secrets, restricted data or unnecessary generated artifacts.
6. Do not merge changes before required reviews and checks are complete.
7. Do not leave blockers or unresolved review feedback undocumented.
8. Keep contributions focused, evidence-based and traceable.
9. Use Markdown for specifications, research notes and documentation when appropriate.
10. Follow the same review standards regardless of whether the contribution contains code.

---

## 12. Final Principle

The `science-environments` repository must function as a reliable collection of well-defined scientific tasks and environments, not merely a collection of code and documents.

Every contribution must be traceable to a task, stored consistently, reviewed by the appropriate people and assigned an accurate maturity status.

**Issue → Branch → Deliverable → Validation → Pull Request → Review → Merge → Status Update**

All contributors are expected to follow this workflow.
