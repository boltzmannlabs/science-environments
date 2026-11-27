# Science Environments

Scientific environment specifications, research, workflows, benchmarks, and implementations for the **Agent Scientist ecosystem**.

This repository provides a consistent way to describe scientific work, configure it, execute it, evaluate it, and preserve the evidence produced. Environments may differ in scientific domain and implementation, but their documentation and traceability conventions should be predictable.

> **Core principle:** A task defines what should be done; configuration defines how it should be done; a run records one execution; results preserve what that execution produced.

## Contents

- [Repository structure](#repository-structure)
- [Directory responsibilities](#directory-responsibilities)
- [Environment documentation](#environment-documentation)
- [Task, configuration, run, and result relationship](#task-configuration-run-and-result-relationship)
- [Recommended file formats and examples](#recommended-file-formats-and-examples)
- [Worked example: Generic scientific task lifecycle](#worked-example-generic-scientific-task-lifecycle)
- [Benchmark organization](#benchmark-organization)
- [Validation and evidence](#validation-and-evidence)
- [Contribution workflow](#contribution-workflow)
- [Naming conventions](#naming-conventions)
- [Mandatory artifact filename format](#mandatory-artifact-filename-format)

## Repository structure

The following is the recommended logical structure. Include only directories that are relevant to an environment; do not add empty placeholders solely to match this diagram.

```text
science-environments/
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
│       │
│       ├── config/
│       │   ├── environment.yaml
│       │   ├── schemas/
│       │   ├── shared/
│       │   └── tasks/
│       │
│       ├── tasks/
│       │   ├── README.md
│       │   └── <task-id>/
│       │       └── task.md
│       │
│       ├── runs/
│       │   └── <task-id>/
│       │       └── <run-id>/
│       │
│       ├── results/
│       │   └── <task-id>/
│       │       └── <run-id>/
│       │
│       ├── tests/
│       ├── scripts/
│       ├── src/
│       └── benchmark/
│           ├── definitions/
│           ├── reference_data/
│           └── evaluation/
│
├── docs/
│   └── decisions/
└── .github/
    ├── PULL_REQUEST_TEMPLATE.md
    └── workflows/
```

### Important structure rules

1. `tasks/` contains task definitions, not execution outputs.
2. `config/` contains reusable defaults, schemas, and task configuration templates or versioned configuration files. It should not be used as an archive for run outputs.
3. `runs/` contains execution records, exact input snapshots or references, logs, and runtime metadata. A failed or interrupted run still belongs here.
4. `results/` contains outputs produced by a run. Each result directory must be traceable to its task and run.
5. `benchmark/` contains benchmark definitions, reference datasets or documented references, evaluation protocols, and benchmark registries. Benchmark execution outputs should also have run-level identity and provenance; do not mix benchmark definitions with unrelated task outputs.
6. Keep historical records. Reorganize them through traceable migrations; do not silently delete, overwrite, or relabel scientific evidence.
7. Use lowercase directory names and consistent identifiers. Avoid case-only differences such as `Results/` and `results/`, which behave differently across operating systems.

## Directory responsibilities

| Path | Responsibility | Typical contents |
|---|---|---|
| `research/` | Scientific background and feasibility work | Research notes, references, literature reviews |
| `environments/<name>/README.md` | Entry point for an environment | Purpose, setup, usage, links to tasks and evidence |
| `ENVIRONMENT_SPEC.md` | Environment contract | Scope, assumptions, inputs, outputs, constraints |
| `STATUS.md` | Current state | Completed, in progress, blocked, limitations |
| `MODELS_AND_TOOLS.md` | Model/tool inventory | Versions, roles, dependencies, licenses, access notes |
| `config/` | Configuration and schemas | YAML/JSON configuration, schemas, defaults |
| `tasks/` | Scientific task definitions | Objective, inputs, method, acceptance criteria |
| `runs/` | Execution history | Run metadata, input snapshot, logs, status |
| `results/` | Run outputs | Reports, metrics, structures, tables, figures, provenance |
| `tests/` | Technical and scientific checks | Unit/integration/contract tests, fixtures |
| `scripts/` | Supporting automation | Preparation, execution, conversion, validation scripts |
| `src/` | Reusable implementation | Packages and environment-specific source code |
| `benchmark/` | Evaluation specification | Benchmark protocol, reference data, scoring and registry |
| `docs/decisions/` | Long-lived decisions | Architecture Decision Records (ADRs) |

Not every environment needs source code, scripts, or a dedicated configuration file. Explain intentional omissions in the environment README or specification.

## Environment documentation

Each environment should provide the following documents where applicable.

### `README.md` — environment entry point

Include:
- Purpose and scientific domain.
- Scope and supported capabilities.
- Quick-start or navigation instructions.
- Task catalogue and task identifiers.
- Configuration and execution instructions.
- Links to benchmarks and results.
- Known limitations and status.

### `ENVIRONMENT_SPEC.md` — environment contract

Include:
- Objectives and out-of-scope behavior.
- Supported workflows and scientific assumptions.
- Input and output contracts.
- Dependencies and execution requirements.
- Constraints, safety considerations, and failure handling.
- Technical and scientific acceptance criteria.

### `STATUS.md` — current state

Use explicit statuses such as `planned`, `in_progress`, `blocked`, `technically_validated`, `scientifically_evaluated`, and `completed`. Do not use `completed` to imply experimental validation unless experiments were actually performed.

### `MODELS_AND_TOOLS.md` — model and tool inventory

For each model or tool, record its purpose, version/checkpoint, source, license or usage constraints, input/output role, and validation status where known. Do not claim a version or validation status that has not been verified.

## Task, configuration, run, and result relationship

The expected traceability chain is:

```text
Environment
   └── Task (stable task_id)
        ├── Task definition
        ├── Configuration (config_id + version/hash)
        └── Run (unique run_id)
             ├── Input snapshot or immutable input references
             ├── Execution metadata and logs
             └── Result (linked to the same task_id and run_id)
                  ├── Report
                  ├── Metrics
                  ├── Artifacts
                  └── Provenance
```

A task may have many runs. Each run must identify exactly one task and the resolved configuration used for that execution. A run may fail and therefore have no publishable scientific result. A successful run may produce multiple artifacts.

**Do not infer relationships from folder names alone.** Store explicit identifiers in metadata files and validate that referenced paths exist.

### Identifier guidance

- `task_id`: stable identifier for a scientific task, e.g. `TASK-001`. Do not reuse it for a different task.
- `config_id`: identifier for a configuration profile, e.g. `CFG-TASK-001`.
- `run_id`: unique execution identifier, e.g. `RUN-20261127-001` or a UUID.
- `result_id`: identifier for the result package, e.g. `RESULT-RUN-20261127-001`.
- `benchmark_id`: stable identifier for a benchmark definition, e.g. `BM-001`.

The human-readable task slug may change only through a documented migration. The stable ID should remain unchanged.

## Recommended file formats and examples

The examples below are illustrative templates. Replace placeholder values with verified environment-specific values. Do not copy sample model versions, hashes, measurements, or statuses as if they were real.

### 1. Task definition — `tasks/TASK-001/task.md`

```markdown
# TASK-001 — <Task title>

## Metadata
- Task ID: TASK-001
- Environment: <environment-name>
- Owner/team: <owner or team>
- Status: planned | active | blocked | retired
- Created: YYYY-MM-DD
- Updated: YYYY-MM-DD

## Objective
Describe the scientific question or outcome this task is intended to address.

## Background and rationale
Summarize relevant context and link to research notes or publications.

## Inputs
| Input | Required | Format | Description / source |
|---|---|---|---|
| input_1 | yes | FASTA | ... |
| input_2 | no | CSV | ... |

## Method / workflow
1. Describe preparation.
2. Describe execution.
3. Describe analysis and evaluation.

## Constraints and assumptions
- State scientific assumptions.
- State computational or operational constraints.
- Identify unsupported cases.

## Expected outputs
| Output | Format | Acceptance condition |
|---|---|---|
| report | Markdown | Includes method, findings, limitations |
| metrics | JSON/CSV | Uses documented metric definitions |

## Acceptance criteria
- [ ] Required inputs are validated.
- [ ] Workflow completes or records a clear failure.
- [ ] Outputs match the declared schema.
- [ ] Provenance is recorded.
- [ ] Scientific limitations are reported.

## References
- [Reference title, DOI/URL, access date]
```

### 2. Configuration — `config/tasks/TASK-001.yaml`

```yaml
config_id: CFG-TASK-001
task_id: TASK-001
config_version: 1

execution:
  mode: local
  timeout_seconds: 3600
  retries: 0

inputs:
  primary_input: data/input.fasta
  optional_input: null

model:
  name: "<model-name>"
  version: "<verified-version-or-checkpoint>"
  parameters:
    seed: 1234

outputs:
  directory: results/TASK-001
  formats:
    - json
    - csv
    - md

validation:
  validate_inputs: true
  validate_outputs: true
  require_provenance: true
```

Keep secrets out of committed configuration. Use environment variables or an approved secret manager and document required variable names without publishing their values. Store a resolved configuration snapshot or cryptographic hash with each run.

### 3. Run record — `runs/TASK-001/RUN-20261127-001/run.json`

```json
{
  "run_id": "RUN-20261127-001",
  "task_id": "TASK-001",
  "environment": "<environment-name>",
  "config_id": "CFG-TASK-001",
  "config_version": 1,
  "config_hash": "<sha256-of-resolved-config>",
  "input_manifest": "input/manifest.json",
  "code_commit": "<git-commit-sha>",
  "model": {
    "name": "<model-name>",
    "version": "<verified-version-or-checkpoint>"
  },
  "status": "running",
  "started_at": "2026-11-27T09:00:00Z",
  "completed_at": null,
  "result_path": null,
  "failure": null
}
```

On completion, update `status`, `completed_at`, `result_path`, and failure details where applicable. Suggested statuses: `queued`, `running`, `completed`, `failed`, `cancelled`, `partial`.

### 4. Input manifest — `runs/TASK-001/RUN-20261127-001/input/manifest.json`

```json
{
  "task_id": "TASK-001",
  "run_id": "RUN-20261127-001",
  "inputs": [
    {
      "logical_name": "primary_input",
      "path": "input/input.fasta",
      "sha256": "<sha256>",
      "source": "<dataset-or-user-provided-source>"
    }
  ]
}
```

Record either a preserved input snapshot or an immutable external reference with version and checksum. A mutable URL alone is not sufficient provenance.

### 5. Result provenance — `results/TASK-001/RUN-20261127-001/provenance.json`

```json
{
  "result_id": "RESULT-RUN-20261127-001",
  "task_id": "TASK-001",
  "run_id": "RUN-20261127-001",
  "config_id": "CFG-TASK-001",
  "config_hash": "<sha256-of-resolved-config>",
  "input_manifest": "../../../runs/TASK-001/RUN-20261127-001/input/manifest.json",
  "code_commit": "<git-commit-sha>",
  "execution_status": "completed",
  "created_at": "2026-11-27T10:15:00Z",
  "artifacts": [
    {
      "path": "REPORT.md",
      "type": "report",
      "sha256": "<sha256>"
    },
    {
      "path": "metrics.json",
      "type": "metrics",
      "sha256": "<sha256>"
    }
  ]
}
```

Artifact paths should be relative to the result directory. The provenance record should list the actual files produced, not merely expected files.

### 6. Result report — `results/TASK-001/RUN-20261127-001/REPORT.md`

```markdown
# Results — TASK-001 / RUN-20261127-001

## Execution summary
- Task ID:
- Run ID:
- Execution status:
- Start/end time:
- Configuration version:
- Code revision:
- Model/checkpoint:

## Inputs
List input files, source identifiers, versions, and checksums.

## Method
Describe the actual workflow performed. Distinguish planned steps from completed steps.

## Results
Present observed outputs and link to machine-readable metrics and artifacts.

## Validation
List checks performed, their outcomes, and any skipped checks with reasons.

## Scientific interpretation
Explain what the results support and what they do not establish.

## Limitations
Document missing data, unsupported conditions, uncertainty, and deviations.

## Reproducibility
Provide the run record, configuration snapshot, input manifest, and provenance links.
```

### 7. Benchmark definition — `benchmark/definitions/BM-001/benchmark.yaml`

```yaml
benchmark_id: BM-001
title: "<benchmark title>"
version: 1
task_ids:
  - TASK-001

objective: "<what this benchmark evaluates>"
dataset:
  name: "<dataset name>"
  version: "<dataset version>"
  source: "<stable source or DOI>"
  checksum: "<verified checksum>"

protocol:
  split_strategy: "<documented split strategy>"
  metrics:
    - name: "<metric>"
      direction: minimize
      definition: "<formula or reference>"

acceptance:
  criteria: "<predefined criteria>"
  limitations: "<known limitations>"
```

Keep benchmark definition and reference data separate from benchmark execution outputs. Record benchmark executions with unique run IDs and provenance just like other runs.

### 8. Research topic formats

`research/<topic>/research-notes.md` should contain the question, scope, search/methodology, findings, evidence quality, assumptions, unresolved questions, and conclusion.

`research/<topic>/references.md` should list complete citations, DOI or stable URL, publication date, access date where relevant, and a short note describing why each source is relevant.


## Worked example: Generic scientific task lifecycle

This section uses entirely fictional identifiers, filenames, tools, timestamps, and parameter
values to demonstrate the repository conventions. These examples are illustrative only. They
must not be interpreted as actual project runs, scientific findings, benchmark results, or
validated model configurations.

### 1. Example task and execution

Assume a fictional environment called `sample_environment` contains a task that runs a
hypothetical sequence-design tool. The task is assigned a stable task identifier, and one
execution receives a unique run identifier.

```text
environments/sample_environment/
├── tasks/
│   └── TASK-EXAMPLE-001/
│       └── task.md
├── config/
│   └── tasks/
│       └── TASK-EXAMPLE-001.json
├── runs/
│   └── TASK-EXAMPLE-001/
│       └── RUN-EXAMPLE-001/
│           ├── run.json
│           ├── input_manifest.json
│           └── logs/
└── results/
    └── TASK-EXAMPLE-001/
        └── RUN-EXAMPLE-001/
            ├── provenance.json
            ├── REPORT.md
            └── artifacts/
                └── ARTIFACT001_sampletool_20260115T103000Z_RUN001_model001_alpha0.5_beta1.0.fasta
```

The task folder defines the scientific objective. The configuration describes the settings.
The run folder records one execution. The result folder stores the outputs produced by that
execution. The task and run identifiers must match across the folder structure and metadata.

### 2. Task definition — `tasks/TASK-EXAMPLE-001/task.md`

```markdown
# TASK-EXAMPLE-001 — Example sequence analysis

## Metadata
- Task ID: TASK-EXAMPLE-001
- Environment: sample_environment
- Owner/team: example-team
- Status: planned
- Created: 2026-01-15
- Updated: 2026-01-15

## Objective
Describe the scientific question this task is intended to investigate.

## Inputs
| Input | Required | Format | Description |
|---|---|---|---|
| input_sequence | yes | FASTA | Fictional example input |
| constraints | no | JSON | Optional design constraints |

## Workflow
1. Validate input files.
2. Load the configured model.
3. Execute the analysis.
4. Validate generated outputs.
5. Record results and provenance.

## Expected outputs
- Generated sequence file in FASTA format.
- Machine-readable run metadata.
- Result report and provenance record.

## Acceptance criteria
- [ ] Inputs are validated.
- [ ] Execution status is recorded.
- [ ] Outputs conform to their declared formats.
- [ ] Every artifact is traceable to this task and run.
- [ ] Limitations are documented.
```

### 3. Configuration — `config/tasks/TASK-EXAMPLE-001.json`

```json
{
  "config_id": "CFG-EXAMPLE-001",
  "config_version": 1,
  "task_id": "TASK-EXAMPLE-001",
  "environment": "sample_environment",
  "tool": {
    "name": "SampleTool",
    "version": "1.0.0",
    "model_identifier": "model001"
  },
  "parameters": {
    "alpha": 0.5,
    "beta": 1.0
  },
  "inputs": {
    "primary_input": "input/example.fasta"
  },
  "outputs": {
    "format": "fasta",
    "relative_directory": "artifacts"
  }
}
```

These values are fictional. Real configuration values must come from the actual tool
documentation and the resolved configuration used for execution.

### 4. Run metadata — `runs/TASK-EXAMPLE-001/RUN-EXAMPLE-001/run.json`

```json
{
  "task_id": "TASK-EXAMPLE-001",
  "run_id": "RUN-EXAMPLE-001",
  "environment": "sample_environment",
  "config_id": "CFG-EXAMPLE-001",
  "config_version": 1,
  "config_sha256": "<sha256-of-resolved-configuration>",
  "input_manifest": "input_manifest.json",
  "code_commit": "<git-commit-sha>",
  "tool": {
    "name": "SampleTool",
    "version": "1.0.0",
    "model_identifier": "model001"
  },
  "parameters": {
    "alpha": 0.5,
    "beta": 1.0
  },
  "status": "completed",
  "started_at": "2026-01-15T10:25:00Z",
  "completed_at": "2026-01-15T10:30:00Z",
  "result_path": "results/TASK-EXAMPLE-001/RUN-EXAMPLE-001",
  "failure": null
}
```

The example status and timestamps are fictional. In a real run, status and timestamps must be
written by the execution system or taken from verified logs. Do not mark a run `completed`
merely because an output file exists.

### 5. Input manifest — `runs/TASK-EXAMPLE-001/RUN-EXAMPLE-001/input_manifest.json`

```json
{
  "task_id": "TASK-EXAMPLE-001",
  "run_id": "RUN-EXAMPLE-001",
  "inputs": [
    {
      "logical_name": "primary_input",
      "path": "inputs/example.fasta",
      "sha256": "<sha256-of-input-file>",
      "source": "fictional-example-dataset",
      "source_version": "1.0"
    }
  ]
}
```

Record a preserved input snapshot or an immutable external reference with a version and checksum.
A mutable URL alone is not sufficient provenance.

### 6. Generated artifact filename

Use this required component order for generated artifacts:

```text
<artifact_id>_<tool_name>_<timestamp_utc>_<run_reference>_<model_identifier>_<parameters>.<extension>
```

Fictional example:

```text
ARTIFACT001_sampletool_20260115T103000Z_RUN001_model001_alpha0.5_beta1.0.fasta
```

Component mapping:

| Position | Component | Fictional value |
|---:|---|---|
| 1 | Artifact ID | `ARTIFACT001` |
| 2 | Tool name | `sampletool` |
| 3 | UTC timestamp | `20260115T103000Z` |
| 4 | Run reference | `RUN001` |
| 5 | Model identifier | `model001` |
| 6 | Parameters | `alpha0.5_beta1.0` |
| 7 | Extension | `.fasta` |

Use underscores between components. Do not use spaces or Windows-invalid characters such as
`< > : " / \ | ? *`. Preserve the original extension and file contents. Parameter names,
values, and order must be consistent and must not be rounded or altered for naming convenience.

### 7. Artifact provenance — `results/TASK-EXAMPLE-001/RUN-EXAMPLE-001/provenance.json`

```json
{
  "task_id": "TASK-EXAMPLE-001",
  "run_id": "RUN-EXAMPLE-001",
  "config_id": "CFG-EXAMPLE-001",
  "code_commit": "<git-commit-sha>",
  "artifacts": [
    {
      "artifact_id": "ARTIFACT001",
      "artifact_type": "generated_sequence",
      "tool": "SampleTool",
      "tool_version": "1.0.0",
      "model_identifier": "model001",
      "created_at": "2026-01-15T10:30:00Z",
      "parameters": {
        "alpha": 0.5,
        "beta": 1.0
      },
      "original_filename": "fictional-original-tool-output.fasta",
      "stored_filename": "ARTIFACT001_sampletool_20260115T103000Z_RUN001_model001_alpha0.5_beta1.0.fasta",
      "relative_path": "artifacts/ARTIFACT001_sampletool_20260115T103000Z_RUN001_model001_alpha0.5_beta1.0.fasta",
      "format": "fasta",
      "sha256": "<sha256-of-generated-file>"
    }
  ]
}
```

If the original tool filename is needed for provenance, retain it in metadata. The on-disk
filename must still follow the repository's portable naming convention. Calculate checksums
from the actual files; never copy placeholder hashes into a real record.

### 8. Result report — `results/TASK-EXAMPLE-001/RUN-EXAMPLE-001/REPORT.md`

```markdown
# Result report — TASK-EXAMPLE-001 / RUN-EXAMPLE-001

## Execution identity
- Environment: sample_environment
- Task ID: TASK-EXAMPLE-001
- Run ID: RUN-EXAMPLE-001
- Tool: SampleTool
- Tool version: 1.0.0
- Model identifier: model001

## Configuration
- Config ID: CFG-EXAMPLE-001
- Config version: 1
- Parameters: alpha=0.5, beta=1.0

## Inputs
List the actual input files, source versions, and checksums.

## Method
Describe the workflow that was actually executed.

## Generated artifacts
List each output file, format, checksum, and validation status.

## Technical validation
Record checks performed and their actual outcomes. Mark unperformed checks as `not_run`.

## Scientific evaluation
Describe the evaluation method, evidence, observations, and limitations.
Do not claim scientific validity from successful execution alone.

## Reproducibility
Link the run record, resolved configuration, input manifest, code revision, and provenance.
```

### 9. Contributor verification checklist

- [ ] Task ID is identical in the task definition, configuration, run record, and provenance.
- [ ] Run ID is identical in the run record, result path, and provenance.
- [ ] Tool and model identifiers match the actual execution configuration.
- [ ] Timestamp and parameters come from verified execution metadata.
- [ ] Artifact filename follows the required component order.
- [ ] No spaces or prohibited characters occur in repository paths.
- [ ] Original tool filename is retained in metadata when needed.
- [ ] File contents and extension are preserved.
- [ ] Checksums are calculated from the actual files.
- [ ] Technical validation and scientific evaluation are reported separately.

**Important:** All names, IDs, dates, tools, versions, parameters, paths, and values in this
worked example are fictional. Replace them with verified values when creating real task,
configuration, run, and result records. Never copy sample outputs or sample validation claims
into a real scientific result.

---

## Benchmark organization

Use `benchmark/` for:
- Benchmark definitions and protocols.
- Reference datasets or immutable dataset references.
- Metric definitions and evaluation scripts.
- Benchmark registries and comparison methodology.

Use `runs/` and `results/` for actual benchmark executions and their outputs, or maintain a clearly documented benchmark-specific execution layout that preserves the same `task_id`/`run_id`/provenance requirements.

Do not treat a benchmark report, a model component test, a synthetic fixture, a retrospective literature comparison, and an experimental validation as interchangeable evidence. Label the evidence type and scope clearly.

## Validation and evidence

### Technical validation

Examples:
- Configuration/schema validation.
- Dependency and environment checks.
- Input/output contract validation.
- Workflow smoke and integration tests.
- Artifact existence and checksum verification.
- Reproducibility checks.

### Scientific validation

Examples:
- Appropriate reference dataset and baseline selection.
- Correct metric definitions and split strategy.
- Comparison with published or independently generated results.
- Uncertainty and limitations reporting.
- Experimental validation, where applicable.

Passing technical tests does not establish scientific validity. A computational benchmark does not establish wet-lab performance unless experimental work was actually conducted.

## Contribution workflow

All contributions must follow [`CONTRIBUTING.md`](CONTRIBUTING.md). Significant work should be associated with a GitHub Issue, developed on a branch, validated, and submitted through a Pull Request.

## Naming conventions

| Item | Convention | Example |
|---|---|---|
| Environment directory | lowercase kebab-case or established legacy name | `enzyme-design/` |
| Task ID | stable, unique ID | `TASK-001` |
| Task directory | ID plus descriptive slug | `TASK-001-retroaldolase-design/` |
| Config | task-linked and versioned | `TASK-001.yaml` |
| Run ID | unique, sortable identifier | `RUN-20261127-001` |
| Result directory | same task and run identity | `results/TASK-001/RUN-20261127-001/` |
| Benchmark ID | stable identifier | `BM-001` |

For existing environments, preserve established identifiers during migration unless a mapping is recorded. Do not rename historical records without retaining their old path/ID in a migration map.

### Mandatory artifact filename format

All contributors and automated workflows must use the same component order for generated
artifact filenames. This is especially important for outputs produced by scientific tools,
which may contain spaces, pipes, colons, or other characters that cannot be checked out on
all supported operating systems.

**Required format**

```text
<artifact_id>_<tool_name>_<timestamp_utc>_<run_reference>_<model_identifier>_<parameters>.<extension>
```

**Component order — do not rearrange**

1. `artifact_id`: stable artifact identifier, preferably the source/tool-generated ID when available.
2. `tool_name`: normalized lowercase tool name, e.g. `antibmpnn`.
3. `timestamp_utc`: execution timestamp in UTC using `YYYYMMDDTHHMMSSZ`.
4. `run_reference`: short run ID or stable run reference; it must map to the full `run_id` in run metadata.
5. `model_identifier`: normalized model/checkpoint identifier, e.g. `model020`.
6. `parameters`: relevant output-generating parameters, in a documented and consistent order.
7. Extension: preserve the original extension and file type.

**Example**

Raw tool-generated name (not suitable for committing as-is):

```text
6afb145e239a6b9f38bf435f_AntiBMPNN - 20261116-143406Z - 2465ae|antibmpnn_020|N-0.0|T-0.1.fa
```

Normalized repository filename:

```text
6afb145e239a6b9f38bf435f_antibmpnn_20261116T143406Z_2465ae_model020_n0.0_t0.1.fa
```

The example illustrates normalization only. Contributors must not invent missing IDs, timestamps,
model identifiers, or parameter values. Use verified values from the execution record.

**Character and formatting rules**

- Use lowercase for normalized tool names and descriptive filename components.
- Use underscores (`_`) between components; use hyphens only inside a component when needed.
- Do not use spaces.
- Never use Windows-invalid filename characters: `< > : " / \ | ? *`.
- Avoid trailing spaces or trailing periods.
- Keep parameter names explicit and preserve their documented order.
- Use a consistent decimal representation; do not silently round or change parameter values.
- Preserve the original file extension and file contents.
- Do not use a filename as the only source of provenance; record identifiers in metadata too.
- Keep filenames reasonably short while retaining the required identity fields.

**Where the original tool filename is needed**

If a tool's original filename is important for provenance, record it in the run manifest or artifact
metadata, for example:

```json
{
  "artifact_id": "6afb145e239a6b9f38bf435f",
  "stored_filename": "6afb145e_antibmpnn_20261116T143406Z_2465ae_model020_n0.0_t0.1.fa",
  "original_filename": "6afb145e239a6b9f38bf435f_AntiBMPNN - 20261116-143406Z - 2465ae|antibmpnn_020|N-0.0|T-0.1.fa",
  "task_id": "TASK-014",
  "run_id": "RUN-20261116-001",
  "tool": "AntiBMPNN",
  "model_identifier": "antibmpnn_020",
  "parameters": {
    "N": 0.0,
    "T": 0.1
  }
}
```

The values above are illustrative. The `original_filename` is metadata only; it must not be used as
the on-disk filename if it contains characters unsupported by a contributor's operating system.

**Directory and filename relationship**

```text
results/
└── TASK-014/
    └── RUN-20261116-001/
        ├── run_metadata.json
        ├── provenance.json
        └── artifacts/
            └── 6afb145e_antibmpnn_20261116T143406Z_2465ae_model020_n0.0_t0.1.fa
```

The directory identifiers and metadata must agree. A filename does not replace the task/run
relationship: every artifact must be traceable to its task and execution.

## License

Refer to the repository's [`LICENSE`](LICENSE) file for licensing information.
