# Execution summary — run_003_prodigy_ipsae_evaluation

Task: `task_003_pd1_framework_guided_cdr_design`. Saved run status: **completed**.

Record organization updated 2026-11-16. This is a retrospective presentation of saved execution evidence.

[Compact config](../../../../results/task_003_pd1_framework_guided_cdr_design/run_003_prodigy_ipsae_evaluation/run.json) · [Workflow](../workflow.md) · [Activity log](agent_scientist_log.md) · [Exact original config](../inputs/execution_records/full_config.json) · [Tool details](../inputs/execution_records/tool_details.json) · [File inventory and SHA-256](../inputs/execution_records/run_files.csv)

## Preparation and inputs

Objective: Quantify interface quality of run_002_agcdr_antibmpnn's 6 Boltz2 models (5 candidates + H965 control) with Prodigy (predicted binding affinity, KD) and ipSAE (interface PAE score) under Boltzmann tooling

Original input provenance, chain/mask contracts and readiness records are retained below. Current file locations, sizes and full SHA-256 values are in `../inputs/execution_records/run_files.csv`.

```json
[
  {
    "input": "12 Boltz2 model PDBs (6 jobs x 2 pairs)",
    "source": "run_002 Boltz2 outputs",
    "description": "per-model platform uploads (see tool_calls)",
    "path": "src/task_003_pd1_framework_guided_cdr_design/run_003_prodigy_ipsae_evaluation/inputs/evaluated_models"
  },
  {
    "input": "boltz2_models_conf.zip (models + pae/plddt npz + confidence json)",
    "source": "packaged from run_002 outputs",
    "sha256": "29a7e779d286d0635fe4efa05fbb56212d0c8f936cbfc157064900744a47f767"
  }
]
```

## Recorded outcome

```json
{
  "last_update": "2026-11-15T04:05:00Z",
  "status": "completed",
  "detail": "12 Prodigy per-model jobs + 1 ipsae-protein job all terminal-completed and downloaded. metrics.csv (24 rows), benchmark_comparison.csv (22 rows), raw/ (13 native outputs), report.md written; run_002 metrics.csv extended with the same 24 prediction rows.",
  "key_results": "ipSAE leader PD1T3-019 (VH 0.899 / VL 0.816, both above H965 control VH 0.785); strongest Prodigy predictions PD1T3-038 (VH -12.6 / VL -13.7 vs H965 -13.1/-9.7); raw values recorded without unit interpretation."
}
```

## Workflow steps and tools

Settings shown below are recorded values. Exact submitted arguments, payloads, resources, responses, validation and fallback details remain in `../inputs/execution_records/tool_details.json`. Historical output names are retained as evidence; use `run_files.csv` for current saved locations.

## S1_prodigy_per_model: Prodigy binding-affinity prediction on each of the 12 PD1:VH / PD1:VL models

State: **completed**. Dependencies: `["run_002_agcdr_antibmpnn S4"]`.

Acceptance/checks: 12 terminal jobs; KD/logKA parsed per model

### C01: Prodigy (Binding Affinity)

Purpose: Interface affinity prediction per model

Source: **boltzmann**; recorded state: **completed**.

Exact record: [tool_details.json](../inputs/execution_records/tool_details.json) → `/records/C01`. Original call ID: `run_003_prodigy_ipsae_evaluation-S1-01..12`.

Identifier/version: `12 boltzmann jobs: 6af886a89de6b44b075d8685 (cand2 VH), 6af886c89850a93adf67d73b (H965 VH), 6af886d2239a6b9f38bec324 (H965 VL), 6af886df9850a93adf67d773 (cand1 VH), 6af886ea9de6b44b075d86f1 (cand1 VL), 6af886f4239a6b9f38bec38d (cand2 VL), 6af886ff9de6b44b075d872a (cand3 VH), 6af887099de6b44b075d8750 (cand3 VL), 6af88713239a6b9f38bec3dd (cand4 VH), 6af8871d239a6b9f38bec3fb (cand4 VL), 6af887289de6b44b075d8791 (cand5 VH), 6af887329850a93adf67d827 …`.

**Inputs**

```json
null
```

**Parameters recorded for this call**

| Setting | Value / exact saved value | Recorded explanation |
| --- | --- | --- |
| `chain_list` | `["A", "B"]` | interacting chains A (PD-1) and B (VH or VL) |
| `input` | `one PDB per job (12 jobs)` | Field meaning: Tool-specific input object or location, retained exactly in the request.  |

