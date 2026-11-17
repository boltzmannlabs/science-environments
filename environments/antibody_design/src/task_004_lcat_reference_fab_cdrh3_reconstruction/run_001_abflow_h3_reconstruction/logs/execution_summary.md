# Execution summary — run_001_abflow_h3_reconstruction

Task: `task_004_lcat_reference_fab_cdrh3_reconstruction`. Saved run status: **completed**.

Record organization updated 2026-11-16. This is a retrospective presentation of saved execution evidence.

[Compact config](../../../../results/task_004_lcat_reference_fab_cdrh3_reconstruction/run_001_abflow_h3_reconstruction/run.json) · [Workflow](../workflow.md) · [Activity log](agent_scientist_log.md) · [Exact original config](../inputs/execution_records/full_config.json) · [Tool details](../inputs/execution_records/tool_details.json) · [File inventory and SHA-256](../inputs/execution_records/run_files.csv)

## Preparation and inputs

Objective: Antigen-conditioned CDR-H3 sequence/structure reconstruction for 5BV7 under the AbFlow RAbD benchmark protocol

Original input provenance, chain/mask contracts and readiness records are retained below. Current file locations, sizes and full SHA-256 values are in `../inputs/execution_records/run_files.csv`.

```json
{
  "masked_input_5bv7.json": {
    "path": "src/task_004_lcat_reference_fab_cdrh3_reconstruction/run_001_abflow_h3_reconstruction/inputs/masked_input_5bv7.json",
    "sha256": "18d76e2ad1c43514a8feb5bec9297f5ad60d2af80fc0b12ddf64b83b6549ce1c",
    "provenance": "authors test.json 5bv7 entry with cdrh3_seq field removed and absolute pdb_data_path"
  },
  "masked_input_5bv7_x32.json": {
    "sha256": "2b4a1c149a58a86e6f36a5227f66a33fe158457d79ecd80acf8e5c8e19ce348e",
    "provenance": "32-fold replication of the masked entry for batched sampling"
  },
  "heldout_reference_5bv7_dataset_entry.json": {
    "sha256": "28487ca965dccfdbe4a46723c7bb92c52a4bec1f4109b93a18500efb01059d91",
    "provenance": "unmodified authors test.json 5bv7 entry (incl. native cdrh3_seq); sealed until freeze"
  },
  "heldout_reference_5bv7_imgt.pdb": {
    "sha256": "bfaa5a0e6993aa5405d1e825c7fe4ae0e3c74e8c06a4ed0e7e774d94c5fe1783",
    "provenance": "authors IMGT-numbered 5bv7.pdb from datasets.zip"
  },
  "checkpoint": {
    "sha256": "fcc614dc357d19e5b5709f22ed4fc8831241722e76e8600389d58c89a5927105",
    "provenance": "HF wenda8759/AbFlow checkpoints/paratope_centric_design.ckpt"
  },
  "test_surf.pkl": {
    "sha256": "885bd474d5e8b564c8a4d62b2b56f4d1ebea7f098f930c8afba5850f5f8d15d0",
    "provenance": "authors released RAbD surface features"
  },
  "test.pkl": {
    "sha256": "1cec73239a8e4c23e0cbdb02a918482cae0a256e8a2a41dae7458a24be315e72",
    "provenance": "authors released RAbD pep file (5bv7 key: 19-res epitope-peptide conditioning X/S)"
  }
}
```

## Recorded outcome

```json
{
  "last_update": "2026-11-14T15:45:00Z",
  "counts": {
    "designed_workflows": 4,
    "selected": 1,
    "executed": 1,
    "candidates_generated": 65,
    "candidates_evaluated": 33,
    "unique_h3_sequences": 4,
    "native_copies": 0,
    "selected_workflows": 2,
    "executed_workflows": 2
  }
}
```

## Workflow steps and tools

Settings shown below are recorded values. Exact submitted arguments, payloads, resources, responses, validation and fallback details remain in `../inputs/execution_records/tool_details.json`. Historical output names are retained as evidence; use `run_files.csv` for current saved locations.

## historical_stage_1: input masking + reference sealing

