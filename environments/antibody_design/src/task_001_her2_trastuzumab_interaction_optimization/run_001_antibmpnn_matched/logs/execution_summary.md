# Execution summary — run_001_antibmpnn_matched

Task: `task_001_her2_trastuzumab_interaction_optimization`. Saved run status: **complete**.

Record organization updated 2026-11-16. This is a retrospective presentation of saved execution evidence.

[Compact config](../../../../results/task_001_her2_trastuzumab_interaction_optimization/run_001_antibmpnn_matched/run.json) · [Workflow](../workflow.md) · [Activity log](agent_scientist_log.md) · [Exact original config](../inputs/execution_records/full_config.json) · [Tool details](../inputs/execution_records/tool_details.json) · [File inventory and SHA-256](../inputs/execution_records/run_files.csv)

## Preparation and inputs

Objective: Reference-guided interaction optimization of trastuzumab Fv against HER2 ECD

Original input provenance, chain/mask contracts and readiness records are retained below. Current file locations, sizes and full SHA-256 values are in `../inputs/execution_records/run_files.csv`.

```json
{
  "1n8z.pdb": {
    "path": "src/task_001_her2_trastuzumab_interaction_optimization/run_001_antibmpnn_matched/inputs/1n8z.pdb",
    "sha256": "ed934d36503335c6764b08880f9e50933d99eb13b9bf145339cfcaee150eb21e",
    "provenance": "RCSB files.rcsb.org/download/1N8Z.pdb"
  },
  "complex_fv_her2.pdb": {
    "path": "src/task_001_her2_trastuzumab_interaction_optimization/run_001_antibmpnn_matched/inputs/complex_fv_her2.pdb",
    "sha256": "4e774d2a59edbe1e9dbfcf88e15a0a483b7021d46b1a31f5cf171e09cbfc5ac9"
  },
  "antibody_fv.pdb": {
    "sha256": "1866856a37221fc8dc59f29d7f075714acde9d1fe1523e5038077f4c249b492c"
  },
  "antigen_her2.pdb": {
    "sha256": "66863dac0dbd4f6e6d9739eeacc5abfd5baab736ddd52df8b99f319c706cbe92"
  },
  "reference_sequences.json": {
    "sha256": "7a32d7d9db34a9a2f1bb3f873096eb9327af27359469de01729321524da880ba"
  },
  "crystal_contacts.csv": {
    "sha256": "75d3f880bc3592df62eb89ae79c89da2fe9e3c70f1164234281f005773e24bcd"
  }
}
```

## Recorded outcome

```json
{
  "workflows_designed": 3,
  "selected": 1,
  "executed": 1,
  "not_selected": 1,
  "not_run": 1,
  "generated": 40,
  "unique_candidates": 38,
  "evaluated": 8,
  "unevaluated": 30,
  "jobs_ledger": "inputs/job_map.json (25 entries)",
  "top_shortlist": "T001-C005 (pre-stated rank key)",
  "integrative_lead": "T001-C008",
  "last_update": "2026-11-14T14:10Z"
}
```

## Workflow steps and tools

Settings shown below are recorded values. Exact submitted arguments, payloads, resources, responses, validation and fallback details remain in `../inputs/execution_records/tool_details.json`. Historical output names are retained as evidence; use `run_files.csv` for current saved locations.

## S0_prep: fetch/verify/split 1N8Z; build correctly numbered design input

State: **complete**. Dependencies: `[]`.

Acceptance/checks: VH/VL 100% trastuzumab; chains verified; CDR windows computed

### C01: stage0_fetch_verify.py

Purpose: fetch 1N8Z, verify chains/sequences, split Fv/HER2, contact map

Source: **open_source**; recorded state: **complete**.

Exact record: [tool_details.json](../inputs/execution_records/tool_details.json) → `/records/C01`. Original call ID: `S0-1`.

Identifier/version: `local python3`.

**Inputs**

```json
{
  "pdb": "inputs/1n8z.pdb (sha256 ed934d36...)"
}
```


**Execution and identifiers**

```json
{
  "command": "python3 code/stage0_fetch_verify.py",
  "log": "stage0_run.log"
}
```

**Returned outputs / historical output names**

```json
{
  "outputs": [
    "inputs/antibody_fv.pdb",
    "inputs/antigen_her2.pdb",
    "inputs/crystal_contacts.csv",
    "inputs/reference_sequences.json"
  ]
}
```

**Validation and checks**

```json
"VH/VL 100% match; A=light(214)/B=heavy(220)/C=HER2(581/607)"
```

### C02: stage0b_fix_numbering.py

Purpose: fix per-atom residue numbering bug; rebuild with per-residue numbering + SEQRES + TER/END

Source: **open_source**; recorded state: **complete**.

Exact record: [tool_details.json](../inputs/execution_records/tool_details.json) → `/records/C02`. Original call ID: `S0-2`.

Identifier/version: `local python3`.

**Inputs**

```json
{
  "input": "inputs/1n8z.pdb"
}
```

**Parameters recorded for this call**

| Setting | Value / exact saved value | Recorded explanation |
| --- | --- | --- |
| `CROP` | `A=107 VL, B=120 VH (variable-domain crop)` | Field meaning: Chain/domain segments retained during preparation.  |
| `renumber` | `per-residue sequential` | Field meaning: Residue-numbering transformation applied during preparation.  |

**Execution and identifiers**

```json
{
  "command": "python3 code/stage0b_fix_numbering.py"
}
```

**Returned outputs / historical output names**

```json
{
  "outputs": [
    "inputs/complex_hl_a_seqres.pdb (sha256 9e54b25d680daa48)"
  ]
}
```

**Validation and checks**

```json
"H=VH(120)/L=VL(107)/A=HER2(581); CDR windows verified"
```

**Failures, retries and fallback**

```json
{
  "prior_call": "S0-1",
  "error": "AntiBMPNN x4: Expected exactly one heavy/VHH domain (per-atom numbering made VH=924 residues)",
  "recovery": "stage0b rewrite"
}
```