**Execution and identifiers**

```json
{
  "jobs": 12,
  "uploaded_receipts": "all checked-level validation"
}
```

**Failures, retries and fallback**

```json
{
  "prior_attempt": "ZIP uploads (boltz2_models.zip, prodigy_set{1,2}.zip)",
  "observed_error": "Structure inventory exceeds 256 KiB receipt budget -> submit-time 'validation rules changed' rejection; single-PDB submit without chain_list hit connector serialization bug (chain_list:'' -> backend 422)",
  "recovery": "per-model uploads with experiment_data {chain_list:[A,B]} declared at upload time",
  "reason_for_switch": "only route that passed receipt validation",
  "protocol_differences": "12 jobs instead of 1-2 ZIP jobs; identical science"
}
```

Original submission records: `C01.R01`, `C01.R02`, `C01.R03`, `C01.R04`, `C01.R05`, `C01.R06`, `C01.R07`, `C01.R08`, `C01.R09`, `C01.R10`, `C01.R11`, `C01.R12`. These are evidence for this call, not additional completed jobs.

### C01.R01: Prodigy

Purpose: See the stage purpose.

Source: **boltzmann**; recorded state: **Success**.

Exact record: [tool_details.json](../inputs/execution_records/tool_details.json) → `/records/C01.R01`. Original call ID: `call_-7077296210414922696:subcall:0`.

Identifier/version: `Prodigy`.

**Inputs**

```json
{
  "saved_request": "src/task_003_pd1_framework_guided_cdr_design/run_003_prodigy_ipsae_evaluation/inputs/submitted_requests/message_18223_subcall_0.json",
  "sha256": "5add1fda56fa1ada0240630fae0d5bd6e1fcfe6ee1270c637bfaca397b542900"
}
```

**Parameters recorded for this call**

| Setting | Value / exact saved value | Recorded explanation |
| --- | --- | --- |
| `chain_list` | `["A", "B"]` | Field meaning: Chain grouping supplied to the interface/affinity tool.  |
| `input_path` | `users/680f678c1b1d883c92aa706c/1794672290927/1_model_0.pdb` | Field meaning: Tool-specific input field; it may contain a file location or sequence payload.  |

**Execution and identifiers**

```json
{
  "session_id": "20261114_110401_625a94",
  "message_id": 18223,
  "tool_call_id": "call_-7077296210414922696",
  "subcall_index": 0,
  "timestamp_utc": "2026-11-14T16:04:56.213784+00:00",
  "doc_id": "6af886a89de6b44b075d8685",
  "evidence_type": "original_observable_request_and_responses"
}
```

**Returned outputs / historical output names**

```json
null
```

**Validation and checks**

```json
{
  "request_matches_export": true,
  "note": "Saved arguments match exported historical tool-call arguments; this does not revalidate the scientific inputs or confirm an unresolved server job."
}
```

### C01.R02: Prodigy

Purpose: See the stage purpose.

Source: **boltzmann**; recorded state: **Success**.

Exact record: [tool_details.json](../inputs/execution_records/tool_details.json) → `/records/C01.R02`. Original call ID: `call_-7077293495995594361:subcall:0`.

Identifier/version: `Prodigy`.

**Inputs**

```json
{
  "saved_request": "src/task_003_pd1_framework_guided_cdr_design/run_003_prodigy_ipsae_evaluation/inputs/submitted_requests/message_18231_subcall_0.json",
  "sha256": "1d3f468a11b79d0bfacad64bbf99a280a45dccf98b718188ce92486c18cda086"
}
```

**Parameters recorded for this call**

| Setting | Value / exact saved value | Recorded explanation |
| --- | --- | --- |
| `chain_list` | `["A", "B"]` | Field meaning: Chain grouping supplied to the interface/affinity tool.  |
| `input_path` | `users/680f678c1b1d883c92aa706c/1794672323898/1_model_0.pdb` | Field meaning: Tool-specific input field; it may contain a file location or sequence payload.  |

**Execution and identifiers**

```json
{
  "session_id": "20261114_110401_625a94",
  "message_id": 18231,
  "tool_call_id": "call_-7077293495995594361",
  "subcall_index": 0,
  "timestamp_utc": "2026-11-14T16:05:28.041638+00:00",
  "doc_id": "6af886c89850a93adf67d73b",
  "evidence_type": "original_observable_request_and_responses"
}
```