State: **completed**. Dependencies: `null`.

### C01: build_run.py

Purpose: mask + seal + manifest

Source: **open_source**; recorded state: **completed**.

Exact record: [tool_details.json](../inputs/execution_records/tool_details.json) → `/records/C01`. Original call ID: `c1`.

**Inputs**

```json
{
  "test_set": "authors RAbD test.json 5bv7 entry (heavy C, light B, antigen [A], IMGT-numbered, cdrh3_seq present)"
}
```

**Parameters recorded for this call**

| Setting | Value / exact saved value | Recorded explanation |
| --- | --- | --- |
| `n_replicates` | `32` | 32 replicate entries under distinct pdb ids for batched sampling (pool protocol uses 30+ draws) |
| `output_dir` | `run_5bv7_abflow` | Field meaning: Output directory requested by the saved command.  |

**Execution and identifiers**

```json
{
  "command": "python build_run.py run_5bv7_abflow 32",
  "executed_at": "2026-11-14T11:17:00Z",
  "exit": 0
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
  "input/test_5bv7_xN.json",
  "reference/*"
]
```

**Validation and checks**

```json
"masked entry field-diff vs native entry: only cdrh3_seq removed + note added"
```

## historical_stage_2: CDR-H3 co-design generation

State: **completed**. Dependencies: `null`.

### C02: AbFlow

Purpose: pilot 32-draw pool (smoke)

Source: **open_source**; recorded state: **completed**.

Exact record: [tool_details.json](../inputs/execution_records/tool_details.json) → `/records/C02`. Original call ID: `c2`.

**Inputs**

```json
{
  "test_set": "input/test_5bv7_xN.json (masked, 32 entries)",
  "surf_file": "AbFlow/all_data/RAbD/test_surf.pkl",
  "pep_file": "AbFlow/all_data/RAbD/test.pkl"
}
```

**Parameters recorded for this call**

| Setting | Value / exact saved value | Recorded explanation |
| --- | --- | --- |
| `seed` | `2023` | 2023 = authors generate.py default |
| `batch_size` | `8` | 8 fits 24GB VRAM conservatively |
| `gpu` | `0` | RTX 3090 GPU 0 free at run time |

**Execution and identifiers**

```json
{
  "command": "python generate_candidates.py --seed 2023 --batch-size 8 ...",
  "executed_at": "2026-11-14T11:19-11:22Z",
  "exit": 0
}
```

**Recorded resources**

```json
{
  "gpu": "RTX 3090 24GB",
  "runtime": "~192 s for 32 draws"
}
```

**Returned outputs / historical output names**

```json
[
  "gen_smoke/candidates.csv (32)"
]
```

**Validation and checks**

```json
"4 unique H3 modes, 0 native copies, framework preserved"
```

### C03: AbFlow

Purpose: 1-shot (paper Table 1 protocol)

Source: **open_source**; recorded state: **completed**.

Exact record: [tool_details.json](../inputs/execution_records/tool_details.json) → `/records/C03`. Original call ID: `c3`.

**Inputs**

```json
{
  "test_set": "input/test_5bv7.json (single masked entry)"
}
```

**Parameters recorded for this call**

| Setting | Value / exact saved value | Recorded explanation |
| --- | --- | --- |
| `seed` | `2023` | Field meaning: Random seed recorded for reproducibility.  |
| `batch_size` | `1` | 1 = paper Table 1 one-shot sampling protocol |

**Execution and identifiers**

```json
{
  "command": "python generate_candidates.py --seed 2023 --batch-size 1 ...",
  "executed_at": "2026-11-14T11:23:47-11:23:56Z",
  "exit": 0
}
```

**Recorded resources**

```json
{
  "gpu": "RTX 3090 24GB",
  "runtime": "~9 s"
}
```

**Returned outputs / historical output names**

```json
[
  "gen_1shot/candidates.csv (1)"
]
```

**Validation and checks**

```json
"same protocol as authors generate.py setup_seed(2023); batch 1"
```

### C04: AbFlow

Purpose: AbFlow-G multi-sample pool, first attempt

Source: **open_source**; recorded state: **completed_with_defect**.

