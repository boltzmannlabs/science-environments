# Execution summary — run_003_antibmpnn_native_backbone

Task: `task_004_lcat_reference_fab_cdrh3_reconstruction`. Saved run status: **completed**.

Record organization updated 2026-11-16. This is a retrospective presentation of saved execution evidence.

[Compact config](../../../../results/task_004_lcat_reference_fab_cdrh3_reconstruction/run_003_antibmpnn_native_backbone/run.json) · [Workflow](../workflow.md) · [Activity log](agent_scientist_log.md) · [Exact original config](../inputs/execution_records/full_config.json) · [Tool details](../inputs/execution_records/tool_details.json) · [File inventory and SHA-256](../inputs/execution_records/run_files.csv)

## Preparation and inputs

Objective: Fixed-backbone CDR-H3 sequence design via Boltzmann AntiBMPNN

Original input provenance, chain/mask contracts and readiness records are retained below. Current file locations, sizes and full SHA-256 values are in `../inputs/execution_records/run_files.csv`.

```json
{
  "antibmpnn_input_5bv7_seq.pdb": {
    "sha256": "e5333129601dad3ea4fdca4411d82a4923cb0ea3499b2da95684b9b75b1ccd22",
    "provenance": "authors 5bv7.pdb with H3 GLY-masked (backbone-only) + sequential renumbering; uploaded to Boltzmann (receipt 6632033784ec47cda454eaed4007f31a, s3 users/680f678c1b1d883c92aa706c/1794671791622/)"
  },
  "antibmpnn_input_5bv7_h3gly.pdb": {
    "sha256": "afa6d82e052d4de8fc4dbf899a90484426458d4624715e9c9081bdf39ba25231",
    "provenance": "pre-renumbering variant (first failed submission)"
  },
  "antibmpnn_results.zip": {
    "sha256": "e3929c995ece433e2374294d4350808089a18e9a4bc78ec6acea835a1eca308e",
    "provenance": "Boltzmann job 6af884b7239a6b9f38bec1e5 output (32 sequences + raw FASTA + metrics)"
  }
}
```

## Recorded outcome

```json
{
  "last_update": "2026-11-14T16:20:00Z",
  "counts": {
    "candidates_generated": 32,
    "candidates_evaluated": 32,
    "unique_h3": 32,
    "native_copies": 0
  }
}
```

## Workflow steps and tools

Settings shown below are recorded values. Exact submitted arguments, payloads, resources, responses, validation and fallback details remain in `../inputs/execution_records/tool_details.json`. Historical output names are retained as evidence; use `run_files.csv` for current saved locations.

## historical_stage_1: input preparation

State: **completed**. Dependencies: `null`.

### C01: local python

Purpose: GLY mask + sequential renumber

Source: **open_source**; recorded state: **completed**.

Exact record: [tool_details.json](../inputs/execution_records/tool_details.json) → `/records/C01`. Original call ID: `a0`.

Identifier/version: `AntiBMPNN`.

**Inputs**

```json
{
  "saved_request": "src/task_004_lcat_reference_fab_cdrh3_reconstruction/run_003_antibmpnn_native_backbone/inputs/submitted_requests/message_17956_subcall_0.json",
  "sha256": "d0683b97baad1c0ef7cf35300dbdfe0d8e27ed816358950a9a9fc4f8e2c0e99a"
}
```

**Parameters recorded for this call**

| Setting | Value / exact saved value | Recorded explanation |
| --- | --- | --- |
| `mask_h3_to` | `GLY` | withholds native H3 sequence identity while retaining backbone |
| `atoms_kept` | `["N", "CA", "C", "O"]` | backbone only for masked residues |
| `renumber` | `sequential 1-N per chain` | removes IMGT insertion codes the platform parser reads as unsupported residues |

**Execution and identifiers**

```json
{
  "executed_at": "2026-11-14T15:52Z",
  "exit": 0
}
```

**Returned outputs / historical output names**

```json
[
  "antibmpnn_input_5bv7_seq.pdb"
]
```

**Validation and checks**

```json
"19 GLY at 96-114; chains 377/109/126"
```

**Failures, retries and fallback**

```json
{
  "error": "first submission 6af882e5239a6b9f38bec0b4 failed: designed chain contains unsupported residues [\"-\"] (IMGT insertion codes)",
  "recovery": "sequential renumbering, same atoms and mask",
  "protocol_difference": "residue numbering only; coordinates and mask unchanged"
}
```

