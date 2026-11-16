# Execution summary — run_001_antibmpnn_interface_refinement

Task: `task_005_gal3bp_glycan_aware_interface_refinement`. Saved run status: **completed_with_caveats**.

Record organization updated 2026-11-16. This is a retrospective presentation of saved execution evidence.

[Compact config](../../../../results/task_005_gal3bp_glycan_aware_interface_refinement/run_001_antibmpnn_interface_refinement/run.json) · [Workflow](../workflow.md) · [Activity log](agent_scientist_log.md) · [Exact original config](../inputs/execution_records/full_config.json) · [Tool details](../inputs/execution_records/tool_details.json) · [File inventory and SHA-256](../inputs/execution_records/run_files.csv)

## Preparation and inputs

Objective: Glycan-aware interface refinement benchmark task: refine/design BDBV-43-derived antibody interface against Gal-3BP (LGALS3BP, UniProt Q08380) following the published study's workflow shape (ref complex -> CDR redesign -> matched evaluation -> interface sampling), using verifiable public inputs

Original input provenance, chain/mask contracts and readiness records are retained below. Current file locations, sizes and full SHA-256 values are in `../inputs/execution_records/run_files.csv`.

```json
[
  {
    "path": "src/task_005_gal3bp_glycan_aware_interface_refinement/run_001_antibmpnn_interface_refinement/inputs/gal3bp_w1_ref_complex/7kew.pdb",
    "provenance": "RCSB PDB 7KEW (Bundibugyo GP antibody BDBV-43)",
    "note": "VH extracted from auth chain G (122 aa), VL from chain J (106 aa)",
    "historical_path": "gal3bp_w1_ref_complex/inputs/7kew.pdb",
    "saved_sha256": "6cd2ea8a143ca36cbc0ebd2f1acd0e82d4a91ffc60e8b00d2b2b5eb15b2246ae"
  },
  {
    "path": "src/task_005_gal3bp_glycan_aware_interface_refinement/run_001_antibmpnn_interface_refinement/inputs/gal3bp_w1_ref_complex/AF-Q08380.pdb",
    "provenance": "AlphaFold DB AF-Q08380 model v6 via API",
    "note": "antigen sequence source of truth for mature 19-585",
    "historical_path": "gal3bp_w1_ref_complex/inputs/AF-Q08380.pdb",
    "saved_sha256": "d6f75334557e3340d73b27e92e5919328ccc308101efc57b5ccd3ac93ab8a109"
  },
  {
    "path": "src/task_005_gal3bp_glycan_aware_interface_refinement/run_001_antibmpnn_interface_refinement/inputs/gal3bp_w1_ref_complex/anarci_out",
    "provenance": "ANARCI imgt --assign_germline on BDBV-43 Fv",
    "note": "germlines IGHV1-69*02/IGHJ5*01, IGKV3-15*01/IGKJ1*01; CDR 1-based windows derived",
    "historical_path": "gal3bp_w1_ref_complex/inputs/anarci_out",
    "saved_sha256": "4e1c4ee7731a774a08536bea32eaba06e8b9d8c9f6014be797fdbf24b9b94639"
  },
  {
    "path": "src/task_005_gal3bp_glycan_aware_interface_refinement/run_001_antibmpnn_interface_refinement/inputs/ref.json",
    "provenance": "composed: 3 protein chains VH/VL/mature Gal-3BP",
    "historical_path": "inputs/ref.json",
    "saved_sha256": "cac0c877df0620250912c4473e96ef32228174007444191186d5479a644a4578"
  },
  {
    "path": "src/task_005_gal3bp_glycan_aware_interface_refinement/run_001_antibmpnn_interface_refinement/inputs/ref_msa.json",
    "provenance": "ref.json + local Protenix MSA paths (12.8k/10.8k/17.2k rows)",
    "historical_path": "inputs/ref_msa.json",
    "saved_sha256": "bf14518b1799f51193ba0858c4dc3cfabca73418629e33f456b8267d7dc47a5b"
  }
]
```

## Recorded outcome

```json
{
  "counts": {
    "designed": 20,
    "unique": 19,
    "evaluated": 3,
    "selected": 3,
    "voided_submissions": 6,
    "task_bundle_files_complete": true
  },
  "last_update": "2026-11-14T19:20Z"
}
```

## Workflow steps and tools