Exact record: [tool_details.json](../inputs/execution_records/tool_details.json) → `/records/C04`. Original call ID: `c4`.

**Inputs**

```json
{
  "test_set": "input/test_5bv7_xN.json (32 entries)"
}
```

**Parameters recorded for this call**

| Setting | Value / exact saved value | Recorded explanation |
| --- | --- | --- |
| `seed` | `20261114` | 20261114 = run-date seed for the independent AbFlow-G pool |
| `batch_size` | `8` | Field meaning: Items processed in one batch.  |

**Execution and identifiers**

```json
{
  "command": "python generate_candidates.py --seed 20261114 --batch-size 8 ...",
  "executed_at": "2026-11-14T11:26-11:27Z",
  "exit": 0
}
```

**Recorded resources**

```json
{
  "gpu": "RTX 3090 24GB",
  "runtime": "~200 s"
}
```

**Returned outputs / historical output names**

```json
[
  "gen_g30_prev (32)"
]
```

**Validation and checks**

```json
"FAILED RANKING CAPTURE: pmets indexed per global candidate id but model.sample returns one pmets value per batch item; candidates 9-32 blank"
```

**Failures, retries and fallback**

```json
{
  "prior_call": "c4",
  "error": "pmets list length = batch size (8), indexed with global idx up to 31",
  "recovery": "fix indexing to per-batch position, regenerate same seed",
  "protocol_difference": "sequences unchanged (32/32 identical on regeneration); coordinates differ by GPU float noise only; ranking now complete"
}
```

### C05: AbFlow

Purpose: AbFlow-G pool regeneration (fixed pmets capture)

Source: **open_source**; recorded state: **completed**.

Exact record: [tool_details.json](../inputs/execution_records/tool_details.json) → `/records/C05`. Original call ID: `c5`.

**Inputs**

```json
{
  "test_set": "input/test_5bv7_xN.json (32 entries)"
}
```

**Parameters recorded for this call**

| Setting | Value / exact saved value | Recorded explanation |
| --- | --- | --- |
| `seed` | `20261114` | same seed as c4 to isolate the code fix from sampling variation |
| `batch_size` | `8` | Field meaning: Items processed in one batch.  |

**Execution and identifiers**

```json
{
  "command": "python generate_candidates.py --seed 20261114 --batch-size 8 ...",
  "executed_at": "2026-11-14T15:03Z",
  "exit": 0,
  "determinism_check": "32/32 sequences identical to c4; coordinates differ only by GPU float noise"
}
```

**Recorded resources**

```json
{
  "gpu": "RTX 3090 24GB",
  "runtime": "~200 s"
}
```

**Returned outputs / historical output names**

```json
[
  "gen_g30/candidates.csv (32, complete pmets)"
]
```

**Validation and checks**

```json
"determinism check vs c4: 32/32 sequence-identical; 0 bad pmets"
```

## historical_stage_3: freeze rankings before native scoring

State: **completed**. Dependencies: `null`.

### C06: freeze_rankings.py

Purpose: pmets-asc frozen ordering + hash check

Source: **open_source**; recorded state: **completed**.

Exact record: [tool_details.json](../inputs/execution_records/tool_details.json) → `/records/C06`. Original call ID: `c6`.

**Inputs**

```json
{
  "pools": [
    "gen_1shot",
    "gen_g30"
  ]
}
```

**Parameters recorded for this call**

| Setting | Value / exact saved value | Recorded explanation |
| --- | --- | --- |
| `ordering` | `pmets asc; tie-break candidate_id asc` | pose-blind model confidence (mean NLL over H3); frozen before any native metric exists |

**Execution and identifiers**

```json
{
  "command": "python freeze_rankings.py",
  "executed_at": "2026-11-14T11:27:55Z / 15:03:38Z (after regeneration)",
  "exit": 0
}
```

**Returned outputs / historical output names**

```json
[
  "shortlist_frozen.csv x2",
  "freeze_record.json x2"
]
```

**Validation and checks**

```json
"hash_check all-verified both times"
```

## historical_stage_4: native-reference evaluation