**Returned outputs / historical output names**

```json
null
```

**Validation and checks**

```json
{
  "request_matches_export": true,
  "note": "Saved arguments match exported historical tool-call arguments; this does not revalidate the scientific inputs or confirm an unresolved server job."
}
```

### C01.R03: Prodigy

Purpose: See the stage purpose.

Source: **boltzmann**; recorded state: **Success**.

Exact record: [tool_details.json](../inputs/execution_records/tool_details.json) → `/records/C01.R03`. Original call ID: `call_-7077291296972339165:subcall:0`.

Identifier/version: `Prodigy`.

**Inputs**

```json
{
  "saved_request": "src/task_003_pd1_framework_guided_cdr_design/run_003_prodigy_ipsae_evaluation/inputs/submitted_requests/message_18235_subcall_0.json",
  "sha256": "8360b990df313a317dbb281ff7ad19a98fb67bd44c33655c083f3ec3e798a543"
}
```

**Parameters recorded for this call**

| Setting | Value / exact saved value | Recorded explanation |
| --- | --- | --- |
| `chain_list` | `["A", "B"]` | Field meaning: Chain grouping supplied to the interface/affinity tool.  |
| `input_path` | `users/680f678c1b1d883c92aa706c/1794672333404/2_model_0.pdb` | Field meaning: Tool-specific input field; it may contain a file location or sequence payload.  |

**Execution and identifiers**

```json
{
  "session_id": "20261114_110401_625a94",
  "message_id": 18235,
  "tool_call_id": "call_-7077291296972339165",
  "subcall_index": 0,
  "timestamp_utc": "2026-11-14T16:05:38.397878+00:00",
  "doc_id": "6af886d2239a6b9f38bec324",
  "evidence_type": "original_observable_request_and_responses"
}
```

**Returned outputs / historical output names**

```json
null
```

**Validation and checks**

```json
{
  "request_matches_export": true,
  "note": "Saved arguments match exported historical tool-call arguments; this does not revalidate the scientific inputs or confirm an unresolved server job."
}
```

### C01.R04: Prodigy

Purpose: See the stage purpose.

Source: **boltzmann**; recorded state: **Success**.

Exact record: [tool_details.json](../inputs/execution_records/tool_details.json) → `/records/C01.R04`. Original call ID: `call_-7077291846728150781:subcall:0`.

Identifier/version: `Prodigy`.

**Inputs**

```json
{
  "saved_request": "src/task_003_pd1_framework_guided_cdr_design/run_003_prodigy_ipsae_evaluation/inputs/submitted_requests/message_18243_subcall_0.json",
  "sha256": "87668b8d3a09d65cef92555ae6e85fa1fbd4530e288ddb22c9130e78a814113e"
}
```

**Parameters recorded for this call**

| Setting | Value / exact saved value | Recorded explanation |
| --- | --- | --- |
| `chain_list` | `["A", "B"]` | Field meaning: Chain grouping supplied to the interface/affinity tool.  |
| `input_path` | `users/680f678c1b1d883c92aa706c/1794672346596/1_model_0.pdb` | Field meaning: Tool-specific input field; it may contain a file location or sequence payload.  |

**Execution and identifiers**

```json
{
  "session_id": "20261114_110401_625a94",
  "message_id": 18243,
  "tool_call_id": "call_-7077291846728150781",
  "subcall_index": 0,
  "timestamp_utc": "2026-11-14T16:05:51.644853+00:00",
  "doc_id": "6af886df9850a93adf67d773",
  "evidence_type": "original_observable_request_and_responses"
}
```

**Returned outputs / historical output names**

```json
null
```

**Validation and checks**

```json
{
  "request_matches_export": true,
  "note": "Saved arguments match exported historical tool-call arguments; this does not revalidate the scientific inputs or confirm an unresolved server job."
}
```

### C01.R05: Prodigy

Purpose: See the stage purpose.

Source: **boltzmann**; recorded state: **Success**.

Exact record: [tool_details.json](../inputs/execution_records/tool_details.json) → `/records/C01.R05`. Original call ID: `call_-7077291400051548703:subcall:0`.

Identifier/version: `Prodigy`.

**Inputs**

