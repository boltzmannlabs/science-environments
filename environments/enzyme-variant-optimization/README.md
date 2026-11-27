# Enzyme Variant Optimization

Scientific assignments and recorded workflows for six enzyme case studies. Agent-alone and specialist-assisted executions retain their own models, tools, sequences, measurements and reviews. A completed computational workflow can find no qualifying candidate.

## Structure

```text
enzyme-variant-optimization/
├── ENVIRONMENT_SPEC.md
├── STATUS.md
├── MODELS_AND_TOOLS.md
├── tasks/<task-id>/task.md
├── config/
│   ├── environment.yaml
│   ├── schemas/
│   ├── shared/
│   └── tasks/<task-id>/<model-and-approach>.json
├── runs/<task-id>/run_<number>_<session-id>/
├── results/<task-id>/run_<same-number>_<same-session-id>/
├── benchmark/
│   ├── definitions/
│   ├── reference_data/
│   └── evaluation/
├── scripts/
└── src/
```

| Location | Contents |
|---|---|
| [Tasks](tasks/README.md) | Stable assignments, scientific constraints and acceptance criteria. |
| [Configuration](config/README.md) | Recovered or frozen task settings, with unknown historical fields explicit. |
| [Runs](runs/README.md) | Each independent execution, native continuation identity, inputs, usage and calls. |
| [Results](results/README.md) | Per-run workflow, reports, sequences, predictions and specialist reviews. |
| [Benchmarks](benchmark/README.md) | Published references and explicitly identified historical comparisons. |
| [Source](src/README.md) | Retained implementation and environment coordinator skill. |
| [Scripts](scripts/README.md) | Native launch preparation, evaluation and offline report tools. |

## Recorded workflows

- [RML lipase — stability](results/task_001_rml_stability/README.md)
- [Limonene epoxide hydrolase — stability](results/task_002_leh_stability/README.md)
- [Bacillus licheniformis alpha-amylase — high-temperature performance](results/task_003_bla_high_temperature/README.md)
- [AtHOL1 methyltransferase — ethyl iodide substrate expansion](results/task_004_athol1_substrate/README.md)
- [Sun LEH study — Pythia mutation scoring](results/task_005_sun_leh_pythia/README.md)
- [Zhang study — cellulase and beta-glucanase scoring](results/task_006_zhang_hydrolases/README.md)

The registry includes 19 scientific workflow records: ten historical campaigns, five later Codex/DiscoveryRSI executions, and four HY4 assisted executions. Preparation-only starts and software fixtures are excluded. Native continuation sessions stay within their original logical run. All six tasks have specialist-assisted evidence.

## Execution

Read the [environment specification](ENVIRONMENT_SPEC.md), select a task, and supply explicit frozen settings to [launch_task.py](scripts/launch_task.py). Historical configuration summaries are incomplete where stated; they are not drop-in replay profiles. Use native SCI resume for an existing run and reconcile accepted or unknown jobs before any retry. MLDE remains excluded. No scientific job was replayed by this migration.

## Provenance and migration

[The path mapping](migration_map.json) preserves links from historical names to current locations. Each result package links its run record and configuration. Large/private artifacts and complete native transcripts remain in retained private archives; the repository keeps concise execution metadata rather than per-call activity logs. Missing original settings or artifact naming components are reported, not invented. No empty tests directory is added; environment-owned validation is available through `python scripts/validate_run_records.py`.

Benchmark protocols, reference notes and calculations are separated under `benchmark/definitions/`, `benchmark/reference_data/` and `benchmark/evaluation/`. Comparisons retain their historical agent-alone scope; they do not silently combine later model runs.

Run directories use `run_001_<session-id>`, numbered separately within each task in existing start order. The same name is used in runs, results and any run-specific source folder. Metadata retains the original native run/session identity. Future executions append without renumbering these records.

## Artifact filenames

Generated scientific tables, sequences, structures, arrays and figures use this component order:

```text
<artifact_id>_<tool_name>_<timestamp_utc>_<run_reference>_<model_identifier>_<parameters>.<original-extension>
```

Each result or benchmark `provenance.json` records the original exported filename/path, stored name, byte checksum, field sources and missing fields. Native session/job IDs and scientific contents are unchanged. Standard documentation, configuration, run records, provenance and evaluator-control JSON retain their documented conventional names.

## Explicit fallback for historical exports

When source metadata is absent, the filename uses the literal `unreported` in that position and metadata records the absence. This is not a model name, timestamp or parameter value. Never substitute the LLM name for a scientific predictor or infer artifact time from filesystem modification time. When a native job ID is absent, an export identity is constructed from the verified content SHA256 plus a checksum of its prior relative path. This identifies the exported file and is explicitly not an upstream job ID.

Where a source payload is recorded, the parameter component is `metadata`; the artifact entry links to that exact existing job-ledger entry rather than embedding large molecular inputs in a filename or truncating parameter values. Otherwise parameters are `unreported`. A job match is accepted only when a document ID in the filename or an unambiguous recorded output filename establishes the link.

This fallback is documented for the owner-requested historical normalization and must be included in maintainer review. It does not fill missing scientific provenance. Newly executed tools should retain their actual artifact identity, model, timestamp and parameters. Old file paths resolve through provenance mappings; altered scientific outputs require updated artifact records rather than reusing a stale checksum identity.
