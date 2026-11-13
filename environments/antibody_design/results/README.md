# Antibody Design Results

This directory stores scientific outputs from antibody design and evaluation. Results are grouped by task and execution run so that sequences, structures, measurements and benchmark comparisons remain attributable to the work that produced them.

## Directory Structure

```text
results/
├── README.md
└── <task_id>/
    ├── workflow_comparison.csv
    ├── <run_id_A>/
    │   ├── report.md
    │   ├── candidates.csv
    │   ├── shortlist.csv
    │   ├── designed_sequences.fasta
    │   ├── metrics.json
    │   ├── benchmark_comparison.csv
    │   ├── benchmark_report.md
    │   ├── structures/
    │   └── evidence/
    │       ├── raw/
    │       ├── reference/
    │       ├── mappings/
    │       └── validation.json
    └── <run_id_B>/
```

Each run follows the same applicable structure. Include artifacts supported by the work performed. Assessment runs use `predictions.csv` and retain the evaluated panel sequences, commonly in `sequences.fasta`. Evaluating existing candidates does not imply new sequence generation or a new shortlist.

## File Contents

| File or directory | Purpose |
| --- | --- |
| `<task_id>/` | Groups executions associated with the exact task identifier. |
| `workflow_comparison.csv` | Compares retained runs or workflow subsets, with evaluation scope, coverage and methodological differences. |
| `<run_id>/` | Contains scientific outputs from one identified execution, linked to its source record. |
| `report.md` | Presents findings, evaluation coverage, candidate comparisons, conclusions and limitations, with supporting evidence links. |
| `candidates.csv` | Records all generated candidates, including exclusions and unevaluated candidates, with IDs, available metrics, selection status and artifact paths. Identifies controls explicitly. |
| `shortlist.csv` | Records selected candidates, rationale, metrics and artifact paths. Distinguishes scientific ranking from archived selection order. |
| `designed_sequences.fasta` | Contains complete sequences for the declared export panel, using stable candidate and chain IDs. The full generated library remains in raw evidence when the export is a subset. |
| `predictions.csv` | Records assessment-panel predictions, endpoint definitions, units, evaluation status and evidence. |
| `metrics.json` | Stores measurements with definitions, units, method, candidate/model scope, aggregation and evidence references. |
| `benchmark_comparison.csv` | Pairs measurements with corresponding benchmark references, compatible differences, comparison outcomes and unresolved metrics. |
| `benchmark_report.md` | Documents benchmark methodology, executed evaluators, findings and limitations affecting reproducibility or interpretation. |
| `structures/` | Stores evaluated PDB/mmCIF models linked to candidate, chain and model identities. Distinguishes predictions from reference-derived reconstructions. |
| `evidence/raw/` | Preserves original scientific outputs: sequence libraries, prediction tables, confidence data and detailed numerical analyses. |
| `evidence/reference/` | Stores evaluated reference/control sequences and structures with source identities. |
| `evidence/mappings/` | Records candidate, chain, domain and residue mappings needed to interpret outputs. |
| `evidence/validation.json` | Records run-level packaging checks, checked scope, counts and issues. |

## Run Organization and Traceability

Independent workflow executions, repeats and retries use distinct run IDs. Follow-up evaluations retain their relationship to the originating run. Reused artifacts identify their original execution. Historical workflow bundles describe their component subsets without implying separate executions.

Use consistent candidate IDs across tables, FASTA records, structures and metrics. State whether inventories include controls and whether exported sequences cover all candidates or a subset. Shortlisted candidates must occur in the inventory and retain supporting evidence.

Plans, implementation, execution inputs, configurations, provenance and logs belong in the corresponding source package under `src/<task_id>/`. Each scientific report links to `src/<task_id>/runs/<run_id>/execution.md`. Package-wide integrity reports are stored under [`src/shared/validation/`](../src/shared/validation/).

## Reporting Requirements

Compare measurements with the corresponding benchmark under compatible target, construct, dataset, metric definition, structural scope and evaluation conditions. Keep single-case observations distinct from dataset aggregates, and predictions distinct from experimental measurements.

Report absent predictions as `not_predicted`, absent calculations as `not_computed` and incompatible comparisons as `not_comparable`, with reasons. Unsupported numeric values remain empty in CSV or `null` in JSON. Preserve partial and failed outcomes accurately; file presence and packaging validation do not establish scientific completion.

See the [environment specification](../ENVIRONMENT_SPEC.md) for the shared execution and artifact contract.