```json
{
  "saved_request": "src/task_003_pd1_framework_guided_cdr_design/run_003_prodigy_ipsae_evaluation/inputs/submitted_requests/message_18251_subcall_0.json",
  "sha256": "7292c24a8d3bc9d78fe51af8492ec8edaa5af86347c711aba3cfce942915bea1"
}
```

**Parameters recorded for this call**

| Setting | Value / exact saved value | Recorded explanation |
| --- | --- | --- |
| `chain_list` | `["A", "B"]` | Field meaning: Chain grouping supplied to the interface/affinity tool.  |
| `input_path` | `users/680f678c1b1d883c92aa706c/1794672357339/2_model_0.pdb` | Field meaning: Tool-specific input field; it may contain a file location or sequence payload.  |

**Execution and identifiers**

```json
{
  "session_id": "20261114_110401_625a94",
  "message_id": 18251,
  "tool_call_id": "call_-7077291400051548703",
  "subcall_index": 0,
  "timestamp_utc": "2026-11-14T16:06:01.750447+00:00",
  "doc_id": "6af886ea9de6b44b075d86f1",
  "evidence_type": "original_observable_request_and_responses"
}
```

**Returned outputs / historical output names**

```json
null
```

**Validation and checks**

```json
{
  "request_matches_export": true,
  "note": "Saved arguments match exported historical tool-call arguments; this does not revalidate the scientific inputs or confirm an unresolved server job."
}
```

### C01.R06: Prodigy

Purpose: See the stage purpose.

Source: **boltzmann**; recorded state: **Success**.

Exact record: [tool_details.json](../inputs/execution_records/tool_details.json) → `/records/C01.R06`. Original call ID: `call_-7077290541058091697:subcall:0`.

Identifier/version: `Prodigy`.

**Inputs**

```json
{
  "saved_request": "src/task_003_pd1_framework_guided_cdr_design/run_003_prodigy_ipsae_evaluation/inputs/submitted_requests/message_18256_subcall_0.json",
  "sha256": "582ef3dd32cb2e1615284a41a026bc308e694e89eec48b14089bc906bc1e8b1b"
}
```

**Parameters recorded for this call**

| Setting | Value / exact saved value | Recorded explanation |
| --- | --- | --- |
| `chain_list` | `["A", "B"]` | Field meaning: Chain grouping supplied to the interface/affinity tool.  |
| `input_path` | `users/680f678c1b1d883c92aa706c/1794672367922/2_model_0.pdb` | Field meaning: Tool-specific input field; it may contain a file location or sequence payload.  |

**Execution and identifiers**

```json
{
  "session_id": "20261114_110401_625a94",
  "message_id": 18256,
  "tool_call_id": "call_-7077290541058091697",
  "subcall_index": 0,
  "timestamp_utc": "2026-11-14T16:06:12.487223+00:00",
  "doc_id": "6af886f4239a6b9f38bec38d",
  "evidence_type": "original_observable_request_and_responses"
}
```

**Returned outputs / historical output names**

```json
null
```

**Validation and checks**

```json
{
  "request_matches_export": true,
  "note": "Saved arguments match exported historical tool-call arguments; this does not revalidate the scientific inputs or confirm an unresolved server job."
}
```

### C01.R07: Prodigy

Purpose: See the stage purpose.

Source: **boltzmann**; recorded state: **Success**.

Exact record: [tool_details.json](../inputs/execution_records/tool_details.json) → `/records/C01.R07`. Original call ID: `call_-7077304972148206469:subcall:0`.

Identifier/version: `Prodigy`.

**Inputs**

```json
{
  "saved_request": "src/task_003_pd1_framework_guided_cdr_design/run_003_prodigy_ipsae_evaluation/inputs/submitted_requests/message_18260_subcall_0.json",
  "sha256": "651456da4fdc23bb2b515797b47710b7b4f9f401648d5a4c471c138d2b2bfed8"
}
```

**Parameters recorded for this call**

| Setting | Value / exact saved value | Recorded explanation |
| --- | --- | --- |
| `chain_list` | `["A", "B"]` | Field meaning: Chain grouping supplied to the interface/affinity tool.  |
| `input_path` | `users/680f678c1b1d883c92aa706c/1794672378710/1_model_0.pdb` | Field meaning: Tool-specific input field; it may contain a file location or sequence payload.  |

**Execution and identifiers**

