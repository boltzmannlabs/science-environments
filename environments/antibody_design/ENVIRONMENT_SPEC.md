# Antibody Design Environment Specification

**Environment ID:** `antibody_design`

## Purpose and organization

The environment organizes computational antibody discovery, design, optimization and evaluation around explicit scientific tasks and traceable results. Task definitions describe the scientific objective; benchmark documents provide reference context; source and result directories retain the methods, inputs and calculated outputs for each recorded run.

The development scope covers monoclonal, bispecific and multispecific antibodies, including de novo design and optimization of existing antibodies. Task definitions declare the molecular format, binding specificities and evaluation requirements.

The current task family is `monoclonal_antibody_design`. Its collection covers reference-guided refinement, framework- and epitope-conditioned design, CDR reconstruction, sequence–structure co-design, property-focused design and supplied-panel assessment. The [task catalog](tasks/monoclonal_antibody_design/README.md) links each definition to its benchmark reference.

## Directory contract

| Path | Role |
| --- | --- |
| `tasks/<family>/<task_id>.md` | Scientific task definition. |
| `benchmark/<family>/<task_id>/reference.md` | Published reference methods, metric definitions and benchmark context. |
| `benchmark/<family>/<task_id>/comparison.md` | Calculated results grouped by run, with interpretation and embedded figures. |
| `benchmark/<family>/<task_id>/figures/` | PNG images used by the comparison document. |
| `configs/<task_id>/<run_id>.json` | Compact Agent-Scientist settings. |
| `src/<task_id>/<run_id>/` | Methods, metadata, implementation, inputs and execution records. |
| `results/<task_id>/<run_id>/` | Scientific run configuration, reports, tables and generated artifacts. |
| `results/<task_id> — Results.md` | Standalone task result summary retained in the upstream Markdown format. |
| `scripts/` | Shared utility directory. |
| `skills/` | Reusable agent-instruction directory. |
| `tests/` | Environment validation-resource directory. |

Reference documents accompany the task definitions. Comparison documents and their figure directories accompany recorded calculations. Source, result and agent-setting files are organized for the completed run packages included in this collection.

## Identifiers and file relationships

Use the same descriptive `<task_id>` in the task filename, benchmark folder, configuration folder, source folder and result folder. A `<run_id>` combines its ordinal with a descriptive method name and stays consistent across the three per-run locations:

```text
configs/<task_id>/<run_id>.json
src/<task_id>/<run_id>/
results/<task_id>/<run_id>/
```

Within run records, `task_id` and `run_id` match those paths. `workflow_id` identifies the recorded method, and `lineage` describes relationships between related runs. Candidate identifiers connect candidate tables, sequence records, evaluated models, metrics and shortlists.

## Task definitions and benchmark documents

A task definition establishes the target and construct, antibody representation, supplied reference material, editable and protected regions, scientific objective and expected outputs. It defines the evaluation endpoints and any input-isolation or comparison rules relevant to the task.

Each matching benchmark directory uses the same task ID. `reference.md` describes the reference source, evaluation context, metric definitions, units and reported values. `comparison.md` presents calculated results with their candidate identities, comparator, sample scope and interpretation. Related runs can appear in separate tables within the same comparison document.

Figures are stored as PNG files under `figures/`, embedded in `comparison.md` and explained by captions. Captions identify what is plotted and how it relates to the reported measurements. Predicted confidence, predicted interaction energy, sequence recovery and structural measurements retain their distinct endpoint definitions.

## Source package

```text
src/<task_id>/<run_id>/
├── workflow.md
├── run.yaml
├── code/
├── inputs/
│   ├── saved_artifacts.csv
│   └── execution_records/
│       ├── full_config.json
│       ├── tool_details.json
│       ├── run_files.csv
│       └── observable_events.jsonl
└── logs/
    ├── agent_scientist_log.md
    └── execution_summary.md
```

`workflow.md` explains the method, input preparation, constraints, stages and selection criteria. `run.yaml` records identity, state, lineage, configuration paths and artifact-manifest metadata. `code/` contains run-specific implementation and analysis files. `inputs/` holds original and prepared inputs, mappings, controls, saved requests and supporting records.

`inputs/execution_records/` retains detailed tool records and the original configuration snapshot. Additional run-specific evidence can be stored alongside these files. `inputs/saved_artifacts.csv` inventories the package, and `run_files.csv` inventories the scientific input, code and result files; entries include paths, file sizes and SHA-256 hashes.

Each `logs/` directory contains exactly two files. `agent_scientist_log.md` records observable activity in chronological order. `execution_summary.md` summarizes preparation, tools, outputs, counts and decisions. Supporting machine-readable records remain under `inputs/execution_records/`.

## Configuration records

| Record | Contents |
| --- | --- |
| `configs/<task_id>/<run_id>.json` | Five Agent-Scientist keys: `use_subagent`, `llm_model`, `llm_version`, `tokens_used` and `time_budget`. Token fields are `input_output` and `cache_reads`; the time field is `minutes`. A leading `~` marks an approximate quantity. |
| `results/<task_id>/<run_id>/run.json` | Scientific identity, preparation, ordered stages, tool sources, supplied inputs, parameter values, recorded outputs, outcome and artifact links. |
| `src/<task_id>/<run_id>/run.yaml` | Source metadata and links to the two current configuration records and the artifact manifest. |
| `src/<task_id>/<run_id>/inputs/execution_records/full_config.json` | Preserved original configuration snapshot. |
| `src/<task_id>/<run_id>/inputs/execution_records/tool_details.json` | Detailed tool records supporting the compact scientific configuration. |

In `run.json`, `paths.src` and `paths.results` declare environment-relative folders. References beginning with `@src/` or `@results/` resolve within those folders. Shared settings appear once; `by_record` holds differences between tool records. A `value_ref` such as `C01#/parameters/key` identifies a value under `records.C01` in `tool_details.json`. Detailed records preserve long payloads while the current configuration remains compact.

## Results package

Results are represented as structured per-run packages and standalone task summary documents. The existing summaries for tasks 006 and 007 retain their upstream Markdown filenames and contents. The following table describes the files within a per-run package.

| File or directory | Contents |
| --- | --- |
| `run.json` | Compact scientific configuration and artifact links. |
| `report.md` | Methods performed, numerical findings, candidate-selection criteria and interpretation. |
| `candidates.csv` | Candidate identities and recorded candidate attributes. |
| `shortlist.csv` | Selected entries and the recorded selection information. |
| `sequences.fasta` | Saved candidate sequences identified by stable record names. |
| `metrics.csv` | Calculated measurements for candidates, models or run-level summaries. |
| `benchmark_comparison.csv` | Per-run reference comparisons and endpoint context. |
| `structures/` | Saved evaluated or generated structural models. |
| `raw/` | Native scientific outputs, including prediction archives, generated libraries, confidence arrays and numerical analyses. |

The artifact set follows the outputs of each calculation. Additional files retain descriptive names, and the report links the tables and native products used in its findings. Source methods and preparation details are documented in the corresponding source package.

## Documentation and navigation

The [main README](README.md) introduces the collection and top-level structure. The [task guide](tasks/README.md), [source guide](src/readme.md), [results guide](results/README.md) and [benchmark guide](benchmark/README.md) explain their respective file roles. Relative links connect task definitions, benchmark references, source methods and result reports so that the collection can be read from its own directory tree.