## S1_design: CDR-only fixed-backbone redesign of trastuzumab Fv

State: **complete**. Dependencies: `["S0_prep"]`.

Acceptance/checks: sequences returned; all edits inside CDR mask; framework identical

### C03: AntiBMPNN

Purpose: design attempts 1-4 (rejected inputs)

Source: **boltzmann**; recorded state: **failed**.

Exact record: [tool_details.json](../inputs/execution_records/tool_details.json) → `/records/C03`. Original call ID: `S1-a1..a4`.

Identifier/version: `boltzmann AntiBMPNN`.

**Inputs**

```json
{
  "inputs": [
    "complex_fv_her2.pdb",
    "complex_vhvl_her2.pdb",
    "complex_vhvl_her2_ter.pdb",
    "fv_vhvl_only.pdb"
  ]
}
```


**Execution and identifiers**

```json
{
  "doc_ids": [
    "6af844059de6b44b075d79e0",
    "6af844589030bff41644751b",
    "6af844ca9850a93adf67cad5",
    "6af8453c239a6b9f38beb6dd"
  ],
  "error": "Expected exactly one heavy/VHH domain; detected 0"
}
```

**Validation and checks**

```json
"terminal failure x4"
```

**Failures, retries and fallback**

```json
{
  "prior_stage": "S0-1",
  "error": "input numbering",
  "recovery": "S0-2 rebuild",
  "reason": "input format",
  "alternative": "complex_hl_a_seqres.pdb"
}
```

Original submission records: `C03.R01`, `C03.R02`, `C03.R03`, `C03.R04`. These are evidence for this call, not additional completed jobs.

### C03.R01: AntiBMPNN

Purpose: See the stage purpose.

Source: **boltzmann**; recorded state: **failed**.

Exact record: [tool_details.json](../inputs/execution_records/tool_details.json) → `/records/C03.R01`. Original call ID: `call_-7077579300299335558:subcall:0`.

Identifier/version: `AntiBMPNN`.

**Inputs**

```json
{
  "saved_request": "src/task_001_her2_trastuzumab_interaction_optimization/run_001_antibmpnn_matched/inputs/submitted_requests/message_16414_subcall_0.json",
  "sha256": "1b08763c4ca78ac8cc51b7f54179c8833ed1ff15f4b5c2710062f0eabea6f487"
}
```

**Parameters recorded for this call**

| Setting | Value / exact saved value | Recorded explanation |
| --- | --- | --- |
| `chains_to_design` | `["H", "L"]` | Field meaning: Chains selected in the submitted design request.  |
| `generation_count` | `40` | Field meaning: Number of samples requested in that call.  |
| `input_path` | `users/68d12a5de5b6a2fdc0e3c443/1794655224765/complex_fv_her2.pdb` | Field meaning: Tool-specific input field; it may contain a file location or sequence payload.  |
| `residue_positions_to_design` | `{"H": "31-35,50-65,95-102", "L": "24-34,50-56,89-97"}` | Field meaning: Per-chain residue positions supplied in the exact request.  |

**Execution and identifiers**