```json
{
  "session_id": "20261114_110401_625a94",
  "message_id": 18260,
  "tool_call_id": "call_-7077304972148206469",
  "subcall_index": 0,
  "timestamp_utc": "2026-11-14T16:06:22.998525+00:00",
  "doc_id": "6af886ff9de6b44b075d872a",
  "evidence_type": "original_observable_request_and_responses"
}
```

**Returned outputs / historical output names**

```json
null
```

**Validation and checks**

```json
{
  "request_matches_export": true,
  "note": "Saved arguments match exported historical tool-call arguments; this does not revalidate the scientific inputs or confirm an unresolved server job."
}
```

### C01.R08: Prodigy

Purpose: See the stage purpose.

Source: **boltzmann**; recorded state: **Success**.

Exact record: [tool_details.json](../inputs/execution_records/tool_details.json) → `/records/C01.R08`. Original call ID: `call_-7077289956942543351:subcall:0`.

Identifier/version: `Prodigy`.

**Inputs**

```json
{
  "saved_request": "src/task_003_pd1_framework_guided_cdr_design/run_003_prodigy_ipsae_evaluation/inputs/submitted_requests/message_18267_subcall_0.json",
  "sha256": "67155df1ca1be69d58395cc27fd9ecc6862bef6d94be7bf9ac88730976fee2be"
}
```

**Parameters recorded for this call**

| Setting | Value / exact saved value | Recorded explanation |
| --- | --- | --- |
| `chain_list` | `["A", "B"]` | Field meaning: Chain grouping supplied to the interface/affinity tool.  |
| `input_path` | `users/680f678c1b1d883c92aa706c/1794672388334/2_model_0.pdb` | Field meaning: Tool-specific input field; it may contain a file location or sequence payload.  |

**Execution and identifiers**

```json
{
  "session_id": "20261114_110401_625a94",
  "message_id": 18267,
  "tool_call_id": "call_-7077289956942543351",
  "subcall_index": 0,
  "timestamp_utc": "2026-11-14T16:06:32.829029+00:00",
  "doc_id": "6af887099de6b44b075d8750",
  "evidence_type": "original_observable_request_and_responses"
}
```

**Returned outputs / historical output names**

```json
null
```

**Validation and checks**

```json
{
  "request_matches_export": true,
  "note": "Saved arguments match exported historical tool-call arguments; this does not revalidate the scientific inputs or confirm an unresolved server job."
}
```

### C01.R09: Prodigy

Purpose: See the stage purpose.

Source: **boltzmann**; recorded state: **Success**.

Exact record: [tool_details.json](../inputs/execution_records/tool_details.json) → `/records/C01.R09`. Original call ID: `call_-7077301398735415583:subcall:0`.

Identifier/version: `Prodigy`.

**Inputs**

```json
{
  "saved_request": "src/task_003_pd1_framework_guided_cdr_design/run_003_prodigy_ipsae_evaluation/inputs/submitted_requests/message_18271_subcall_0.json",
  "sha256": "af22e7feeb21c390127e2a67ab78755b9ca371d23a7787c38502fc96cc5e555b"
}
```

**Parameters recorded for this call**

| Setting | Value / exact saved value | Recorded explanation |
| --- | --- | --- |
| `chain_list` | `["A", "B"]` | Field meaning: Chain grouping supplied to the interface/affinity tool.  |
| `input_path` | `users/680f678c1b1d883c92aa706c/1794672398243/1_model_0.pdb` | Field meaning: Tool-specific input field; it may contain a file location or sequence payload.  |

**Execution and identifiers**

```json
{
  "session_id": "20261114_110401_625a94",
  "message_id": 18271,
  "tool_call_id": "call_-7077301398735415583",
  "subcall_index": 0,
  "timestamp_utc": "2026-11-14T16:06:42.969693+00:00",
  "doc_id": "6af88713239a6b9f38bec3dd",
  "evidence_type": "original_observable_request_and_responses"
}
```

**Returned outputs / historical output names**

```json
null
```

**Validation and checks**

```json
{
  "request_matches_export": true,
  "note": "Saved arguments match exported historical tool-call arguments; this does not revalidate the scientific inputs or confirm an unresolved server job."
}
```

### C01.R10: Prodigy

Purpose: See the stage purpose.

Source: **boltzmann**; recorded state: **Success**.

