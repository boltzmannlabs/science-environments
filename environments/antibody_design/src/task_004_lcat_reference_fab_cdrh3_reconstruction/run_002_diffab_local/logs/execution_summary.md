# Execution summary — run_002_diffab_local

Task: `task_004_lcat_reference_fab_cdrh3_reconstruction`. Saved run status: **completed**.

Record organization updated 2026-11-16. This is a retrospective presentation of saved execution evidence.

[Compact config](../../../../results/task_004_lcat_reference_fab_cdrh3_reconstruction/run_002_diffab_local/run.json) · [Workflow](../workflow.md) · [Activity log](agent_scientist_log.md) · [Exact original config](../inputs/execution_records/full_config.json) · [Tool details](../inputs/execution_records/tool_details.json) · [File inventory and SHA-256](../inputs/execution_records/run_files.csv)

## Preparation and inputs

Objective: DiffAb in-context CDR-H3 co-design comparator for 5bv7

Original input provenance, chain/mask contracts and readiness records are retained below. Current file locations, sizes and full SHA-256 values are in `../inputs/execution_records/run_files.csv`.

```json
{
  "native_5bv7_complex.pdb": {
    "sha256": "bfaa5a0e6993aa5405d1e825c7fe4ae0e3c74e8c06a4ed0e7e774d94c5fe1783",
    "provenance": "authors datasets.zip 5bv7.pdb (in-context protocol input)"
  },
  "info.txt": {
    "sha256": "4384bd9609231ff1563a4a668b14e1a5d09fd785238ed537bb73bb91893c38ca",
    "provenance": "H_CDR3 span locator (sequence locates the 19-res mask; runner contract)"
  },
  "lcat_h3_n32.yml": {
    "sha256": "e525ed6a298ac52be455b64c158decc9e08cc8f0383e368059f8574fcfafef1e",
    "provenance": "sampling config: codesign_single.pt, H_CDR3 only, n=32, seed 20261114"
  },
  "codesign_single.pt": {
    "sha256": "53d1c240020ce87c0d2a8f552accb41415106f1d26a8c8701076d76bde81a21e",
    "provenance": "DiffAb released single-CDR co-design checkpoint (local repo)"
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

## historical_stage_1: DiffAb in-context H3 generation

State: **completed**. Dependencies: `null`.

### C01: DiffAb

Purpose: H3 co-design, 32 samples

Source: **open_source**; recorded state: **completed**.

Exact record: [tool_details.json](../inputs/execution_records/tool_details.json) → `/records/C01`. Original call ID: `d1`.

Identifier/version: `DiffAb codesign_single.pt (sha256 53d1c240020ce87c...)`.

**Inputs**

```json
{
  "pdb": "native_5bv7_complex.pdb (native complex, in-context)",
  "cdr": "H_CDR3 (0-based 95-113, len 19)"
}
```

**Parameters recorded for this call**

| Setting | Value / exact saved value | Recorded explanation |
| --- | --- | --- |
| `seed` | `20261114` | run-date seed, distinct from AbFlow runs |
| `num_samples` | `32` | 32 to match AbFlow-G pool size |
| `sample_structure` | `true` | Field meaning: Whether structure sampling was requested.  |
| `sample_sequence` | `true` | Field meaning: Whether sequence sampling was requested.  |
| `cdrs` | `["H_CDR3"]` | H3 only — single-CDR track |

**Execution and identifiers**

```json
{
  "command": "PYTHONPATH=<repo> <diffab env>/bin/python run_diffab_exact_cdrs_from_input.py native_5bv7_complex.pdb --info-file info.txt --heavy C --light B --config lcat_h3_n32.yml --out_root out_h3_n32 --cdrs HCDR3 --label LCAT_H3",
  "executed_at": "2026-11-14T15:48:27Z",
  "exit": 0,
  "env": "conda diffab"
}
```

**Recorded resources**

```json
{
  "gpu": "RTX 3090 24GB",
  "runtime_s": 55
}
```

**Returned outputs / historical output names**

```json
[
  "out_h3_n32/... 32 candidate PDBs"
]
```

**Validation and checks**

```json
"32/32 candidates; H3 length 19 conserved; 32 unique H3 sequences; 0 native copies; framework byte-identical (in-context)"
```

### C02: graft_diffab.py

Purpose: evaluator-compatible model build (Chothia->IMGT H3 transplant)

Source: **open_source**; recorded state: **completed**.

Exact record: [tool_details.json](../inputs/execution_records/tool_details.json) → `/records/C02`. Original call ID: `d1b`.

**Inputs**

```json
{
  "candidates": "32 DiffAb PDBs",
  "scaffold": "native IMGT complex"
}
```

**Parameters recorded for this call**

| Setting | Value / exact saved value | Recorded explanation |
| --- | --- | --- |
| `renumber` | `H3 block -> native IMGT keys, 1:1 by sequence position` | position 1:1; no residue insertion/deletion; framework untouched |

**Execution and identifiers**

```json
{
  "command": "python graft_diffab.py",
  "executed_at": "2026-11-14T16:05Z",
  "exit": 0
}
```

**Returned outputs / historical output names**

```json
[
  "gen_diffab_grafted/ (32 models)"
]
```

**Validation and checks**

```json
"Bio.PDB parse OK; chains A/C/B 377/126/109; first attempt had icode column bug — fixed and regrafted (all 32)"
```

**Failures, retries and fallback**

```json
{
  "prior_call": "d1",
  "error": "first graft wrote insertion codes into wrong PDB columns -> Bio.PDB parse failure",
  "recovery": "column-correct regraft of all 32",
  "protocol_difference": "none — numbering layout only"
}
```

## historical_stage_2: freeze ranking

State: **completed**. Dependencies: `null`.

### C03: local python

Purpose: filename-order freeze (deterministic sampling order)

Source: **open_source**; recorded state: **completed**.

Exact record: [tool_details.json](../inputs/execution_records/tool_details.json) → `/records/C03`. Original call ID: `d2`.

**Inputs**

```json
null
```

**Parameters recorded for this call**

| Setting | Value / exact saved value | Recorded explanation |
| --- | --- | --- |
| `ordering` | `filename (sampling) order` | seeded sampling order is deterministic; no score-based reordering possible pre-scoring |

**Execution and identifiers**

```json
{
  "executed_at": "2026-11-14T16:07Z",
  "exit": 0
}
```

**Returned outputs / historical output names**

```json
[
  "diffab_frozen_shortlist.json"
]
```

**Validation and checks**

```json
"32 entries, PDB sha256 recorded"
```

## historical_stage_3: scoring

State: **completed**. Dependencies: `null`.

### C04: AbFlow evaluator

Purpose: score vs sealed native

Source: **open_source**; recorded state: **completed**.

Exact record: [tool_details.json](../inputs/execution_records/tool_details.json) → `/records/C04`. Original call ID: `d3`.

**Inputs**

```json
{
  "mod_pdbs": "32 grafted models",
  "ref": "sealed native 5bv7",
  "chains": "C/B/[A]"
}
```

**Parameters recorded for this call**

| Setting | Value / exact saved value | Recorded explanation |
| --- | --- | --- |
| `cdr_type` | `['H3']` | authors' H3-scoring path |

**Execution and identifiers**

```json
{
  "command": "PATH=<env>/bin:$PATH python score_runs23_final.py",
  "executed_at": "2026-11-14T16:07-16:10Z",
  "exit": 0,
  "notes": "first attempt: DockQ silently 0 for all — evaluator shells ./DockQ/DockQ.py relative to repo; chdir fix; rescored all 64 (runs 2+3) — DockQ now populated"
}
```

**Recorded resources**

```json
{
  "cpu": "workstation",
  "runtime": "~5 s/candidate"
}
```

**Returned outputs / historical output names**

```json
[
  "scored_diffab/metrics_per_candidate.json"
]
```

**Validation and checks**

```json
"n=32; AAR H3 mean 0.2747; rank-1 0.2105"
```

**Failures, retries and fallback**

```json
{
  "prior_call": "d3-attempt-1",
  "error": "DockQ silently 0: evaluator shells ./DockQ/DockQ.py relative to repo; driver had not chdir-ed",
  "recovery": "chdir to repo; native-vs-native control (AAR 1.0/TM 1.0) then full rescore of all 64 candidates",
  "protocol_difference": "none — execution environment only"
}
```

## historical_stage_4: packaging

State: **completed**. Dependencies: `null`.

### C05: local python

Purpose: results tree

Source: **open_source**; recorded state: **completed**.

Exact record: [tool_details.json](../inputs/execution_records/tool_details.json) → `/records/C05`. Original call ID: `d4`.

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
  "results/task_004_lcat_reference_fab_cdrh3_reconstruction/run_002_diffab_local/"
]
```

**Validation and checks**

```json
"complete"
```