Settings shown below are recorded values. Exact submitted arguments, payloads, resources, responses, validation and fallback details remain in `../inputs/execution_records/tool_details.json`. Historical output names are retained as evidence; use `run_files.csv` for current saved locations.

## W1_ref_complex: None

State: **completed**. Dependencies: `null`.

### C01: Boltz2 (boltzmann platform)

Purpose: pairwise structure prediction VH:VL and VH:antigen

Source: **boltzmann**; recorded state: **completed_superseded**.

Exact record: [tool_details.json](../inputs/execution_records/tool_details.json) → `/records/C01`. Original call ID: `w1-boltz2`.

Identifier/version: `Boltz2`.

**Inputs**

```json
{
  "saved_request": "src/task_005_gal3bp_glycan_aware_interface_refinement/run_001_antibmpnn_interface_refinement/inputs/submitted_requests/message_16571_subcall_0.json",
  "sha256": "11cc468aa2f1767368aa49b40b0a9f3ff2275ad2b93eb0fa2267910817739836"
}
```

**Parameters recorded for this call**

| Setting | Value / exact saved value | Recorded explanation |
| --- | --- | --- |
| `Protein_Sequences` | `{"record": "C01", "pointer": "/parameters/Protein_Sequences", "summary": "sequence lengths: 122, 106, 567"}` | Field meaning: Submitted protein sequence list; order is preserved in the exact request.  |
| `DNA_Sequences` | `[]` | Field meaning: Submitted DNA sequence list.  |
| `RNA_Sequences` | `[]` | Field meaning: Submitted RNA sequence list.  |
| `SMILES` | `[]` | Field meaning: Submitted small-molecule representations.  |

**Execution and identifiers**

```json
{
  "doc_id": "6af844cd9de6b44b075d7a93",
  "duration": "7.6 min"
}
```

**Returned outputs / historical output names**

```json
"gal3bp_w1_ref_complex/outputs/extracted/boltz_pdb/{1,2}_model_0.pdb"
```

**Validation and checks**

```json
"pair models only (no ternary); VH:VL iptm 0.945, VH:antigen iptm 0.317"
```

**Failures, retries and fallback**

```json
"superseded by AFM ternary after platform credits returned"
```

Original submission records: `C01.R01`. These are evidence for this call, not additional completed jobs.

### C01.R01: Boltz2

Purpose: See the stage purpose.

Source: **boltzmann**; recorded state: **Success**.

Exact record: [tool_details.json](../inputs/execution_records/tool_details.json) → `/records/C01.R01`. Original call ID: `call_-7077575589447591549:subcall:0`.

Identifier/version: `Boltz2`.

**Inputs**

```json
{
  "saved_request": "src/task_005_gal3bp_glycan_aware_interface_refinement/run_001_antibmpnn_interface_refinement/inputs/submitted_requests/message_16571_subcall_0.json",
  "sha256": "11cc468aa2f1767368aa49b40b0a9f3ff2275ad2b93eb0fa2267910817739836"
}
```

**Parameters recorded for this call**

| Setting | Value / exact saved value | Recorded explanation |
| --- | --- | --- |
| `Protein_Sequences` | `{"record": "C01.R01", "pointer": "/parameters/Protein_Sequences", "summary": "sequence lengths: 122, 106, 567"}` | Field meaning: Submitted protein sequence list; order is preserved in the exact request.  |
| `DNA_Sequences` | `[]` | Field meaning: Submitted DNA sequence list.  |
| `RNA_Sequences` | `[]` | Field meaning: Submitted RNA sequence list.  |
| `SMILES` | `[]` | Field meaning: Submitted small-molecule representations.  |

**Execution and identifiers**

