# Execution summary — run_002_igdesign_codesign

Task: `task_005_gal3bp_glycan_aware_interface_refinement`. Saved run status: **completed**.

Record organization updated 2026-11-16. This is a retrospective presentation of saved execution evidence.

[Compact config](../../../../results/task_005_gal3bp_glycan_aware_interface_refinement/run_002_igdesign_codesign/run.json) · [Workflow](../workflow.md) · [Activity log](agent_scientist_log.md) · [Exact original config](../inputs/execution_records/full_config.json) · [Tool details](../inputs/execution_records/tool_details.json) · [File inventory and SHA-256](../inputs/execution_records/run_files.csv)

## Preparation and inputs

Objective: glycan-aware interface refinement of BDBV-43-derived candidates on Gal-3BP E1-window; second design engine (antigen-conditioned LM codesign) beyond fixed-backbone AntiBMPNN

Original input provenance, chain/mask contracts and readiness records are retained below. Current file locations, sizes and full SHA-256 values are in `../inputs/execution_records/run_files.csv`.

```json
[
  {
    "path": "inputs/igdesign_input_complex.pdb",
    "provenance": "run run_001_antibmpnn_interface_refinement W1 AFM rank_001 (doc 6af879cf9de6b44b075d7f4c) + 3-letter SEQRES added",
    "sha256": "627a4180839a182be6917a3afd5e11228d526983cc58599d59e00cb80c8651ad",
    "validation": "igdesign PDBParserAnnotator parse OK; chains A 122 / B 106 / C 567; A byte==reference VH"
  },
  {
    "path": "inputs/hcdr123_gal3bp.yaml",
    "provenance": "this run",
    "sha256": "bcb931c2ec44a46fdcfa9b78cd4b9d874c6f12c0bc60c923956ce1a6c50b3e06",
    "validation": "positions 0-based verified vs igdesign annotate_chain on full VH (no truncation)"
  },
  {
    "path": "inputs/igdesign_cdr_positions.json",
    "provenance": "igdesign structure_analysis.annotate_chain",
    "sha256": "851faa225cd8bdb7ad926d5c9c0ce57ec2655eeb934cc639507259d6a9742587"
  },
  {
    "path": "inputs/ref_sequences.fasta",
    "provenance": "PDB 7KEW BDBV-43 Fv",
    "sha256": "2a67bc15718f6815030d1e658280a05f0c0b95fac4f01546d4648e5f8ca9ef98"
  },
  {
    "path": "code/run_igdesign_mmap.py",
    "provenance": "copied from task_017 validated wrapper (skill igdesign-memory-safe-inference)",
    "sha256": "54adb4432aaec335e37c87335ce7ee46195a5ba33406cb9394eff8e1c1693831"
  }
]
```

## Recorded outcome

```json
{
  "status": "completed",
  "counts": {
    "generated_samples": 100,
    "retained_candidates": 97,
    "evaluated_candidates": 3,
    "shortlist": 3
  },
  "evidence": [
    "results/task_005_gal3bp_glycan_aware_interface_refinement/run_002_igdesign_codesign/report.md",
    "results/task_005_gal3bp_glycan_aware_interface_refinement/run_002_igdesign_codesign/metrics.csv",
    "src/task_005_gal3bp_glycan_aware_interface_refinement/run_002_igdesign_codesign/inputs/job_registry.json"
  ],
  "status_reconciled_utc": "2026-11-16T05:06:52+00:00",
  "scope": "Execution and saved computational artifacts complete; scientific interpretation remains in report.md."
}
```

## Workflow steps and tools

Settings shown below are recorded values. Exact submitted arguments, payloads, resources, responses, validation and fallback details remain in `../inputs/execution_records/tool_details.json`. Historical output names are retained as evidence; use `run_files.csv` for current saved locations.

## S1_generation: Local IgDesign generation

State: **completed**. Dependencies: `[]`.

Acceptance/checks: Recorded sequence checks and saved per-run evaluation artifacts; see report.md.

Saved stage evidence:

```json
[
  "src/task_005_gal3bp_glycan_aware_interface_refinement/run_002_igdesign_codesign/inputs/igdesign_run002_results.csv",
  "src/task_005_gal3bp_glycan_aware_interface_refinement/run_002_igdesign_codesign/inputs/igdesign_run002_candidates.json"
]
```