Original submission records: `C01.R01`. These are evidence for this call, not additional completed jobs.

### C01.R01: AntiBMPNN

Purpose: See the stage purpose.

Source: **boltzmann**; recorded state: **failed**.

Exact record: [tool_details.json](../inputs/execution_records/tool_details.json) → `/records/C01.R01`. Original call ID: `call_-7077311191260852909:subcall:0`.

Identifier/version: `AntiBMPNN`.

**Inputs**

```json
{
  "saved_request": "src/task_004_lcat_reference_fab_cdrh3_reconstruction/run_003_antibmpnn_native_backbone/inputs/submitted_requests/message_17956_subcall_0.json",
  "sha256": "d0683b97baad1c0ef7cf35300dbdfe0d8e27ed816358950a9a9fc4f8e2c0e99a"
}
```

**Parameters recorded for this call**

| Setting | Value / exact saved value | Recorded explanation |
| --- | --- | --- |
| `chains_to_design` | `["C"]` | Field meaning: Chains selected in the submitted design request.  |
| `generation_count` | `32` | Field meaning: Number of samples requested in that call.  |
| `input_path` | `users/680f678c1b1d883c92aa706c/1794671323049/antibmpnn_input_5bv7_h3gly.pdb` | Field meaning: Tool-specific input field; it may contain a file location or sequence payload.  |
| `residue_positions_to_design` | `{"C": "96-114"}` | Field meaning: Per-chain residue positions supplied in the exact request.  |

**Execution and identifiers**