```json
{
  "session_id": "20261114_110418_c0bdfc",
  "message_id": 16571,
  "tool_call_id": "call_-7077575589447591549",
  "subcall_index": 0,
  "timestamp_utc": "2026-11-14T11:23:57.395199+00:00",
  "doc_id": "6af844cd9de6b44b075d7a93",
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

### C02: Multimer_Structure_Prediction (colabfold_multimer, AF2-Multimer v3)

Purpose: ternary reference complex

Source: **boltzmann**; recorded state: **completed**.

Exact record: [tool_details.json](../inputs/execution_records/tool_details.json) → `/records/C02`. Original call ID: `w1-afm`.

Identifier/version: `Multimer_Structure_Prediction`.

**Inputs**

```json
{
  "saved_request": "src/task_005_gal3bp_glycan_aware_interface_refinement/run_001_antibmpnn_interface_refinement/inputs/submitted_requests/message_17387_subcall_0.json",
  "sha256": "2d49f565e094a0c00c3b62b71441f56c3396cf134acb58ea939af9b845293f3a"
}
```

**Parameters recorded for this call**

| Setting | Value / exact saved value | Recorded explanation |
| --- | --- | --- |
| `input_path` | `{"record": "C02", "pointer": "/parameters/input_path", "summary": "sequence lengths: 122, 106, 567"}` | Field meaning: Tool-specific input field; it may contain a file location or sequence payload.  |

**Execution and identifiers**

```json
{
  "doc_id": "6af879cf9de6b44b075d7f4c",
  "submitted": "2026-11-14T15:10Z",
  "duration": "2h10m"
}
```

**Returned outputs / historical output names**

```json
"gal3bp_w1_ref_complex/outputs_afm/ (5 models)"
```

**Validation and checks**

```json
"chains A/B/C correct; iptm 0.26-0.32 (low-confidence interface, honest borrowed-scaffold prior)"
```

Original submission records: `C02.R01`. These are evidence for this call, not additional completed jobs.

### C02.R01: Multimer_Structure_Prediction

Purpose: See the stage purpose.

Source: **boltzmann**; recorded state: **Success**.

Exact record: [tool_details.json](../inputs/execution_records/tool_details.json) → `/records/C02.R01`. Original call ID: `call_-7077347681303002936:subcall:0`.

Identifier/version: `Multimer_Structure_Prediction`.

**Inputs**

```json
{
  "saved_request": "src/task_005_gal3bp_glycan_aware_interface_refinement/run_001_antibmpnn_interface_refinement/inputs/submitted_requests/message_17387_subcall_0.json",
  "sha256": "2d49f565e094a0c00c3b62b71441f56c3396cf134acb58ea939af9b845293f3a"
}
```

**Parameters recorded for this call**

| Setting | Value / exact saved value | Recorded explanation |
| --- | --- | --- |
| `input_path` | `{"record": "C02.R01", "pointer": "/parameters/input_path", "summary": "sequence lengths: 122, 106, 567"}` | Field meaning: Tool-specific input field; it may contain a file location or sequence payload.  |

**Execution and identifiers**

```json
{
  "session_id": "20261114_110418_c0bdfc",
  "message_id": 17387,
  "tool_call_id": "call_-7077347681303002936",
  "subcall_index": 0,
  "timestamp_utc": "2026-11-14T15:10:07.431908+00:00",
  "doc_id": "6af879cf9de6b44b075d7f4c",
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

### C03: interface_map.py, interface_chemistry.py, glycan_dsasa.py (skill script), Prodigy (conda base)

Purpose: interface map, chemistry, glycan dSASA, dG

Source: **open_source**; recorded state: **completed**.

Exact record: [tool_details.json](../inputs/execution_records/tool_details.json) → `/records/C03`. Original call ID: `w1-local`.

**Inputs**

```json
null
```


**Execution and identifiers**

```json
{
  "environment": "conda base python + Biopython 1.84; local"
}
```

**Returned outputs / historical output names**

```json
"gal3bp_w1_ref_complex/outputs/*.json, prodigy_ref.txt"
```

**Validation and checks**

```json
"ref interface 26 residue pairs (CA-CA<6A, atom-level); 1387 heavy contacts; 9 H-bonds; 0 salt bridges; 530 C-C; Prodigy -9.2 kcal/mol, Kd 1.7e-7; glycan dSASA 245.3 A2 at N344 (simplified model)"
```

## W2_cdr_design: None

State: **completed**. Dependencies: `null`.

### C04: AntiBMPNN (boltzmann platform)

Purpose: CDR redesign on ref rank_001

Source: **boltzmann**; recorded state: **validation_failed**.

Exact record: [tool_details.json](../inputs/execution_records/tool_details.json) → `/records/C04`. Original call ID: `w2-antibmpnn-1`.

Identifier/version: `AntiBMPNN`.

**Inputs**

```json
{
  "saved_request": "src/task_005_gal3bp_glycan_aware_interface_refinement/run_001_antibmpnn_interface_refinement/inputs/submitted_requests/message_18724_subcall_0.json",
  "sha256": "f27d874a0f493de670c2e410411d9cfdd4033b34dd7c9f5efaa63f824d823a1a"
}
```

**Parameters recorded for this call**

| Setting | Value / exact saved value | Recorded explanation |
| --- | --- | --- |
| `chains_to_design` | `["A", "B"]` | Field meaning: Chains selected in the submitted design request.  |
| `generation_count` | `20` | Field meaning: Number of samples requested in that call.  |
| `input_path` | `users/680f678c1b1d883c92aa706c/1794677121895/ref_rank1_clean.pdb` | Field meaning: Tool-specific input field; it may contain a file location or sequence payload.  |
| `residue_positions_to_design` | `{"A": "26-38,54-64,104-117", "B": "26-38,54-61,104-113"}` | Field meaning: Per-chain residue positions supplied in the exact request.  |

**Validation and checks**

```json
"position 113 > chain B length 106 (mask built from gapped IMGT numbering)"
```

**Failures, retries and fallback**

```json
"mask recomputed from ANARCI non-gap indices; L3 clamped to 105-106"
```

Original submission records: `C04.R01`. These are evidence for this call, not additional completed jobs.

### C04.R01: AntiBMPNN

Purpose: See the stage purpose.

Source: **boltzmann**; recorded state: **failed**.

Exact record: [tool_details.json](../inputs/execution_records/tool_details.json) → `/records/C04.R01`. Original call ID: `call_-7077213197287026404:subcall:0`.

Identifier/version: `AntiBMPNN`.

**Inputs**

```json
{
  "saved_request": "src/task_005_gal3bp_glycan_aware_interface_refinement/run_001_antibmpnn_interface_refinement/inputs/submitted_requests/message_18724_subcall_0.json",
  "sha256": "f27d874a0f493de670c2e410411d9cfdd4033b34dd7c9f5efaa63f824d823a1a"
}
```

**Parameters recorded for this call**

| Setting | Value / exact saved value | Recorded explanation |
| --- | --- | --- |
| `chains_to_design` | `["A", "B"]` | Field meaning: Chains selected in the submitted design request.  |
| `generation_count` | `20` | Field meaning: Number of samples requested in that call.  |
| `input_path` | `users/680f678c1b1d883c92aa706c/1794677121895/ref_rank1_clean.pdb` | Field meaning: Tool-specific input field; it may contain a file location or sequence payload.  |
| `residue_positions_to_design` | `{"A": "26-38,54-64,104-117", "B": "26-38,54-61,104-113"}` | Field meaning: Per-chain residue positions supplied in the exact request.  |

**Execution and identifiers**

```json
{
  "session_id": "20261114_110418_c0bdfc",
  "message_id": 18724,
  "tool_call_id": "call_-7077213197287026404",
  "subcall_index": 0,
  "timestamp_utc": "2026-11-14T17:25:47.501736+00:00",
  "doc_id": "6af8999b9030bff4164485c2",
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

### C05: AntiBMPNN (boltzmann platform)

Purpose: CDR redesign

Source: **boltzmann**; recorded state: **completed**.

Exact record: [tool_details.json](../inputs/execution_records/tool_details.json) → `/records/C05`. Original call ID: `w2-antibmpnn-2`.

Identifier/version: `AntiBMPNN`.

**Inputs**

```json
{
  "saved_request": "src/task_005_gal3bp_glycan_aware_interface_refinement/run_001_antibmpnn_interface_refinement/inputs/submitted_requests/message_18740_subcall_0.json",
  "sha256": "22a84ddb4c73e432d354dd62ecccae0799e3a2549978d318aae3086a56e8270a"
}
```

**Parameters recorded for this call**

| Setting | Value / exact saved value | Recorded explanation |
| --- | --- | --- |
| `chains_to_design` | `["A", "B"]` | Field meaning: Chains selected in the submitted design request.  |
| `generation_count` | `20` | Field meaning: Number of samples requested in that call.  |
| `fixed` | `chain C (antigen)` | Field meaning: Recorded protected/fixed portions of the input.  |
| `masks` | `{"A": "27-38,56-65,105-119", "B": "27-38,55-61,105-106"}` | Field meaning: Recorded region/chain masks.  |

**Returned outputs / historical output names**

```json
"gal3bp_w2_cdr_design/outputs/ (19 unique of 20 designs)"
```

**Validation and checks**

```json
"framework positions unchanged (verified by diff); scores 0.336-0.400"
```

Original submission records: `C05.R01`. These are evidence for this call, not additional completed jobs.

### C05.R01: AntiBMPNN

Purpose: See the stage purpose.

Source: **boltzmann**; recorded state: **Success**.

Exact record: [tool_details.json](../inputs/execution_records/tool_details.json) → `/records/C05.R01`. Original call ID: `call_-7077215739907664453:subcall:0`.

Identifier/version: `AntiBMPNN`.

**Inputs**

```json
{
  "saved_request": "src/task_005_gal3bp_glycan_aware_interface_refinement/run_001_antibmpnn_interface_refinement/inputs/submitted_requests/message_18740_subcall_0.json",
  "sha256": "22a84ddb4c73e432d354dd62ecccae0799e3a2549978d318aae3086a56e8270a"
}
```

**Parameters recorded for this call**

| Setting | Value / exact saved value | Recorded explanation |
| --- | --- | --- |
| `chains_to_design` | `["A", "B"]` | Field meaning: Chains selected in the submitted design request.  |
| `generation_count` | `20` | Field meaning: Number of samples requested in that call.  |
| `input_path` | `users/680f678c1b1d883c92aa706c/1794677121895/ref_rank1_clean.pdb` | Field meaning: Tool-specific input field; it may contain a file location or sequence payload.  |
| `residue_positions_to_design` | `{"A": "27-38,56-65,105-119", "B": "27-38,55-61,105-106"}` | Field meaning: Per-chain residue positions supplied in the exact request.  |

**Execution and identifiers**

```json
{
  "session_id": "20261114_110418_c0bdfc",
  "message_id": 18740,
  "tool_call_id": "call_-7077215739907664453",
  "subcall_index": 0,
  "timestamp_utc": "2026-11-14T17:33:02.073750+00:00",
  "doc_id": "6af89b4ed29658acc304eef4",
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

## W3_candidate_eval: None

State: **completed**. Dependencies: `null`.

### C06: Multimer_Structure_Prediction

Purpose: matched evaluation G3BPD-14

Source: **boltzmann**; recorded state: **completed**.

Exact record: [tool_details.json](../inputs/execution_records/tool_details.json) → `/records/C06`. Original call ID: `w3-g14`.

Identifier/version: `Multimer_Structure_Prediction`.

**Inputs**

```json
{
  "saved_request": "src/task_005_gal3bp_glycan_aware_interface_refinement/run_001_antibmpnn_interface_refinement/inputs/submitted_requests/message_18884_subcall_0.json",
  "sha256": "aa6325c5577824ec46367e4eb35f52e56e21050a7288e712ad154388ffb0e261"
}
```

**Parameters recorded for this call**

| Setting | Value / exact saved value | Recorded explanation |
| --- | --- | --- |
| `input_path` | `{"record": "C06", "pointer": "/parameters/input_path", "summary": "sequence lengths: 122, 106, 567"}` | Field meaning: Tool-specific input field; it may contain a file location or sequence payload.  |

**Validation and checks**

```json
"downloaded model VH/VL sequences match design exactly; iptm rank1 0.68 (others 0.50/0.29/0.28/0.28); 512 contacts, 5 H-bonds, Prodigy -8.7"
```

Original submission records: `C06.R01`. These are evidence for this call, not additional completed jobs.

### C06.R01: Multimer_Structure_Prediction

Purpose: See the stage purpose.

Source: **boltzmann**; recorded state: **Success**.

Exact record: [tool_details.json](../inputs/execution_records/tool_details.json) → `/records/C06.R01`. Original call ID: `call_-7077212750610425421:subcall:0`.

Identifier/version: `Multimer_Structure_Prediction`.

**Inputs**

```json
{
  "saved_request": "src/task_005_gal3bp_glycan_aware_interface_refinement/run_001_antibmpnn_interface_refinement/inputs/submitted_requests/message_18884_subcall_0.json",
  "sha256": "aa6325c5577824ec46367e4eb35f52e56e21050a7288e712ad154388ffb0e261"
}
```

**Parameters recorded for this call**

| Setting | Value / exact saved value | Recorded explanation |
| --- | --- | --- |
| `input_path` | `{"record": "C06.R01", "pointer": "/parameters/input_path", "summary": "sequence lengths: 122, 106, 567"}` | Field meaning: Tool-specific input field; it may contain a file location or sequence payload.  |

**Execution and identifiers**

```json
{
  "session_id": "20261114_110418_c0bdfc",
  "message_id": 18884,
  "tool_call_id": "call_-7077212750610425421",
  "subcall_index": 0,
  "timestamp_utc": "2026-11-14T17:41:20.047491+00:00",
  "doc_id": "6af89d409850a93adf67dbf3",
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

### C07: Multimer_Structure_Prediction

Purpose: matched evaluation G3BPD-04

Source: **boltzmann**; recorded state: **completed**.

Exact record: [tool_details.json](../inputs/execution_records/tool_details.json) → `/records/C07`. Original call ID: `w3-g04`.

Identifier/version: `Multimer_Structure_Prediction`.

**Inputs**

```json
{
  "saved_request": "src/task_005_gal3bp_glycan_aware_interface_refinement/run_001_antibmpnn_interface_refinement/inputs/submitted_requests/message_18886_subcall_0.json",
  "sha256": "2cb0e2adef7ce4a6a350e4c62a441d6f743cdc82166a8b9b5239c0e4d1741ed5"
}
```

**Parameters recorded for this call**

| Setting | Value / exact saved value | Recorded explanation |
| --- | --- | --- |
| `input_path` | `{"record": "C07", "pointer": "/parameters/input_path", "summary": "sequence lengths: 122, 106, 567"}` | Field meaning: Tool-specific input field; it may contain a file location or sequence payload.  |

**Validation and checks**

```json
"sequences verified; iptm rank1 0.66 (0.55/0.30/0.30/0.29); 608 contacts, 5 H-bonds, Prodigy -8.7"
```

Original submission records: `C07.R01`. These are evidence for this call, not additional completed jobs.

### C07.R01: Multimer_Structure_Prediction

Purpose: See the stage purpose.

Source: **boltzmann**; recorded state: **Success**.

Exact record: [tool_details.json](../inputs/execution_records/tool_details.json) → `/records/C07.R01`. Original call ID: `call_-7077208764880773712:subcall:0`.

Identifier/version: `Multimer_Structure_Prediction`.

**Inputs**

```json
{
  "saved_request": "src/task_005_gal3bp_glycan_aware_interface_refinement/run_001_antibmpnn_interface_refinement/inputs/submitted_requests/message_18886_subcall_0.json",
  "sha256": "2cb0e2adef7ce4a6a350e4c62a441d6f743cdc82166a8b9b5239c0e4d1741ed5"
}
```

**Parameters recorded for this call**

| Setting | Value / exact saved value | Recorded explanation |
| --- | --- | --- |
| `input_path` | `{"record": "C07.R01", "pointer": "/parameters/input_path", "summary": "sequence lengths: 122, 106, 567"}` | Field meaning: Tool-specific input field; it may contain a file location or sequence payload.  |

**Execution and identifiers**

```json
{
  "session_id": "20261114_110418_c0bdfc",
  "message_id": 18886,
  "tool_call_id": "call_-7077208764880773712",
  "subcall_index": 0,
  "timestamp_utc": "2026-11-14T17:41:39.549926+00:00",
  "doc_id": "6af89d539030bff41644864d",
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

### C08: Multimer_Structure_Prediction

Purpose: matched evaluation G3BPD-17

Source: **boltzmann**; recorded state: **completed**.

Exact record: [tool_details.json](../inputs/execution_records/tool_details.json) → `/records/C08`. Original call ID: `w3-g17`.

Identifier/version: `Multimer_Structure_Prediction`.

**Inputs**

```json
{
  "saved_request": "src/task_005_gal3bp_glycan_aware_interface_refinement/run_001_antibmpnn_interface_refinement/inputs/submitted_requests/message_18956_subcall_0.json",
  "sha256": "3211bd5d1c782d8d2acffddcdc59a45c9cb1675f1e14f9faff60d4b2148171a1"
}
```

**Parameters recorded for this call**

| Setting | Value / exact saved value | Recorded explanation |
| --- | --- | --- |
| `input_path` | `{"record": "C08", "pointer": "/parameters/input_path", "summary": "sequence lengths: 122, 106, 567"}` | Field meaning: Tool-specific input field; it may contain a file location or sequence payload.  |

**Validation and checks**

```json
"sequences verified after chimera void; iptm rank1 0.56 (others pending extraction); 665 contacts, 6 H-bonds, 2 salt bridges, Prodigy -8.6"
```

Original submission records: `C08.R01`. These are evidence for this call, not additional completed jobs.

### C08.R01: Multimer_Structure_Prediction

Purpose: See the stage purpose.

Source: **boltzmann**; recorded state: **Success**.

Exact record: [tool_details.json](../inputs/execution_records/tool_details.json) → `/records/C08.R01`. Original call ID: `call_-7077167567554472990:subcall:0`.

Identifier/version: `Multimer_Structure_Prediction`.

**Inputs**

```json
{
  "saved_request": "src/task_005_gal3bp_glycan_aware_interface_refinement/run_001_antibmpnn_interface_refinement/inputs/submitted_requests/message_18956_subcall_0.json",
  "sha256": "3211bd5d1c782d8d2acffddcdc59a45c9cb1675f1e14f9faff60d4b2148171a1"
}
```

**Parameters recorded for this call**

| Setting | Value / exact saved value | Recorded explanation |
| --- | --- | --- |
| `input_path` | `{"record": "C08.R01", "pointer": "/parameters/input_path", "summary": "sequence lengths: 122, 106, 567"}` | Field meaning: Tool-specific input field; it may contain a file location or sequence payload.  |

**Execution and identifiers**

```json
{
  "session_id": "20261114_110418_c0bdfc",
  "message_id": 18956,
  "tool_call_id": "call_-7077167567554472990",
  "subcall_index": 0,
  "timestamp_utc": "2026-11-14T18:29:42.863248+00:00",
  "doc_id": "6af8a897445ae94313c3cfa6",
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

### C09: ANARCI (igdesign env)

Purpose: germline assignment candidates

Source: **open_source**; recorded state: **completed**.

Exact record: [tool_details.json](../inputs/execution_records/tool_details.json) → `/records/C09`. Original call ID: `w3-anarci`.

**Inputs**

```json
null
```


**Returned outputs / historical output names**

```json
"gal3bp_w3_candidate_eval/outputs/anarci_candidates_summary.json"
```

**Validation and checks**

```json
"all 6 chains numbered; IGHV1-69*06 (0.90-0.91 identity) / IGKV3-15*01 retained; liability scan: NS motif at VH 85 (framework, parental)"
```

### C10: glycan_dsasa.py (skill script, open_source)

Purpose: candidate-side glycan occlusion under identical conventions

Source: **open_source**; recorded state: **completed**.

Exact record: [tool_details.json](../inputs/execution_records/tool_details.json) → `/records/C10`. Original call ID: `w3-glycan`.

**Inputs**

```json
null
```


**Execution and identifiers**

```json
{
  "environment": "conda base python + numpy"
}
```

**Returned outputs / historical output names**

```json
"gal3bp_w3_candidate_eval/outputs/glycan_dsasa_{G3BPD-14,G3BPD-04,G3BPD-17}.json"
```

**Validation and checks**

```json
"dSASA 222.2/217.2/217.5 A2, 0 clashes each; mirrored into results metrics.json"
```

### C11: candidate_persistence.py (local)

Purpose: per-sample interface persistence + inter-model RMSD for each candidate's 5 AFM models

Source: **open_source**; recorded state: **completed**.

Exact record: [tool_details.json](../inputs/execution_records/tool_details.json) → `/records/C11`. Original call ID: `w3-persistence`.

**Inputs**

```json
null
```


**Execution and identifiers**

```json
{
  "environment": "conda base python + Biopython"
}
```

**Returned outputs / historical output names**

```json
"gal3bp_w3_candidate_eval/outputs/candidate_per_sample_persistence.json"
```

**Validation and checks**

```json
"0 rank-1 pairs persist >=3/5 for all candidates; RMSD 6.1-45.3 A; mirrored into metrics.json"
```

## W4_interface_sampling: None

State: **completed**. Dependencies: `null`.

### C12: w4_interface_sampling.py (local)

Purpose: cross-model interface RMSD + persistence on 5 AFM ref models

Source: **open_source**; recorded state: **completed**.

Exact record: [tool_details.json](../inputs/execution_records/tool_details.json) → `/records/C12`. Original call ID: `w4-afm`.

**Inputs**

```json
null
```


**Returned outputs / historical output names**

```json
"gal3bp_w4_interface_sampling/outputs/w4_interface_sampling.json"
```

**Validation and checks**

```json
"0/130 contact pairs persist in >=3 models; pairwise interface RMSD 18-28 A; each model poses the Fv differently (consistent with iptm ~0.3)"
```

### C13: Protenix local (protenix_base_default_v1.0.0)

Purpose: independent-protocol sampling: 3 seeds x 5 samples with real MSAs

Source: **open_source**; recorded state: **completed**.

Exact record: [tool_details.json](../inputs/execution_records/tool_details.json) → `/records/C13`. Original call ID: `w4-protenix`.

**Inputs**

```json
null
```


**Execution and identifiers**

```json
"RTX 3090, 4m19s"
```

**Returned outputs / historical output names**

```json
"gal3bp_w4_interface_sampling/outputs/protenix_w4_summary.json"
```

**Validation and checks**

```json
"iptm 0.146-0.166 all 15 samples; best-sample interface 40 pairs; 0 pairs shared by >1 sample (persistence histogram all 0.1) — third engine confirms no stable interface"
```

### C14: Boltz2 (aux evidence)

Purpose: VH:antigen pair iptm

Source: **boltzmann**; recorded state: **completed**.

Exact record: [tool_details.json](../inputs/execution_records/tool_details.json) → `/records/C14`. Original call ID: `w4-boltz2-aux`.

Identifier/version: `Boltz2`.

**Inputs**

```json
{
  "saved_request": "src/task_005_gal3bp_glycan_aware_interface_refinement/run_001_antibmpnn_interface_refinement/inputs/submitted_requests/message_16571_subcall_0.json",
  "sha256": "11cc468aa2f1767368aa49b40b0a9f3ff2275ad2b93eb0fa2267910817739836"
}
```

**Parameters recorded for this call**

| Setting | Value / exact saved value | Recorded explanation |
| --- | --- | --- |
| `Protein_Sequences` | `{"record": "C14", "pointer": "/parameters/Protein_Sequences", "summary": "sequence lengths: 122, 106, 567"}` | Field meaning: Submitted protein sequence list; order is preserved in the exact request.  |
| `DNA_Sequences` | `[]` | Field meaning: Submitted DNA sequence list.  |
| `RNA_Sequences` | `[]` | Field meaning: Submitted RNA sequence list.  |
| `SMILES` | `[]` | Field meaning: Submitted small-molecule representations.  |

**Validation and checks**

```json
"iptm 0.317"
```

Original submission records: `C14.R01`. These are evidence for this call, not additional completed jobs.

### C14.R01: Boltz2

Purpose: See the stage purpose.

Source: **boltzmann**; recorded state: **Success**.

Exact record: [tool_details.json](../inputs/execution_records/tool_details.json) → `/records/C14.R01`. Original call ID: `call_-7077575589447591549:subcall:0`.

Identifier/version: `Boltz2`.

**Inputs**

```json
{
  "saved_request": "src/task_005_gal3bp_glycan_aware_interface_refinement/run_001_antibmpnn_interface_refinement/inputs/submitted_requests/message_16571_subcall_0.json",
  "sha256": "11cc468aa2f1767368aa49b40b0a9f3ff2275ad2b93eb0fa2267910817739836"
}
```

**Parameters recorded for this call**

| Setting | Value / exact saved value | Recorded explanation |
| --- | --- | --- |
| `Protein_Sequences` | `{"record": "C14.R01", "pointer": "/parameters/Protein_Sequences", "summary": "sequence lengths: 122, 106, 567"}` | Field meaning: Submitted protein sequence list; order is preserved in the exact request.  |
| `DNA_Sequences` | `[]` | Field meaning: Submitted DNA sequence list.  |
| `RNA_Sequences` | `[]` | Field meaning: Submitted RNA sequence list.  |
| `SMILES` | `[]` | Field meaning: Submitted small-molecule representations.  |

**Execution and identifiers**

```json
{
  "session_id": "20261114_110418_c0bdfc",
  "message_id": 16571,
  "tool_call_id": "call_-7077575589447591549",
  "subcall_index": 0,
  "timestamp_utc": "2026-11-14T11:23:57.395199+00:00",
  "doc_id": "6af844cd9de6b44b075d7a93",
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