This stage is documented through saved artifacts rather than a normalized call record. The files above are the execution evidence; no command, timestamp or default has been inferred.

Exact saved local configuration:

```yaml
# IgDesign config: task_005 run_002 heavy-CDR123 codesign on BDBV-43/Gal-3BP reference complex
structure_path: "/home/boltzmann10/new_agent_scienece_env/science-environments/environments/antibody_design/src/task_005_gal3bp_glycan_aware_interface_refinement/run_002_igdesign_codesign/inputs/igdesign_input_complex.pdb"
lmdesign_checkpoint: "/home/boltzmann10/agent_sci_boltpro_errors_tools/igdesign/ckpts/igdesign_acvr2b_holdout.ckpt"
pmpnn_checkpoint: "/home/boltzmann10/agent_sci_boltpro_errors_tools/igdesign/ckpts/igmpnn_acvr2b_holdout.ckpt"
save_path: "/home/boltzmann10/.sci/cache/scratch/gal3bp_run/igdesign_run002_results.csv"

region_order: ["hcdr1", "hcdr2", "hcdr3"]

lmdesign_num_decoding_orders: 10
lmdesign_num_pmpnn_seqs: 10
lmdesign_num_lm_seqs: 1  # 100 samples
lmdesign_pmpnn_logit_temperature: 0.5
lmdesign_output_logit_temperature: 0.5

independent_loss: true
condition_on_light_chain: true
condition_on_antigen: true
predict_light_chain: false
batch_size: 1
num_batches: 1
random_seed: 0
epitope_idxs_or_all: all
antigen_chain_id: "C"
heavy_chain_id: "A"
light_chain_id: "B"

regions:
  hcdr1:
    positions: [24, 25, 26, 27, 28, 29, 30, 31, 32, 33]
    chain: "heavy"
  hcdr2:
    positions: [50, 51, 52, 53, 54, 55, 56, 57, 58]
    chain: "heavy"
  hcdr3:
    positions: [96, 97, 98, 99, 100, 101, 102, 103, 104, 105, 106, 107, 108, 109, 110, 111]
    chain: "heavy"
```

## S2_sequence_checks: Recorded sequence/framework gates and candidate inventory

State: **completed**. Dependencies: `["S1_generation"]`.

Acceptance/checks: Recorded sequence checks and saved per-run evaluation artifacts; see report.md.

Saved stage evidence:

```json
[
  "src/task_005_gal3bp_glycan_aware_interface_refinement/run_002_igdesign_codesign/code/igdesign_gates.py",
  "src/task_005_gal3bp_glycan_aware_interface_refinement/run_002_igdesign_codesign/inputs/igdesign_run002_candidates.json"
]
```

This stage is documented through saved artifacts rather than a normalized call record. The files above are the execution evidence; no command, timestamp or default has been inferred.

## S3_matched_prediction: Three completed AF2-Multimer candidate predictions

State: **completed**. Dependencies: `["S2_sequence_checks"]`.

Acceptance/checks: Recorded sequence checks and saved per-run evaluation artifacts; see report.md.

Saved stage evidence:

```json
[
  "src/task_005_gal3bp_glycan_aware_interface_refinement/run_002_igdesign_codesign/inputs/job_registry.json",
  "src/task_005_gal3bp_glycan_aware_interface_refinement/run_002_igdesign_codesign/inputs/igdesign_run002_job_manifest.json"
]
```

### C01: Multimer_Structure_Prediction

Purpose: Matched evaluation G3I-01

Source: **boltzmann**; recorded state: **completed**.

Exact record: [tool_details.json](../inputs/execution_records/tool_details.json) → `/records/C01`. Original call ID: `saved-afm-G3I-01`.

Identifier/version: `Multimer_Structure_Prediction`.

**Inputs**

```json
{
  "payload_file": "src/task_005_gal3bp_glycan_aware_interface_refinement/run_002_igdesign_codesign/inputs/payload_G3I-01.txt",
  "sha256": "46afc16c1ff4a572c5e61212b200ba40deef986a763cf4f83d2beab8204de6ee"
}
```


**Execution and identifiers**

```json
{
  "doc_id": "6af9a0ce9de6b44b075d9527",
  "record_type": "existing_execution_evidence"
}
```

**Returned outputs / historical output names**