Exact record: [tool_details.json](../inputs/execution_records/tool_details.json) → `/records/C01.R10`. Original call ID: `call_-7077298615596608617:subcall:0`.

Identifier/version: `Prodigy`.

**Inputs**

```json
{
  "saved_request": "src/task_003_pd1_framework_guided_cdr_design/run_003_prodigy_ipsae_evaluation/inputs/submitted_requests/message_18279_subcall_0.json",
  "sha256": "22a80ba41e3c5585f7032e486e23c13d799adba301c39a4c403418fb0643c6e9"
}
```

**Parameters recorded for this call**

| Setting | Value / exact saved value | Recorded explanation |
| --- | --- | --- |
| `chain_list` | `["A", "B"]` | Field meaning: Chain grouping supplied to the interface/affinity tool.  |
| `input_path` | `users/680f678c1b1d883c92aa706c/1794672408890/2_model_0.pdb` | Field meaning: Tool-specific input field; it may contain a file location or sequence payload.  |

**Execution and identifiers**

```json
{
  "session_id": "20261114_110401_625a94",
  "message_id": 18279,
  "tool_call_id": "call_-7077298615596608617",
  "subcall_index": 0,
  "timestamp_utc": "2026-11-14T16:06:53.390711+00:00",
  "doc_id": "6af8871d239a6b9f38bec3fb",
  "evidence_type": "original_observable_request_and_responses"
}
```

**Returned outputs / historical output names**

```json
null
```

**Validation and checks**

```json
{
  "request_matches_export": true,
  "note": "Saved arguments match exported historical tool-call arguments; this does not revalidate the scientific inputs or confirm an unresolved server job."
}
```

### C01.R11: Prodigy

Purpose: See the stage purpose.

Source: **boltzmann**; recorded state: **Success**.

Exact record: [tool_details.json](../inputs/execution_records/tool_details.json) → `/records/C01.R11`. Original call ID: `call_-7077298031481060430:subcall:0`.

Identifier/version: `Prodigy`.

**Inputs**

```json
{
  "saved_request": "src/task_003_pd1_framework_guided_cdr_design/run_003_prodigy_ipsae_evaluation/inputs/submitted_requests/message_18284_subcall_0.json",
  "sha256": "40827e34ff05d998b8f09d5f7b3ca3e57d6de3d43083bc8c68c124a589dc2256"
}
```

**Parameters recorded for this call**

| Setting | Value / exact saved value | Recorded explanation |
| --- | --- | --- |
| `chain_list` | `["A", "B"]` | Field meaning: Chain grouping supplied to the interface/affinity tool.  |
| `input_path` | `users/680f678c1b1d883c92aa706c/1794672418788/1_model_0.pdb` | Field meaning: Tool-specific input field; it may contain a file location or sequence payload.  |

**Execution and identifiers**

```json
{
  "session_id": "20261114_110401_625a94",
  "message_id": 18284,
  "tool_call_id": "call_-7077298031481060430",
  "subcall_index": 0,
  "timestamp_utc": "2026-11-14T16:07:03.575566+00:00",
  "doc_id": "6af887289de6b44b075d8791",
  "evidence_type": "original_observable_request_and_responses"
}
```

**Returned outputs / historical output names**

```json
null
```

**Validation and checks**

```json
{
  "request_matches_export": true,
  "note": "Saved arguments match exported historical tool-call arguments; this does not revalidate the scientific inputs or confirm an unresolved server job."
}
```

### C01.R12: Prodigy

Purpose: See the stage purpose.

Source: **boltzmann**; recorded state: **Success**.

Exact record: [tool_details.json](../inputs/execution_records/tool_details.json) → `/records/C01.R12`. Original call ID: `call_-7077288410754313142:subcall:0`.

Identifier/version: `Prodigy`.

**Inputs**

```json
{
  "saved_request": "src/task_003_pd1_framework_guided_cdr_design/run_003_prodigy_ipsae_evaluation/inputs/submitted_requests/message_18288_subcall_0.json",
  "sha256": "84f42673ca4f2286f1f4e0dd165c20f1369a6a4f27d6995b0c8515614c46e25e"
}
```

**Parameters recorded for this call**

| Setting | Value / exact saved value | Recorded explanation |
| --- | --- | --- |
| `chain_list` | `["A", "B"]` | Field meaning: Chain grouping supplied to the interface/affinity tool.  |
| `input_path` | `users/680f678c1b1d883c92aa706c/1794672429501/2_model_0.pdb` | Field meaning: Tool-specific input field; it may contain a file location or sequence payload.  |

