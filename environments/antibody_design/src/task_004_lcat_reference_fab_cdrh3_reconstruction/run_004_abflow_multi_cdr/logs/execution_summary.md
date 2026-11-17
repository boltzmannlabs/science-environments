# Execution summary — run_004_abflow_multi_cdr

Task: `task_004_lcat_reference_fab_cdrh3_reconstruction`. Saved run status: **completed**.

Record organization updated 2026-11-16. This is a retrospective presentation of saved execution evidence.

[Compact config](../../../../results/task_004_lcat_reference_fab_cdrh3_reconstruction/run_004_abflow_multi_cdr/run.json) · [Workflow](../workflow.md) · [Activity log](agent_scientist_log.md) · [Exact original config](../inputs/execution_records/full_config.json) · [Tool details](../inputs/execution_records/tool_details.json) · [File inventory and SHA-256](../inputs/execution_records/run_files.csv)

## Preparation and inputs

Objective: All-CDR sequence/structure co-design for 5bv7 as a declared separate evaluation track (paper Table 2 protocol)

Original input provenance, chain/mask contracts and readiness records are retained below. Current file locations, sizes and full SHA-256 values are in `../inputs/execution_records/run_files.csv`.

```json
{
  "masked_input_5bv7.json": {
    "path": "src/task_004_lcat_reference_fab_cdrh3_reconstruction/run_004_abflow_multi_cdr/inputs/masked_input_5bv7.json",
    "sha256": "18d76e2ad1c43514a8feb5bec9297f5ad60d2af80fc0b12ddf64b83b6549ce1c",
    "provenance": "authors test.json 5bv7 entry minus cdrh3_seq (same file as run_001 S1 output)"
  },
  "multi_cdr_design.ckpt": {
    "sha256": "ae5d78d583615b2c4c0d0a01081206c2fdf7121773e922d2575b973aa870eac4",
    "provenance": "HF wenda8759/AbFlow checkpoints/multi_cdr_design.ckpt (paper Table 2 model)"
  },
  "heldout_reference": {
    "path": "src/task_004_lcat_reference_fab_cdrh3_reconstruction/run_001_abflow_h3_reconstruction/inputs/heldout_reference_5bv7_dataset_entry.json",
    "sha256": "28487ca965dccfdbe4a46723c7bb92c52a4bec1f4109b93a18500efb01059d91",
    "provenance": "sealed reference shared with run_001"
  }
}
```

## Recorded outcome

```json
{
  "last_update": "2026-11-14T16:40:00Z",
  "counts": {
    "candidates_generated": 1,
    "candidates_evaluated": 1,
    "unique_h3": 1,
    "native_copies": 0
  }
}
```

## Workflow steps and tools

Settings shown below are recorded values. Exact submitted arguments, payloads, resources, responses, validation and fallback details remain in `../inputs/execution_records/tool_details.json`. Historical output names are retained as evidence; use `run_files.csv` for current saved locations.

## historical_stage_1: masking + reference sealing (inherited from run_001 S1)

State: **completed**. Dependencies: `null`.

### C01: build_run.py

Purpose: mask+seal (same artifacts reused)

Source: **open_source**; recorded state: **completed**.

Exact record: [tool_details.json](../inputs/execution_records/tool_details.json) → `/records/C01`. Original call ID: `mc1`.

**Inputs**

```json
{
  "test_set": "authors RAbD test.json 5bv7 entry (heavy C, light B, antigen [A], IMGT)"
}
```

**Parameters recorded for this call**

| Setting | Value / exact saved value | Recorded explanation |
| --- | --- | --- |
| `n_replicates` | `32` | replicate count for pool runs; this run uses the single-entry input |

**Execution and identifiers**

```json
{
  "command": "python build_run.py run_5bv7_abflow 32",
  "executed_at": "2026-11-14T11:17:00Z"
}
```

**Recorded resources**

```json
{
  "cpu": "workstation"
}
```

**Returned outputs / historical output names**

```json
[
  "input/test_5bv7.json",
  "reference/freeze_manifest.json"
]
```

**Validation and checks**

```json
"field-diff confirmed only cdrh3_seq removed"
```

## historical_stage_2: all-CDR generation

State: **completed**. Dependencies: `null`.

### C02: AbFlow

Purpose: all-CDR 1-shot co-design

Source: **open_source**; recorded state: **completed**.

Exact record: [tool_details.json](../inputs/execution_records/tool_details.json) → `/records/C02`. Original call ID: `mc2`.

Identifier/version: `multi_cdr_design.ckpt (HF wenda8759/AbFlow, sha256 ae5d78d583615b2c...)`.

**Inputs**

```json
{
  "test_set": "run_5bv7_abflow/input/test_5bv7.json (masked)",
  "surf_file": "AbFlow/all_data/RAbD/test_surf.pkl",
  "pep_file": "AbFlow/all_data/RAbD/test.pkl"
}
```

**Parameters recorded for this call**

| Setting | Value / exact saved value | Recorded explanation |
| --- | --- | --- |
| `seed` | `2023` | 2023 = authors generate.py default (setup_seed(2023)); explicit choice for reproducibility |
| `batch_size` | `1` | 1 = single-sample 1-shot protocol (paper Table 2 sampling convention, matches Table 1 1-shot) |
| `gpu` | `0` | RTX 3090 24GB, GPU 0 (free at run time) |
| `ckpt` | `AbFlow/checkpoints/multi_cdr_design.ckpt` | authors Table-2 all-CDR checkpoint; selected because it is the benchmark-referenced method for this track |

**Execution and identifiers**

```json
{
  "command": {
    "record": "C02",
    "pointer": "/execution/command",
    "summary": "296 characters; exact value in tool_details.json"
  },
  "executed_at": "2026-11-14T15:28:42Z",
  "exit": 0,
  "env": "conda abflow_benchmark"
}
```