```json
{
  "session_id": "20261114_110408_5c556e",
  "message_id": 17956,
  "tool_call_id": "call_-7077311191260852909",
  "subcall_index": 0,
  "timestamp_utc": "2026-11-14T15:48:53.325696+00:00",
  "doc_id": "6af882e5239a6b9f38bec0b4",
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

## historical_stage_2: AntiBMPNN design (Boltzmann)

State: **completed**. Dependencies: `null`.

### C02: AntiBMPNN

Purpose: fixed-backbone H3 sequence design

Source: **boltzmann**; recorded state: **completed**.

Exact record: [tool_details.json](../inputs/execution_records/tool_details.json) → `/records/C02`. Original call ID: `a1`.

Identifier/version: `AntiBMPNN`.

**Inputs**

```json
{
  "input_path": "uploaded antibmpnn_input_5bv7_seq.pdb (receipt 6632033784ec47cda454eaed4007f31a)",
  "upload_sha256": "e5333129601dad3ea4fdca4411d82a4923cb0ea3499b2da95684b9b75b1ccd22"
}
```

**Parameters recorded for this call**

| Setting | Value / exact saved value | Recorded explanation |
| --- | --- | --- |
| `chains_to_design` | `["C"]` | heavy chain C only |
| `residue_positions_to_design` | `{"C": "96-114"}` | 1-based 96-114 = the 19-res H3 mask (sequential numbering) |
| `generation_count` | `32` | 32 to match pool protocols |

**Execution and identifiers**

```json
{
  "submitted_at": "2026-11-14T15:56:38Z",
  "completed": "2026-11-14T15:58Z",
  "doc_id": "6af884b7239a6b9f38bec1e5",
  "status": "Success",
  "notes": "partial-validation approval on upload+submit (chain/position scientific suitability verified locally: chain C exists, 96-114 = H3); results zip downloaded via fresh signed URL after connector download 400"
}
```

**Recorded resources**

```json
{
  "node": "boltzmann7",
  "runtime_s": 98,
  "billing": "1 unit (rounded 2 min @ 20/hr)"
}
```

**Returned outputs / historical output names**

```json
[
  "antibmpnn_results.zip -> antibmpnn_out/ (results.csv 32 rows, raw FASTA, metrics, manifest, logs)"
]
```

**Validation and checks**

```json
"32 sequences; framework 95+114 identical, VL identical (after restoring domain-cropped terminal residue); 32 unique H3s; 0 native copies; diffs confined to H3"
```

Original submission records: `C02.R01`. These are evidence for this call, not additional completed jobs.

### C02.R01: AntiBMPNN

Purpose: See the stage purpose.

Source: **boltzmann**; recorded state: **Success**.

Exact record: [tool_details.json](../inputs/execution_records/tool_details.json) → `/records/C02.R01`. Original call ID: `call_-7077307789646756081:subcall:0`.

Identifier/version: `AntiBMPNN`.

**Inputs**

```json
{
  "saved_request": "src/task_004_lcat_reference_fab_cdrh3_reconstruction/run_003_antibmpnn_native_backbone/inputs/submitted_requests/message_18012_subcall_0.json",
  "sha256": "8a205f3ff73a71b4bdb0c3666fa62a0b40cd8d2dd4c90f82b85244710f25690d"
}
```

**Parameters recorded for this call**

| Setting | Value / exact saved value | Recorded explanation |
| --- | --- | --- |
| `chains_to_design` | `["C"]` | Field meaning: Chains selected in the submitted design request.  |
| `generation_count` | `32` | Field meaning: Number of samples requested in that call.  |
| `input_path` | `users/680f678c1b1d883c92aa706c/1794671791622/antibmpnn_input_5bv7_seq.pdb` | Field meaning: Tool-specific input field; it may contain a file location or sequence payload.  |
| `residue_positions_to_design` | `{"C": "96-114"}` | Field meaning: Per-chain residue positions supplied in the exact request.  |

**Execution and identifiers**

```json
{
  "session_id": "20261114_110408_5c556e",
  "message_id": 18012,
  "tool_call_id": "call_-7077307789646756081",
  "subcall_index": 0,
  "timestamp_utc": "2026-11-14T15:56:38.893454+00:00",
  "doc_id": "6af884b7239a6b9f38bec1e5",
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

## historical_stage_3: freeze

State: **completed**. Dependencies: `null`.

### C03: local python

Purpose: model-score-ascending freeze

Source: **open_source**; recorded state: **completed**.

Exact record: [tool_details.json](../inputs/execution_records/tool_details.json) → `/records/C03`. Original call ID: `a2`.

**Inputs**

```json
null
```

**Parameters recorded for this call**

| Setting | Value / exact saved value | Recorded explanation |
| --- | --- | --- |
| `ordering` | `model score asc, tie-break candidate_id` | lower score = higher model confidence (ProteinMPNN convention: negative log-prob related) |

**Execution and identifiers**

```json
{
  "executed_at": "2026-11-14T16:04Z",
  "exit": 0
}
```

**Returned outputs / historical output names**

```json
[
  "antibmpnn_prep.json (frozen)"
]
```

**Validation and checks**

```json
"32 entries with scores; PDB sha256 recorded"
```

## historical_stage_4: scoring

State: **completed**. Dependencies: `null`.

### C04: AbFlow evaluator

Purpose: score native-backbone models

Source: **open_source**; recorded state: **completed**.

Exact record: [tool_details.json](../inputs/execution_records/tool_details.json) → `/records/C04`. Original call ID: `a3`.

**Inputs**

```json
{
  "mod_pdbs": "32 native-backbone graft models",
  "ref": "sealed native",
  "chains": "C/B/[A]"
}
```

**Parameters recorded for this call**

| Setting | Value / exact saved value | Recorded explanation |
| --- | --- | --- |
| `cdr_type` | `['H3']` | authors' H3 path |

**Execution and identifiers**

```json
{
  "command": "PATH=<env>/bin:$PATH python score_runs23_final.py",
  "executed_at": "2026-11-14T16:07-16:10Z",
  "exit": 0
}
```

**Returned outputs / historical output names**

```json
[
  "scored_antibmpnn/metrics_per_candidate.json"
]
```

**Validation and checks**

```json
"n=32; AAR H3 mean 0.5526; rank-1 0.5789"
```

**Failures, retries and fallback**

```json
{
  "prior_call": "a3-attempt-1",
  "error": "same DockQ cwd artifact as run_002",
  "recovery": "same chdir fix + rescore",
  "protocol_difference": "none"
}
```

## historical_stage_5: packaging

State: **completed**. Dependencies: `null`.

### C05: local python

Purpose: results tree

Source: **open_source**; recorded state: **completed**.

Exact record: [tool_details.json](../inputs/execution_records/tool_details.json) → `/records/C05`. Original call ID: `a4`.

**Inputs**

```json
null
```

**Parameters recorded for this call**

| Setting | Value / exact saved value | Recorded explanation |
| --- | --- | --- |
| `per_run_tree` | `true` | §6 layout |

**Execution and identifiers**

```json
{
  "executed_at": "2026-11-14T16:20Z"
}
```

**Returned outputs / historical output names**

```json
[
  "results/task_004_lcat_reference_fab_cdrh3_reconstruction/run_003_antibmpnn_native_backbone/"
]
```

**Validation and checks**

```json
"complete"
```