**Execution and identifiers**

```json
{
  "session_id": "20261114_110401_625a94",
  "message_id": 18288,
  "tool_call_id": "call_-7077288410754313142",
  "subcall_index": 0,
  "timestamp_utc": "2026-11-14T16:07:14.072758+00:00",
  "doc_id": "6af887329850a93adf67d827",
  "evidence_type": "original_observable_request_and_responses"
}
```

**Returned outputs / historical output names**

```json
null
```

**Validation and checks**

```json
{
  "request_matches_export": true,
  "note": "Saved arguments match exported historical tool-call arguments; this does not revalidate the scientific inputs or confirm an unresolved server job."
}
```

## S2_ipsae_interface_scoring: ipSAE interface score on models+PAE bundle

State: **completed**. Dependencies: `["run_002_agcdr_antibmpnn S4"]`.

Acceptance/checks: Terminal job; ipSAE scores parsed

### C02: ipsae-protein (ipSAE Generation)

Purpose: PAE-based interface score per model

Source: **boltzmann**; recorded state: **completed**.

Exact record: [tool_details.json](../inputs/execution_records/tool_details.json) → `/records/C02`. Original call ID: `run_003_prodigy_ipsae_evaluation-S2-01`.

Identifier/version: `boltzmann job ipsae-protein, doc 6af88746d29658acc304eb69`.

**Inputs**

```json
{
  "saved_request": "src/task_003_pd1_framework_guided_cdr_design/run_003_prodigy_ipsae_evaluation/inputs/submitted_requests/message_18294_subcall_0.json",
  "sha256": "5ade90cc3a7dcac6fbb17ec60eed3d3d9e6636fdc276025b93c4e1828f7fdf9d"
}
```

**Parameters recorded for this call**

| Setting | Value / exact saved value | Recorded explanation |
| --- | --- | --- |
| `pae_cutoff` | `10.0` | worker default |
| `dist_cutoff` | `10.0` | worker default |

**Execution and identifiers**

```json
{
  "doc_id": "6af88746d29658acc304eb69",
  "status": "submitted"
}
```

Original submission records: `C02.R01`. These are evidence for this call, not additional completed jobs.

### C02.R01: ipsae-protein

Purpose: See the stage purpose.

Source: **boltzmann**; recorded state: **Success**.

Exact record: [tool_details.json](../inputs/execution_records/tool_details.json) → `/records/C02.R01`. Original call ID: `call_-7077274563779753363:subcall:0`.

Identifier/version: `ipsae-protein`.

**Inputs**

```json
{
  "saved_request": "src/task_003_pd1_framework_guided_cdr_design/run_003_prodigy_ipsae_evaluation/inputs/submitted_requests/message_18294_subcall_0.json",
  "sha256": "5ade90cc3a7dcac6fbb17ec60eed3d3d9e6636fdc276025b93c4e1828f7fdf9d"
}
```

**Parameters recorded for this call**

| Setting | Value / exact saved value | Recorded explanation |
| --- | --- | --- |
| `input_path` | `users/680f678c1b1d883c92aa706c/1794672444600/boltz2_models_conf.zip` | Field meaning: Tool-specific input field; it may contain a file location or sequence payload.  |
| `model_type` | `boltz2` | Field meaning: Requested model mode/identifier.  |
| `pae_cutoff` | `10.0` | Field meaning: Predicted-aligned-error threshold supplied to the interface scorer.  |
| `dist_cutoff` | `10.0` | Field meaning: Interface distance cutoff; use the saved tool request for units.  |

**Execution and identifiers**

```json
{
  "session_id": "20261114_110401_625a94",
  "message_id": 18294,
  "tool_call_id": "call_-7077274563779753363",
  "subcall_index": 0,
  "timestamp_utc": "2026-11-14T16:07:31.370722+00:00",
  "doc_id": "6af88746d29658acc304eb69",
  "evidence_type": "original_observable_request_and_responses"
}
```

**Returned outputs / historical output names**

```json
null
```

**Validation and checks**

```json
{
  "request_matches_export": true,
  "note": "Saved arguments match exported historical tool-call arguments; this does not revalidate the scientific inputs or confirm an unresolved server job."
}
```