```json
{
  "session_id": "20261114_110112_c07285",
  "message_id": 16414,
  "tool_call_id": "call_-7077579300299335558",
  "subcall_index": 0,
  "timestamp_utc": "2026-11-14T11:20:37.730417+00:00",
  "doc_id": "6af844059de6b44b075d79e0",
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

### C03.R02: AntiBMPNN

Purpose: See the stage purpose.

Source: **boltzmann**; recorded state: **failed**.

Exact record: [tool_details.json](../inputs/execution_records/tool_details.json) → `/records/C03.R02`. Original call ID: `call_-7077575039691783799:subcall:0`.

Identifier/version: `AntiBMPNN`.

**Inputs**

```json
{
  "saved_request": "src/task_001_her2_trastuzumab_interaction_optimization/run_001_antibmpnn_matched/inputs/submitted_requests/message_16492_subcall_0.json",
  "sha256": "b0f9687edccc3074aaca15440be36cab10659c4426175c10c3bfb9fec7f464e0"
}
```

**Parameters recorded for this call**

| Setting | Value / exact saved value | Recorded explanation |
| --- | --- | --- |
| `chains_to_design` | `["A", "B"]` | Field meaning: Chains selected in the submitted design request.  |
| `generation_count` | `40` | Field meaning: Number of samples requested in that call.  |
| `input_path` | `users/68d12a5de5b6a2fdc0e3c443/1794655314759/complex_vhvl_her2.pdb` | Field meaning: Tool-specific input field; it may contain a file location or sequence payload.  |
| `residue_positions_to_design` | `{"A": "31-35,50-65,95-102", "B": "24-34,50-56,89-97"}` | Field meaning: Per-chain residue positions supplied in the exact request.  |

**Execution and identifiers**

```json
{
  "session_id": "20261114_110112_c07285",
  "message_id": 16492,
  "tool_call_id": "call_-7077575039691783799",
  "subcall_index": 0,
  "timestamp_utc": "2026-11-14T11:22:00.318391+00:00",
  "doc_id": "6af844589030bff41644751b",
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

### C03.R03: AntiBMPNN

Purpose: See the stage purpose.

Source: **boltzmann**; recorded state: **failed**.

Exact record: [tool_details.json](../inputs/execution_records/tool_details.json) → `/records/C03.R03`. Original call ID: `call_-7077577238715039327:subcall:0`.

Identifier/version: `AntiBMPNN`.

**Inputs**

```json
{
  "saved_request": "src/task_001_her2_trastuzumab_interaction_optimization/run_001_antibmpnn_matched/inputs/submitted_requests/message_16568_subcall_0.json",
  "sha256": "c6bf778f4a5a3a71106665a067d081654297659d29365033d79894fc5841e2e6"
}
```

**Parameters recorded for this call**

| Setting | Value / exact saved value | Recorded explanation |
| --- | --- | --- |
| `chains_to_design` | `["A", "B"]` | Field meaning: Chains selected in the submitted design request.  |
| `generation_count` | `40` | Field meaning: Number of samples requested in that call.  |
| `input_path` | `users/68d12a5de5b6a2fdc0e3c443/1794655428858/complex_vhvl_her2_ter.pdb` | Field meaning: Tool-specific input field; it may contain a file location or sequence payload.  |
| `residue_positions_to_design` | `{"A": "31-35,50-65,95-102", "B": "24-34,50-56,89-97"}` | Field meaning: Per-chain residue positions supplied in the exact request.  |

**Execution and identifiers**

```json
{
  "session_id": "20261114_110112_c07285",
  "message_id": 16568,
  "tool_call_id": "call_-7077577238715039327",
  "subcall_index": 0,
  "timestamp_utc": "2026-11-14T11:23:54.354766+00:00",
  "doc_id": "6af844ca9850a93adf67cad5",
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

### C03.R04: AntiBMPNN

Purpose: See the stage purpose.

Source: **boltzmann**; recorded state: **failed**.

Exact record: [tool_details.json](../inputs/execution_records/tool_details.json) → `/records/C03.R04`. Original call ID: `call_-7077571706797161870:subcall:0`.

Identifier/version: `AntiBMPNN`.

**Inputs**

```json
{
  "saved_request": "src/task_001_her2_trastuzumab_interaction_optimization/run_001_antibmpnn_matched/inputs/submitted_requests/message_16614_subcall_0.json",
  "sha256": "ecb46baf625050cb154bfc60c2ace2198244101a77fbcf5020ba9787f99cfcf4"
}
```

**Parameters recorded for this call**

| Setting | Value / exact saved value | Recorded explanation |
| --- | --- | --- |
| `chains_to_design` | `["A", "B"]` | Field meaning: Chains selected in the submitted design request.  |
| `generation_count` | `40` | Field meaning: Number of samples requested in that call.  |
| `input_path` | `users/68d12a5de5b6a2fdc0e3c443/1794655540930/fv_vhvl_only.pdb` | Field meaning: Tool-specific input field; it may contain a file location or sequence payload.  |
| `residue_positions_to_design` | `{"A": "31-35,50-65,95-102", "B": "24-34,50-56,89-97"}` | Field meaning: Per-chain residue positions supplied in the exact request.  |

**Execution and identifiers**

```json
{
  "session_id": "20261114_110112_c07285",
  "message_id": 16614,
  "tool_call_id": "call_-7077571706797161870",
  "subcall_index": 0,
  "timestamp_utc": "2026-11-14T11:25:48.096608+00:00",
  "doc_id": "6af8453c239a6b9f38beb6dd",
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

### C04: AntiBMPNN

Purpose: benign control (1MCP) to bisect service vs input fault

Source: **boltzmann**; recorded state: **complete**.

Exact record: [tool_details.json](../inputs/execution_records/tool_details.json) → `/records/C04`. Original call ID: `S1-control`.

Identifier/version: `boltzmann AntiBMPNN`.

**Inputs**

```json
{
  "input": "inputs/1mcp_control.pdb (340,443 bytes)"
}
```

**Parameters recorded for this call**

| Setting | Value / exact saved value | Recorded explanation |
| --- | --- | --- |
| `chains_to_design` | `["H", "L"]` | Field meaning: Chains selected in the submitted design request.  |
| `generation_count` | `2` | Field meaning: Number of samples requested in that call.  |
| `input_path` | `users/68d12a5de5b6a2fdc0e3c443/1794655604072/1mcp_control.pdb` | Field meaning: Tool-specific input field; it may contain a file location or sequence payload.  |
| `residue_positions_to_design` | `{}` | Field meaning: Per-chain residue positions supplied in the exact request.  |

**Execution and identifiers**

```json
{
  "doc_id": "6af84579239a6b9f38beb714",
  "cost_usd": 1
}
```

**Validation and checks**

```json
"service healthy; failures were input-format"
```

Original submission records: `C04.R01`. These are evidence for this call, not additional completed jobs.

### C04.R01: AntiBMPNN

Purpose: See the stage purpose.

Source: **boltzmann**; recorded state: **Success**.

Exact record: [tool_details.json](../inputs/execution_records/tool_details.json) → `/records/C04.R01`. Original call ID: `call_-7077585931728844002:subcall:0`.

Identifier/version: `AntiBMPNN`.

**Inputs**

```json
{
  "saved_request": "src/task_001_her2_trastuzumab_interaction_optimization/run_001_antibmpnn_matched/inputs/submitted_requests/message_16656_subcall_0.json",
  "sha256": "0b0bad500b12a0f0181e8ef13d00393174cfb64aebc6e44164cbf233f7ff6815"
}
```

**Parameters recorded for this call**

| Setting | Value / exact saved value | Recorded explanation |
| --- | --- | --- |
| `chains_to_design` | `["H", "L"]` | Field meaning: Chains selected in the submitted design request.  |
| `generation_count` | `2` | Field meaning: Number of samples requested in that call.  |
| `input_path` | `users/68d12a5de5b6a2fdc0e3c443/1794655604072/1mcp_control.pdb` | Field meaning: Tool-specific input field; it may contain a file location or sequence payload.  |
| `residue_positions_to_design` | `{}` | Field meaning: Per-chain residue positions supplied in the exact request.  |

**Execution and identifiers**

```json
{
  "session_id": "20261114_110112_c07285",
  "message_id": 16656,
  "tool_call_id": "call_-7077585931728844002",
  "subcall_index": 0,
  "timestamp_utc": "2026-11-14T11:26:49.668764+00:00",
  "doc_id": "6af84579239a6b9f38beb714",
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

### C05: AntiBMPNN

Purpose: winning design run: 40 CDR-redesign generations on fixed 1N8Z Fv backbone

Source: **boltzmann**; recorded state: **complete**.

Exact record: [tool_details.json](../inputs/execution_records/tool_details.json) → `/records/C05`. Original call ID: `S1-final`.

Identifier/version: `boltzmann AntiBMPNN`.

**Inputs**

```json
{
  "input": "users/68d12a5de5b6a2fdc0e3c443/1794655764557/complex_hl_a_seqres.pdb",
  "sha256": "9e54b25d680daa48749f87bf1cc4038a8a09d0dd3217387241aaa3d354bd98cd"
}
```

**Parameters recorded for this call**

| Setting | Value / exact saved value | Recorded explanation |
| --- | --- | --- |
| `generation_count` | `40 candidates within budget` | Field meaning: Number of samples requested in that call.  |
| `residue_positions_to_design` | `Kabat CDR windows (task constraint: CDR-only)` | Field meaning: Per-chain residue positions supplied in the exact request.  |

**Execution and identifiers**

```json
{
  "doc_id": "6af8461a9850a93adf67cb88",
  "experiment_name": "AntiBMPNN - 20261114-112354Z - fb6923",
  "completed_utc": "~2026-11-14T11:32:07Z"
}
```

**Returned outputs / historical output names**

```json
{
  "outputs": [
    "inputs/antibmpnn_results.zip (40,806 bytes)"
  ],
  "validation": "40 sequences; domains H=VH(120) L=VL(107) kappa"
}
```

Original submission records: `C05.R01`. These are evidence for this call, not additional completed jobs.

### C05.R01: AntiBMPNN

Purpose: See the stage purpose.

Source: **boltzmann**; recorded state: **Success**.

Exact record: [tool_details.json](../inputs/execution_records/tool_details.json) → `/records/C05.R01`. Original call ID: `call_-7077572531430878641:subcall:0`.

Identifier/version: `AntiBMPNN`.

**Inputs**

```json
{
  "saved_request": "src/task_001_her2_trastuzumab_interaction_optimization/run_001_antibmpnn_matched/inputs/submitted_requests/message_16729_subcall_0.json",
  "sha256": "79fa7bb874689d878f206db6dc180a72dc6aa5da997bfdbe1a094c83a32635fa"
}
```

**Parameters recorded for this call**

| Setting | Value / exact saved value | Recorded explanation |
| --- | --- | --- |
| `chains_to_design` | `["H", "L"]` | Field meaning: Chains selected in the submitted design request.  |
| `generation_count` | `40` | Field meaning: Number of samples requested in that call.  |
| `input_path` | `users/68d12a5de5b6a2fdc0e3c443/1794655764557/complex_hl_a_seqres.pdb` | Field meaning: Tool-specific input field; it may contain a file location or sequence payload.  |
| `residue_positions_to_design` | `{"H": "31-35,50-65,95-102", "L": "24-34,50-56,89-97"}` | Field meaning: Per-chain residue positions supplied in the exact request.  |

**Execution and identifiers**

```json
{
  "session_id": "20261114_110112_c07285",
  "message_id": 16729,
  "tool_call_id": "call_-7077572531430878641",
  "subcall_index": 0,
  "timestamp_utc": "2026-11-14T11:29:30.581045+00:00",
  "doc_id": "6af8461a9850a93adf67cb88",
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

## S2_verify: edit-mask verification, dedupe, candidate table

State: **complete**. Dependencies: `["S1_design"]`.

Acceptance/checks: 100% mutations inside mask; framework byte-identical; no new Cys

### C06: stage2_verify_mask.py

Purpose: position-by-position mask verification + dedupe + liability scan

Source: **open_source**; recorded state: **complete**.

Exact record: [tool_details.json](../inputs/execution_records/tool_details.json) → `/records/C06`. Original call ID: `S2-1`.

Identifier/version: `local python3`.

**Inputs**

```json
{
  "input": "inputs/antibmpnn_results.zip"
}
```

**Parameters recorded for this call**

| Setting | Value / exact saved value | Recorded explanation |
| --- | --- | --- |
| `mask` | `Kabat CDR windows` | Field meaning: Recorded editable/protected-residue mask.  |

**Execution and identifiers**

```json
{
  "command": "python3 code/stage2_verify_mask.py"
}
```

**Returned outputs / historical output names**

```json
{
  "outputs": [
    "inputs/candidates.json (38 unique)"
  ]
}
```

**Validation and checks**

```json
"40/40 mask-clean; 0 framework violations; 0 new Cys; 2 dup pairs removed; NG/DS/DT motifs inherited from reference"
```

## S3_structure: matched Boltz2 complex prediction: reference + top-8 candidates

State: **complete**. Dependencies: `["S2_verify"]`.

Acceptance/checks: all jobs terminal Success; artifacts downloaded

### C07: Boltz2

Purpose: reference complex prediction (trastuzumab VH/VL vs HER2 construct)

Source: **boltzmann**; recorded state: **complete**.

Exact record: [tool_details.json](../inputs/execution_records/tool_details.json) → `/records/C07`. Original call ID: `S3-ref`.

Identifier/version: `boltzmann boltz_structure_prediction`.

**Inputs**

```json
{
  "Protein_Sequences": "[HER2_construct_607aa, VH_120aa, VL_107aa] (exact in inputs/boltz2_payloads.json[0])"
}
```

**Parameters recorded for this call**

| Setting | Value / exact saved value | Recorded explanation |
| --- | --- | --- |
| `DNA_Sequences` | `[]` | Field meaning: Submitted DNA sequence list.  |
| `Protein_Sequences` | `{"record": "C07", "pointer": "/parameters/Protein_Sequences", "summary": "sequence lengths: 607, 120, 107"}` | Field meaning: Submitted protein sequence list; order is preserved in the exact request.  |
| `RNA_Sequences` | `[]` | Field meaning: Submitted RNA sequence list.  |
| `SMILES` | `[]` | Field meaning: Submitted small-molecule representations.  |

**Execution and identifiers**

```json
{
  "doc_id": "6af84747445ae94313c3a9ae",
  "account": "users/68d12a5de5b6a2fdc0e3c443 (old key)"
}
```

**Returned outputs / historical output names**

```json
{
  "outputs": [
    "inputs/boltz2_reference/{pdbs_outputs.zip,outputs.zip,paths.csv}"
  ]
}
```

**Validation and checks**

```json
"Success; pairwise records rec1=HER2+VH ipTM 0.220, rec2=HER2+VL ipTM 0.340"
```

Original submission records: `C07.R01`. These are evidence for this call, not additional completed jobs.

### C07.R01: Boltz2

Purpose: See the stage purpose.

Source: **boltzmann**; recorded state: **Success**.

Exact record: [tool_details.json](../inputs/execution_records/tool_details.json) → `/records/C07.R01`. Original call ID: `call_-7077568167744108664:subcall:0`.

Identifier/version: `Boltz2`.

**Inputs**

```json
{
  "saved_request": "src/task_001_her2_trastuzumab_interaction_optimization/run_001_antibmpnn_matched/inputs/submitted_requests/message_16852_subcall_0.json",
  "sha256": "b27f6ad23d4fdd9fa885450f34cc177bd09a0ab21a309a3f3a971c88c09a43a4"
}
```

**Parameters recorded for this call**

| Setting | Value / exact saved value | Recorded explanation |
| --- | --- | --- |
| `DNA_Sequences` | `[]` | Field meaning: Submitted DNA sequence list.  |
| `Protein_Sequences` | `{"record": "C07.R01", "pointer": "/parameters/Protein_Sequences", "summary": "sequence lengths: 607, 120, 107"}` | Field meaning: Submitted protein sequence list; order is preserved in the exact request.  |
| `RNA_Sequences` | `[]` | Field meaning: Submitted RNA sequence list.  |
| `SMILES` | `[]` | Field meaning: Submitted small-molecule representations.  |

**Execution and identifiers**

```json
{
  "session_id": "20261114_110112_c07285",
  "message_id": 16852,
  "tool_call_id": "call_-7077568167744108664",
  "subcall_index": 0,
  "timestamp_utc": "2026-11-14T11:34:31.466881+00:00",
  "doc_id": "6af84747445ae94313c3a9ae",
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

### C08: Boltz2

Purpose: candidate complex prediction T001-C001

Source: **boltzmann**; recorded state: **complete**.

Exact record: [tool_details.json](../inputs/execution_records/tool_details.json) → `/records/C08`. Original call ID: `S3-T001-C001`.

Identifier/version: `boltzmann boltz_structure_prediction`.

**Inputs**

```json
{
  "payload": "inputs/boltz2_payloads.json[T001-C001]"
}
```


**Execution and identifiers**

```json
{
  "doc_id": "6af87767239a6b9f38beba67",
  "account": "users/680f678c1b1d883c92aa706c (new key)"
}
```

**Returned outputs / historical output names**

```json
{
  "outputs": [
    "inputs/boltz2_candidates/T001-C001/"
  ]
}
```

**Validation and checks**

```json
"Success"
```

### C09: Boltz2

Purpose: candidate complex prediction T001-C002

Source: **boltzmann**; recorded state: **complete**.

Exact record: [tool_details.json](../inputs/execution_records/tool_details.json) → `/records/C09`. Original call ID: `S3-T001-C002`.

Identifier/version: `boltzmann boltz_structure_prediction`.

**Inputs**

```json
{
  "payload": "inputs/boltz2_payloads.json[T001-C002]"
}
```


**Execution and identifiers**

```json
{
  "doc_id": "6af87769239a6b9f38beba72",
  "account": "users/680f678c1b1d883c92aa706c (new key)"
}
```

**Returned outputs / historical output names**

```json
{
  "outputs": [
    "inputs/boltz2_candidates/T001-C002/"
  ]
}
```

**Validation and checks**

```json
"Success"
```

### C10: Boltz2

Purpose: candidate complex prediction T001-C003

Source: **boltzmann**; recorded state: **complete**.

Exact record: [tool_details.json](../inputs/execution_records/tool_details.json) → `/records/C10`. Original call ID: `S3-T001-C003`.

Identifier/version: `boltzmann boltz_structure_prediction`.

**Inputs**

```json
{
  "payload": "inputs/boltz2_payloads.json[T001-C003]"
}
```


**Execution and identifiers**

```json
{
  "doc_id": "6af8776c9850a93adf67ce91",
  "account": "users/680f678c1b1d883c92aa706c (new key)"
}
```

**Returned outputs / historical output names**

```json
{
  "outputs": [
    "inputs/boltz2_candidates/T001-C003/"
  ]
}
```

**Validation and checks**

```json
"Success"
```

### C11: Boltz2

Purpose: candidate complex prediction T001-C004

Source: **boltzmann**; recorded state: **complete**.

Exact record: [tool_details.json](../inputs/execution_records/tool_details.json) → `/records/C11`. Original call ID: `S3-T001-C004`.

Identifier/version: `boltzmann boltz_structure_prediction`.

**Inputs**

```json
{
  "payload": "inputs/boltz2_payloads.json[T001-C004]"
}
```


**Execution and identifiers**

```json
{
  "doc_id": "6af8776e9de6b44b075d7e2f",
  "account": "users/680f678c1b1d883c92aa706c (new key)"
}
```

**Returned outputs / historical output names**

```json
{
  "outputs": [
    "inputs/boltz2_candidates/T001-C004/"
  ]
}
```

**Validation and checks**

```json
"Success"
```

### C12: Boltz2

Purpose: candidate complex prediction T001-C005

Source: **boltzmann**; recorded state: **complete**.

Exact record: [tool_details.json](../inputs/execution_records/tool_details.json) → `/records/C12`. Original call ID: `S3-T001-C005`.

Identifier/version: `boltzmann boltz_structure_prediction`.

**Inputs**

```json
{
  "payload": "inputs/boltz2_payloads.json[T001-C005]"
}
```


**Execution and identifiers**

```json
{
  "doc_id": "6af87770445ae94313c3add0",
  "account": "users/680f678c1b1d883c92aa706c (new key)"
}
```

**Returned outputs / historical output names**

```json
{
  "outputs": [
    "inputs/boltz2_candidates/T001-C005/"
  ]
}
```

**Validation and checks**

```json
"Success"
```

### C13: Boltz2

Purpose: candidate complex prediction T001-C006

Source: **boltzmann**; recorded state: **complete**.

Exact record: [tool_details.json](../inputs/execution_records/tool_details.json) → `/records/C13`. Original call ID: `S3-T001-C006`.

Identifier/version: `boltzmann boltz_structure_prediction`.

**Inputs**

```json
{
  "payload": "inputs/boltz2_payloads.json[T001-C006]"
}
```


**Execution and identifiers**

```json
{
  "doc_id": "6af87773239a6b9f38beba85",
  "account": "users/680f678c1b1d883c92aa706c (new key)"
}
```

**Returned outputs / historical output names**

```json
{
  "outputs": [
    "inputs/boltz2_candidates/T001-C006/"
  ]
}
```

**Validation and checks**

```json
"Success"
```

### C14: Boltz2

Purpose: candidate complex prediction T001-C007

Source: **boltzmann**; recorded state: **complete**.

Exact record: [tool_details.json](../inputs/execution_records/tool_details.json) → `/records/C14`. Original call ID: `S3-T001-C007`.

Identifier/version: `boltzmann boltz_structure_prediction`.

**Inputs**

```json
{
  "payload": "inputs/boltz2_payloads.json[T001-C007]"
}
```


**Execution and identifiers**

```json
{
  "doc_id": "6af877759de6b44b075d7e3e",
  "account": "users/680f678c1b1d883c92aa706c (new key)"
}
```

**Returned outputs / historical output names**

```json
{
  "outputs": [
    "inputs/boltz2_candidates/T001-C007/"
  ]
}
```

**Validation and checks**

```json
"Success"
```

### C15: Boltz2

Purpose: candidate complex prediction T001-C008

Source: **boltzmann**; recorded state: **complete**.

Exact record: [tool_details.json](../inputs/execution_records/tool_details.json) → `/records/C15`. Original call ID: `S3-T001-C008`.

Identifier/version: `boltzmann boltz_structure_prediction`.

**Inputs**

```json
{
  "payload": "inputs/boltz2_payloads.json[T001-C008]"
}
```


**Execution and identifiers**

```json
{
  "doc_id": "6af877789030bff416447921",
  "account": "users/680f678c1b1d883c92aa706c (new key)"
}
```

**Returned outputs / historical output names**

```json
{
  "outputs": [
    "inputs/boltz2_candidates/T001-C008/"
  ]
}
```

**Validation and checks**

```json
"Success"
```

## S4_affinity: Prodigy binding-affinity on Boltz2 structures (both records per construct)

State: **complete**. Dependencies: `["S3_structure"]`.

Acceptance/checks: prodigy.csv per construct

### C16: Prodigy

Purpose: v1 submissions with nested pdbs_outputs.zip

Source: **boltzmann**; recorded state: **failed**.

Exact record: [tool_details.json](../inputs/execution_records/tool_details.json) → `/records/C16`. Original call ID: `S4-v1`.

Identifier/version: `boltzmann Prodigy`.

**Inputs**

```json
{
  "input": "pdbs_outputs.zip (nested boltz_pdb/)"
}
```

**Parameters recorded for this call**

| Setting | Value / exact saved value | Recorded explanation |
| --- | --- | --- |
| `chain_list` | `[] = automatic pairwise analysis of uppercase chains` | Field meaning: Chain grouping supplied to the interface/affinity tool.  |

**Execution and identifiers**

```json
{
  "doc_ids": [
    "6af87c88d29658acc304e3e3",
    "6af87c8a445ae94313c3b2c3",
    "6af87c8c9de6b44b075d8065",
    "6af87c8e9850a93adf67d0b0",
    "6af87c8f445ae94313c3b2d1",
    "6af87c91239a6b9f38bebcb8",
    "6af87c939850a93adf67d0bb",
    "6af87c949850a93adf67d0c6",
    "6af87c96d29658acc304e3f6"
  ],
  "error": "Signed URL download failed: 404 / no nonempty PDB files at supported archive level"
}
```

**Validation and checks**

```json
"all 9 failed"
```

**Failures, retries and fallback**

```json
{
  "error": "nested archive level unsupported",
  "recovery": "flatten zips (PDBs at root)",
  "reason": "input format",
  "alternative": "flat zip resubmission, one per job (policy: one corrected resubmission)"
}
```

### C17: Prodigy

Purpose: flat-zip corrected submission REFERENCE

Source: **boltzmann**; recorded state: **complete**.

Exact record: [tool_details.json](../inputs/execution_records/tool_details.json) → `/records/C17`. Original call ID: `S4-REFERENCE`.

Identifier/version: `boltzmann Prodigy`.

**Inputs**

```json
{
  "input": "inputs/prodigy_flat/REFERENCE_flat.zip"
}
```

**Parameters recorded for this call**

| Setting | Value / exact saved value | Recorded explanation |
| --- | --- | --- |
| `chain_list` | `[] automatic pairwise` | Field meaning: Chain grouping supplied to the interface/affinity tool.  |

**Execution and identifiers**

```json
{
  "doc_id": "6af883e0d29658acc304e85a"
}
```

**Returned outputs / historical output names**

```json
{
  "outputs": [
    "inputs/prodigy/REFERENCE/prodigy.csv"
  ]
}
```

**Validation and checks**

```json
"Success"
```

### C18: Prodigy

Purpose: flat-zip corrected submission T001-C001

Source: **boltzmann**; recorded state: **complete**.

Exact record: [tool_details.json](../inputs/execution_records/tool_details.json) → `/records/C18`. Original call ID: `S4-T001-C001`.

Identifier/version: `boltzmann Prodigy`.

**Inputs**

```json
{
  "input": "inputs/prodigy_flat/T001-C001_flat.zip"
}
```

**Parameters recorded for this call**

| Setting | Value / exact saved value | Recorded explanation |
| --- | --- | --- |
| `chain_list` | `[] automatic pairwise` | Field meaning: Chain grouping supplied to the interface/affinity tool.  |

**Execution and identifiers**

```json
{
  "doc_id": "6af883e39de6b44b075d8496"
}
```

**Returned outputs / historical output names**

```json
{
  "outputs": [
    "inputs/prodigy/T001-C001/prodigy.csv"
  ]
}
```

**Validation and checks**

```json
"Success"
```

### C19: Prodigy

Purpose: flat-zip corrected submission T001-C002

Source: **boltzmann**; recorded state: **complete**.

Exact record: [tool_details.json](../inputs/execution_records/tool_details.json) → `/records/C19`. Original call ID: `S4-T001-C002`.

Identifier/version: `boltzmann Prodigy`.

**Inputs**

```json
{
  "input": "inputs/prodigy_flat/T001-C002_flat.zip"
}
```

**Parameters recorded for this call**

| Setting | Value / exact saved value | Recorded explanation |
| --- | --- | --- |
| `chain_list` | `[] automatic pairwise` | Field meaning: Chain grouping supplied to the interface/affinity tool.  |

**Execution and identifiers**

```json
{
  "doc_id": "6af883e4d29658acc304e869"
}
```

**Returned outputs / historical output names**

```json
{
  "outputs": [
    "inputs/prodigy/T001-C002/prodigy.csv"
  ]
}
```

**Validation and checks**

```json
"Success"
```

### C20: Prodigy

Purpose: flat-zip corrected submission T001-C003

Source: **boltzmann**; recorded state: **complete**.

Exact record: [tool_details.json](../inputs/execution_records/tool_details.json) → `/records/C20`. Original call ID: `S4-T001-C003`.

Identifier/version: `boltzmann Prodigy`.

**Inputs**

```json
{
  "input": "inputs/prodigy_flat/T001-C003_flat.zip"
}
```

**Parameters recorded for this call**

| Setting | Value / exact saved value | Recorded explanation |
| --- | --- | --- |
| `chain_list` | `[] automatic pairwise` | Field meaning: Chain grouping supplied to the interface/affinity tool.  |

**Execution and identifiers**

```json
{
  "doc_id": "6af883e69850a93adf67d51a"
}
```

**Returned outputs / historical output names**

```json
{
  "outputs": [
    "inputs/prodigy/T001-C003/prodigy.csv"
  ]
}
```

**Validation and checks**

```json
"Success"
```

### C21: Prodigy

Purpose: flat-zip corrected submission T001-C004

Source: **boltzmann**; recorded state: **complete**.

Exact record: [tool_details.json](../inputs/execution_records/tool_details.json) → `/records/C21`. Original call ID: `S4-T001-C004`.

Identifier/version: `boltzmann Prodigy`.

**Inputs**

```json
{
  "input": "inputs/prodigy_flat/T001-C004_flat.zip"
}
```

**Parameters recorded for this call**

| Setting | Value / exact saved value | Recorded explanation |
| --- | --- | --- |
| `chain_list` | `[] automatic pairwise` | Field meaning: Chain grouping supplied to the interface/affinity tool.  |

**Execution and identifiers**

```json
{
  "doc_id": "6af883e89030bff416447f91"
}
```

**Returned outputs / historical output names**

```json
{
  "outputs": [
    "inputs/prodigy/T001-C004/prodigy.csv"
  ]
}
```

**Validation and checks**

```json
"Success"
```

### C22: Prodigy

Purpose: flat-zip corrected submission T001-C005

Source: **boltzmann**; recorded state: **complete**.

Exact record: [tool_details.json](../inputs/execution_records/tool_details.json) → `/records/C22`. Original call ID: `S4-T001-C005`.

Identifier/version: `boltzmann Prodigy`.

**Inputs**

```json
{
  "input": "inputs/prodigy_flat/T001-C005_flat.zip"
}
```

**Parameters recorded for this call**

| Setting | Value / exact saved value | Recorded explanation |
| --- | --- | --- |
| `chain_list` | `[] automatic pairwise` | Field meaning: Chain grouping supplied to the interface/affinity tool.  |

**Execution and identifiers**

```json
{
  "doc_id": "6af883ea445ae94313c3bcee"
}
```

**Returned outputs / historical output names**

```json
{
  "outputs": [
    "inputs/prodigy/T001-C005/prodigy.csv"
  ]
}
```

**Validation and checks**

```json
"Success"
```

### C23: Prodigy

Purpose: flat-zip corrected submission T001-C006

Source: **boltzmann**; recorded state: **complete**.

Exact record: [tool_details.json](../inputs/execution_records/tool_details.json) → `/records/C23`. Original call ID: `S4-T001-C006`.

Identifier/version: `boltzmann Prodigy`.

**Inputs**

```json
{
  "input": "inputs/prodigy_flat/T001-C006_flat.zip"
}
```

**Parameters recorded for this call**

| Setting | Value / exact saved value | Recorded explanation |
| --- | --- | --- |
| `chain_list` | `[] automatic pairwise` | Field meaning: Chain grouping supplied to the interface/affinity tool.  |

**Execution and identifiers**

```json
{
  "doc_id": "6af883eb9850a93adf67d541"
}
```

**Returned outputs / historical output names**

```json
{
  "outputs": [
    "inputs/prodigy/T001-C006/prodigy.csv"
  ]
}
```

**Validation and checks**

```json
"Success"
```

### C24: Prodigy

Purpose: flat-zip corrected submission T001-C007

Source: **boltzmann**; recorded state: **complete**.

Exact record: [tool_details.json](../inputs/execution_records/tool_details.json) → `/records/C24`. Original call ID: `S4-T001-C007`.

Identifier/version: `boltzmann Prodigy`.

**Inputs**

```json
{
  "input": "inputs/prodigy_flat/T001-C007_flat.zip"
}
```

**Parameters recorded for this call**

| Setting | Value / exact saved value | Recorded explanation |
| --- | --- | --- |
| `chain_list` | `[] automatic pairwise` | Field meaning: Chain grouping supplied to the interface/affinity tool.  |

**Execution and identifiers**

```json
{
  "doc_id": "6af883eed29658acc304e8a3"
}
```

**Returned outputs / historical output names**

```json
{
  "outputs": [
    "inputs/prodigy/T001-C007/prodigy.csv"
  ]
}
```

**Validation and checks**

```json
"Success"
```

### C25: Prodigy

Purpose: flat-zip corrected submission T001-C008

Source: **boltzmann**; recorded state: **complete**.

Exact record: [tool_details.json](../inputs/execution_records/tool_details.json) → `/records/C25`. Original call ID: `S4-T001-C008`.

Identifier/version: `boltzmann Prodigy`.

**Inputs**

```json
{
  "input": "inputs/prodigy_flat/T001-C008_flat.zip"
}
```

**Parameters recorded for this call**

| Setting | Value / exact saved value | Recorded explanation |
| --- | --- | --- |
| `chain_list` | `[] automatic pairwise` | Field meaning: Chain grouping supplied to the interface/affinity tool.  |

**Execution and identifiers**

```json
{
  "doc_id": "6af883ef239a6b9f38bec13b"
}
```

**Returned outputs / historical output names**

```json
{
  "outputs": [
    "inputs/prodigy/T001-C008/prodigy.csv"
  ]
}
```

**Validation and checks**

```json
"Success"
```

## S5_evaluation: consolidated metrics + artifacts

State: **complete**. Dependencies: `["S4_affinity"]`.

Acceptance/checks: monoclonal.md section-6 artifact set complete

### C26: stage4_extract_confidence.py

Purpose: Boltz2 confidence extraction

Source: **open_source**; recorded state: **complete**.

Exact record: [tool_details.json](../inputs/execution_records/tool_details.json) → `/records/C26`. Original call ID: `S5-1`.

Identifier/version: `local python3`.

**Inputs**

```json
{
  "inputs": "inputs/boltz2_reference/outputs.zip + inputs/boltz2_candidates/*/outputs.zip"
}
```


**Execution and identifiers**

```json
{
  "command": "python3 code/stage4_extract_confidence.py"
}
```

**Returned outputs / historical output names**

```json
{
  "outputs": [
    "raw/boltz2_confidence.{json,csv}"
  ]
}
```

### C27: stage6_evaluate.py

Purpose: Prodigy dG/Kd + epitope recovery + CDR pLDDT

Source: **open_source**; recorded state: **complete**.

Exact record: [tool_details.json](../inputs/execution_records/tool_details.json) → `/records/C27`. Original call ID: `S5-2`.

Identifier/version: `local python3`.

**Inputs**

```json
{
  "inputs": "prodigy CSVs + plddt npz + crystal_contacts.csv"
}
```

**Parameters recorded for this call**

| Setting | Value / exact saved value | Recorded explanation |
| --- | --- | --- |
| `RT` | `0.0019872041 kcal/mol/K` | Field meaning: Recorded gas-constant/temperature factor used by the analysis.  |
| `T` | `298.15 K` | Field meaning: Temperature setting; use the saved implementation for units.  |
| `epitope` | `1N8Z HER2 crystal contacts (16 residues 532-603)` | Field meaning: Recorded residue set used in the analysis.  |

**Execution and identifiers**

```json
{
  "command": "python3 code/stage6_evaluate.py"
}
```

**Returned outputs / historical output names**

```json
{
  "outputs": [
    "raw/evaluation.{csv,json}"
  ]
}
```

**Validation and checks**

```json
"9 rows x 20 cols"
```

### C28: clash scan

Purpose: interface heavy-atom clashes <2.2 A

Source: **open_source**; recorded state: **complete**.

Exact record: [tool_details.json](../inputs/execution_records/tool_details.json) → `/records/C28`. Original call ID: `S5-3`.

Identifier/version: `local python3 (inline)`.

**Inputs**

```json
{
  "inputs": "pdbs_outputs.zip members"
}
```

**Parameters recorded for this call**

| Setting | Value / exact saved value | Recorded explanation |
| --- | --- | --- |
| `cutoff` | `2.2 A heavy-atom pairs` | Field meaning: Distance/check threshold; units and comparison are defined by the saved script.  |

**Returned outputs / historical output names**

```json
{
  "outputs": [
    "raw/clash_counts.json"
  ]
}
```

**Validation and checks**

```json
"0-3 per construct"
```

### C29: stage7_artifacts.py

Purpose: candidates/shortlist/fasta/metrics/benchmark/report build

Source: **open_source**; recorded state: **complete**.

Exact record: [tool_details.json](../inputs/execution_records/tool_details.json) → `/records/C29`. Original call ID: `S5-4`.

Identifier/version: `local python3`.

**Inputs**

```json
{
  "inputs": "candidates.json + evaluation.json + confidences + clashes"
}
```

**Parameters recorded for this call**

| Setting | Value / exact saved value | Recorded explanation |
| --- | --- | --- |
| `rank_key` | `mean Prodigy dG -> ipTM rec2 -> fewer mutations (pre-stated)` | Field meaning: Recorded sort key used for ranking.  |

**Execution and identifiers**

```json
{
  "command": "python code/stage7_artifacts.py"
}
```

**Returned outputs / historical output names**

```json
{
  "outputs": [
    "candidates.csv (38)",
    "shortlist.csv (8)",
    "sequences.fasta (78)",
    "metrics.csv (81 rows)",
    "benchmark_comparison.csv",
    "report.md"
  ]
}
```

**Validation and checks**

```json
"verified counts"
```