State: **completed**. Dependencies: `null`.

### C07: AbFlow evaluator

Purpose: first scoring attempt

Source: **open_source**; recorded state: **failed**.

Exact record: [tool_details.json](../inputs/execution_records/tool_details.json) → `/records/C07`. Original call ID: `c7`.

**Inputs**

```json
{
  "mod_pdb": "candidate PDBs",
  "ref_pdb": "reference/native_5bv7.pdb",
  "chains": "H=C, L=B, A=[A]"
}
```

**Parameters recorded for this call**

| Setting | Value / exact saved value | Recorded explanation |
| --- | --- | --- |
| `cdr_type` | `['H3']` | authors' H3-scoring path; AAR H3 on positions 95-113 |

**Execution and identifiers**

```json
{
  "command": "python score_candidates.py",
  "executed_at": "2026-11-14T11:24Z",
  "exit": "non-zero",
  "error": "lddt binary not found (sh: lddt: not found)"
}
```

**Validation and checks**

```json
"FAILED: lddt binary not found (sh: lddt: not found)"
```

**Failures, retries and fallback**

```json
{
  "prior_call": "c7",
  "error": "lddt not on PATH for the conda env used by os.system inside evaluation/lddt.py",
  "recovery": "export PATH=/home/boltzmann10/anaconda3/envs/abflow_benchmark/bin:$PATH",
  "protocol_difference": "none - same binaries, PATH only"
}
```

### C08: AbFlow evaluator

Purpose: full scoring (1-shot + pool)

Source: **open_source**; recorded state: **completed**.

Exact record: [tool_details.json](../inputs/execution_records/tool_details.json) → `/records/C08`. Original call ID: `c8`.

**Inputs**

```json
{
  "mod_pdb": "candidate PDBs (33)",
  "ref_pdb": "reference/native_5bv7.pdb (sealed until freeze)",
  "chains": "H=C, L=B, A=[A]"
}
```

**Parameters recorded for this call**

| Setting | Value / exact saved value | Recorded explanation |
| --- | --- | --- |
| `cdr_type` | `['H3']` | authors' H3-scoring path |
| `PATH_prefix` | `/home/boltzmann10/anaconda3/envs/abflow_benchmark/bin` | lddt binary lives in the conda env bin, not on default PATH |

**Execution and identifiers**

```json
{
  "command": "PATH=<env>/bin:$PATH python score_candidates.py",
  "executed_at": "2026-11-14T11:25-11:27Z / 15:03-15:06Z",
  "exit": 0
}
```

**Recorded resources**

```json
{
  "cpu": "workstation, ~5 s/candidate"
}
```

**Returned outputs / historical output names**

```json
[
  "metrics_per_candidate.json x2 (1+32)",
  "metrics_summary.json"
]
```

**Validation and checks**

```json
"1-shot AAR 0.5263 / CAAR 0.3333 / TM 0.9648 / lDDT 0.8105 / RMSD(AppendixC) 14.472 A / DockQ 0.889; pool stats consistent"
```

## historical_stage_5: packaging + benchmark comparison

State: **completed**. Dependencies: `null`.

### C09: package_results.py

Purpose: bundle + CHECKSUMS + repo results tree

Source: **open_source**; recorded state: **completed**.

Exact record: [tool_details.json](../inputs/execution_records/tool_details.json) → `/records/C09`. Original call ID: `c9`.

**Inputs**

```json
null
```

**Parameters recorded for this call**

| Setting | Value / exact saved value | Recorded explanation |
| --- | --- | --- |
| `include_diagnostics` | `false` | smoke/prev pools excluded from the deliverable bundle (retained in workspace) |
| `bundles` | `["lcat_results"]` | task-md bundle layout |

**Execution and identifiers**

```json
{
  "command": "python package_results.py",
  "executed_at": "2026-11-14T15:07Z",
  "exit": 0
}
```

**Returned outputs / historical output names**

```json
[
  "results/.../lcat_results/ (52 files verified)",
  "results/.../run_001_abflow_h3_reconstruction/"
]
```

**Validation and checks**

```json
"CHECKSUMS.sha256 verified 52/52"
```