```json
{
  "native_folder": "results/task_005_gal3bp_glycan_aware_interface_refinement/run_002_igdesign_codesign/raw/afm_native/G3I-01",
  "evaluated_structure": "results/task_005_gal3bp_glycan_aware_interface_refinement/run_002_igdesign_codesign/structures/G3I-01_afm_rank1.pdb"
}
```

**Validation and checks**

```json
{
  "sequence_verification": "results/task_005_gal3bp_glycan_aware_interface_refinement/run_002_igdesign_codesign/raw/run002_seq_verification.json"
}
```

### C02: Multimer_Structure_Prediction

Purpose: Matched evaluation G3I-02

Source: **boltzmann**; recorded state: **completed**.

Exact record: [tool_details.json](../inputs/execution_records/tool_details.json) → `/records/C02`. Original call ID: `saved-afm-G3I-02`.

Identifier/version: `Multimer_Structure_Prediction`.

**Inputs**

```json
{
  "payload_file": "src/task_005_gal3bp_glycan_aware_interface_refinement/run_002_igdesign_codesign/inputs/payload_G3I-02.txt",
  "sha256": "a938d0b08d86db0b7c3705b0e4a0fd20ead4753821e65a1b519bef96ab6fac1b"
}
```


**Execution and identifiers**

```json
{
  "doc_id": "6af9a0d7d29658acc304fdb4",
  "record_type": "existing_execution_evidence"
}
```

**Returned outputs / historical output names**

```json
{
  "native_folder": "results/task_005_gal3bp_glycan_aware_interface_refinement/run_002_igdesign_codesign/raw/afm_native/G3I-02",
  "evaluated_structure": "results/task_005_gal3bp_glycan_aware_interface_refinement/run_002_igdesign_codesign/structures/G3I-02_afm_rank1.pdb"
}
```

**Validation and checks**

```json
{
  "sequence_verification": "results/task_005_gal3bp_glycan_aware_interface_refinement/run_002_igdesign_codesign/raw/run002_seq_verification.json"
}
```

### C03: Multimer_Structure_Prediction

Purpose: Matched evaluation G3I-03

Source: **boltzmann**; recorded state: **completed**.

Exact record: [tool_details.json](../inputs/execution_records/tool_details.json) → `/records/C03`. Original call ID: `saved-afm-G3I-03`.

Identifier/version: `Multimer_Structure_Prediction`.

**Inputs**

```json
{
  "payload_file": "src/task_005_gal3bp_glycan_aware_interface_refinement/run_002_igdesign_codesign/inputs/payload_G3I-03.txt",
  "sha256": "59f8783f9a556d548f1a9f0db5046bd215918e56606b76850625e20cb1fa0b4d"
}
```


**Execution and identifiers**

```json
{
  "doc_id": "6af9a105d29658acc304fdc5",
  "record_type": "existing_execution_evidence"
}
```

**Returned outputs / historical output names**

```json
{
  "native_folder": "results/task_005_gal3bp_glycan_aware_interface_refinement/run_002_igdesign_codesign/raw/afm_native/G3I-03",
  "evaluated_structure": "results/task_005_gal3bp_glycan_aware_interface_refinement/run_002_igdesign_codesign/structures/G3I-03_afm_rank1.pdb"
}
```

**Validation and checks**

```json
{
  "sequence_verification": "results/task_005_gal3bp_glycan_aware_interface_refinement/run_002_igdesign_codesign/raw/run002_seq_verification.json"
}
```

## S4_evaluation: Interface chemistry, predicted energy, glycan and model-persistence analyses

State: **completed**. Dependencies: `["S3_matched_prediction"]`.

Acceptance/checks: Recorded sequence checks and saved per-run evaluation artifacts; see report.md.

Saved stage evidence:

```json
[
  "results/task_005_gal3bp_glycan_aware_interface_refinement/run_002_igdesign_codesign/metrics.csv",
  "results/task_005_gal3bp_glycan_aware_interface_refinement/run_002_igdesign_codesign/metrics.json",
  "results/task_005_gal3bp_glycan_aware_interface_refinement/run_002_igdesign_codesign/raw/run002_persistence_glycan.json"
]
```

This stage is documented through saved artifacts rather than a normalized call record. The files above are the execution evidence; no command, timestamp or default has been inferred.