**Recorded resources**

```json
{
  "gpu": "RTX 3090 24GB",
  "gpu_mem_approx": "~6 GB",
  "runtime": "~9 s"
}
```

**Returned outputs / historical output names**

```json
[
  "gen_mcdr_1shot/5bv7_h3_000.pdb",
  "gen_mcdr_1shot/candidates.csv",
  "gen_mcdr_1shot/generation_freeze.json"
]
```

**Validation and checks**

```json
"VH FW identity 106/107 outside H3; changes only in CDR positions (VH {51,98-114}, VL {28-31,49-51,88-96}); H3 len 19; no native copy"
```

## historical_stage_3: freeze before scoring

State: **completed**. Dependencies: `null`.

### C03: freeze_rankings.py

Purpose: pmets-asc freeze + hash verify

Source: **open_source**; recorded state: **completed**.

Exact record: [tool_details.json](../inputs/execution_records/tool_details.json) → `/records/C03`. Original call ID: `mc3`.

**Inputs**

```json
{
  "pool": "gen_mcdr_1shot"
}
```

**Parameters recorded for this call**

| Setting | Value / exact saved value | Recorded explanation |
| --- | --- | --- |
| `ordering` | `pmets asc, tie-break candidate_id` | pose-blind model confidence; frozen before any native metric exists |

**Execution and identifiers**

```json
{
  "command": "python freeze_rankings.py run_5bv7_abflow/gen_mcdr_1shot",
  "executed_at": "2026-11-14T15:29:33Z",
  "exit": 0
}
```

**Returned outputs / historical output names**

```json
[
  "shortlist_frozen.csv",
  "freeze_record.json"
]
```

**Validation and checks**

```json
"PDB sha256 verified against generation_freeze.json; protocol label corrected post-hoc in freeze_record.json (documentation only)"
```

## historical_stage_4: native-reference scoring

State: **completed**. Dependencies: `null`.

### C04: AbFlow evaluator

Purpose: recovery/structure/interface metrics vs sealed native

Source: **open_source**; recorded state: **completed**.

Exact record: [tool_details.json](../inputs/execution_records/tool_details.json) → `/records/C04`. Original call ID: `mc4`.

**Inputs**

```json
{
  "mod_pdb": "gen_mcdr_1shot/5bv7_h3_000.pdb",
  "ref_pdb": "reference/native_5bv7.pdb (sealed)",
  "chains": "H=C, L=B, A=[A]"
}
```

**Parameters recorded for this call**

| Setting | Value / exact saved value | Recorded explanation |
| --- | --- | --- |
| `cdr_type` | `['H3']` | evaluator's H3-scoring path (same as run_001); full-antibody metrics unaffected by this list; AAR H3 computed on positions 95-113 |

**Execution and identifiers**

```json
{
  "command": "PATH=<env>/bin:$PATH python score_candidates.py",
  "executed_at": "2026-11-14T15:31Z",
  "exit": 0
}
```

**Recorded resources**

```json
{
  "cpu": "workstation",
  "runtime_s": 4.9
}
```

**Returned outputs / historical output names**

```json
[
  "gen_mcdr_1shot/metrics_per_candidate.json"
]
```

**Validation and checks**

```json
"AAR H3 0.4211, CAAR 0.25, TM 0.9593, lDDT 0.7686, RMSD(AppC) 19.8398 A, DockQ 0.345"
```

### C05: AbFlow evaluator

Purpose: per-CDR Kabsch RMSDs for repo-benchmark Table-2 comparison

Source: **open_source**; recorded state: **completed**.

Exact record: [tool_details.json](../inputs/execution_records/tool_details.json) → `/records/C05`. Original call ID: `mc4b`.

**Inputs**

```json
{
  "mod_pdb": "gen_mcdr_1shot/5bv7_h3_000.pdb",
  "ref_pdb": "sealed native",
  "chains": "C/B/[A]"
}
```

**Parameters recorded for this call**

| Setting | Value / exact saved value | Recorded explanation |
| --- | --- | --- |
| `cdr_type` | `['H1','H2','H3','L1','L2','L3']` | evaluator emits per-CDR RMSD(CA) CDRx + aligned (Kabsch) pairs |

**Execution and identifiers**

```json
{
  "command": "cal_metrics([mod, ref, C, B, [A], [H1..L3]])",
  "executed_at": "2026-11-14T16:35Z",
  "exit": 0
}
```

**Returned outputs / historical output names**

```json
[
  "gen_mcdr_1shot/metrics_allcdrs.json"
]
```

**Validation and checks**

```json
"H1/H2 Kabsch 0.61/0.53 vs published 0.63/0.55 — definition confirmed"
```

## historical_stage_5: packaging

State: **completed**. Dependencies: `null`.

### C06: local python

Purpose: per-run tree + planning updates

Source: **open_source**; recorded state: **completed**.

Exact record: [tool_details.json](../inputs/execution_records/tool_details.json) → `/records/C06`. Original call ID: `mc5`.

**Inputs**

```json
null
```

**Parameters recorded for this call**

| Setting | Value / exact saved value | Recorded explanation |
| --- | --- | --- |
| `per_run_tree` | `true` | write full §6 results tree for this run |
| `planning_updates` | `true` | update all planning tables to 4 designed / 2 selected / 2 executed |

**Execution and identifiers**

```json
{
  "executed_at": "2026-11-14T15:40Z"
}
```

**Returned outputs / historical output names**

```json
[
  "results/task_004_lcat_reference_fab_cdrh3_reconstruction/run_004_abflow_multi_cdr/"
]
```

**Validation and checks**

```json
"all contract files present"
```
