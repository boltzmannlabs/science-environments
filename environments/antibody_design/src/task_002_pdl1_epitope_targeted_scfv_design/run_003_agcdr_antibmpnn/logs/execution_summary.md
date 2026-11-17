# Execution summary — run_003_agcdr_antibmpnn

Task: `task_002_pdl1_epitope_targeted_scfv_design`. Saved run status: **completed**.

Record organization updated 2026-11-16. This is a retrospective presentation of saved execution evidence.

[Compact config](../../../../results/task_002_pdl1_epitope_targeted_scfv_design/run_003_agcdr_antibmpnn/run.json) · [Workflow](../workflow.md) · [Activity log](agent_scientist_log.md) · [Exact original config](../inputs/execution_records/full_config.json) · [Tool details](../inputs/execution_records/tool_details.json) · [File inventory and SHA-256](../inputs/execution_records/run_files.csv)

## Preparation and inputs

Objective: framework-conditioned, epitope-directed design of paired VH/VL candidates (scFv output) against human PD-L1 with H5/35TL as comparator only

Original input provenance, chain/mask contracts and readiness records are retained below. Current file locations, sizes and full SHA-256 values are in `../inputs/execution_records/run_files.csv`.

```json
[
  {
    "path": "src/task_002_pdl1_epitope_targeted_scfv_design/run_003_agcdr_antibmpnn/inputs/antibody_framework_placed.pdb",
    "sha256": "c23013a8752488b0e5f22825361d4c5879796d23e4e4b7880a49e0a58801d2a1",
    "provenance": "Existing saved task input"
  },
  {
    "path": "src/task_002_pdl1_epitope_targeted_scfv_design/run_003_agcdr_antibmpnn/inputs/antigen_pdl1_Vdomain.pdb",
    "sha256": "79612be97be4785cc9e83d2c6e1a33beffc8d5db052e477849daa0c327902768",
    "provenance": "Existing saved task input"
  },
  {
    "path": "src/task_002_pdl1_epitope_targeted_scfv_design/run_003_agcdr_antibmpnn/inputs/eval_35TL_experimental.pdb",
    "sha256": "cffc4623e7139143f59ce1b10b1fc889851e2b9a182300a6a2c838c463808406",
    "provenance": "Existing saved task input"
  },
  {
    "path": "src/task_002_pdl1_epitope_targeted_scfv_design/run_003_agcdr_antibmpnn/inputs/placed_complex_framework.pdb",
    "sha256": "59caf0aa38ffa4acaed1c7eec16e911e3c120f5f8e078b3fbac81ff917a2f8d3",
    "provenance": "Existing saved task input"
  },
  {
    "path": "src/task_002_pdl1_epitope_targeted_scfv_design/run_003_agcdr_antibmpnn/inputs/pose_donor_5X8M_durvalumab.pdb",
    "sha256": "72c7afc6526ca5695246c76c533b3864666d1216623e487bf707afb02dcd64af",
    "provenance": "Existing saved task input"
  },
  {
    "path": "src/task_002_pdl1_epitope_targeted_scfv_design/run_003_agcdr_antibmpnn/inputs/prep_record.json",
    "sha256": "e35dd37c551eba0cb254732b883461aa8f90f0ab8c51d5be7d64c5ae6fe9adb8",
    "provenance": "Existing saved task input"
  },
  {
    "path": "src/task_002_pdl1_epitope_targeted_scfv_design/run_003_agcdr_antibmpnn/inputs/study_framework_scfv.pdb",
    "sha256": "cbdb24aac3fe9b15b738816421fa02b422d341fde5ccd6ffb12a763763516a93",
    "provenance": "Existing saved task input"
  },
  {
    "path": "src/task_002_pdl1_epitope_targeted_scfv_design/run_003_agcdr_antibmpnn/inputs/study_target_pdl1_seedcomplex.pdb",
    "sha256": "d7351a441c34cbb9c799798425295106f25beca45428f96d8d8a8f63c586e132",
    "provenance": "Existing saved task input"
  }
]
```

## Recorded outcome

```json
{
  "status": "completed",
  "reason": "Alternative workflow completed with saved generated and evaluated outputs. It is a different implementation from W1; comparative limitations remain in the historical report.",
  "inventory_rows": 8,
  "packaged_at": "2026-11-15T11:14:35+00:00",
  "historical_submission_attempts_recovered": 12
}
```

## Workflow steps and tools

Settings shown below are recorded values. Exact submitted arguments, payloads, resources, responses, validation and fallback details remain in `../inputs/execution_records/tool_details.json`. Historical output names are retained as evidence; use `run_files.csv` for current saved locations.

## W4_generation_and_evaluation: Backbone-generation alternative and evaluation

State: **completed**. Dependencies: `[]`.

Acceptance/checks: Original task constraints and the saved route-specific success/exclusion records.

### C01: agcdr_diff

Purpose: task002_agcdr_diff_run1

Source: **boltzmann**; recorded state: **accepted**.

Exact record: [tool_details.json](../inputs/execution_records/tool_details.json) → `/records/C01`. Original call ID: `call_-7077259136257224762:subcall:0`.

Identifier/version: `agcdr_diff`.

**Inputs**

```json
{
  "saved_request": "src/task_002_pdl1_epitope_targeted_scfv_design/run_003_agcdr_antibmpnn/inputs/submitted_requests/message_18613_subcall_0.json",
  "sha256": "69bdd9737c0624a91fc1de7d46ccdaf6105794245f83bb63c82671aa88e7e49d"
}
```

**Parameters recorded for this call**

| Setting | Value / exact saved value | Recorded explanation |
| --- | --- | --- |
| `antibody_pdb_path` | `users/68d12a5de5b6a2fdc0e3c443/1794655276746/antibody_framework_placed.pdb` | Field meaning: Antibody structure input location.  |
| `antigen_pdb_path` | `users/68d12a5de5b6a2fdc0e3c443/1794655271659/antigen_pdl1_Vdomain.pdb` | Field meaning: Antigen structure input location.  |
| `num_samples` | `8` | Field meaning: Number of samples requested.  |
| `num_steps` | `10` | Field meaning: Requested sampling-step count.  |

**Execution and identifiers**

```json
{
  "session_id": "20261114_110304_1c10da",
  "message_id": 18613,
  "tool_call_id": "call_-7077259136257224762",
  "subcall_index": 0,
  "timestamp_utc": "2026-11-14T16:33:15.090181+00:00",
  "doc_id": "6af88d4b9de6b44b075d8990",
  "experiment_name": "task002_agcdr_diff_run1",
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

### C02: AntiBMPNN

Purpose: task002_antibmpnn_on_agcdr_sample1

Source: **boltzmann**; recorded state: **accepted**.

Exact record: [tool_details.json](../inputs/execution_records/tool_details.json) → `/records/C02`. Original call ID: `call_-7077265080491962406:subcall:0`.

Identifier/version: `AntiBMPNN`.

**Inputs**

```json
{
  "saved_request": "src/task_002_pdl1_epitope_targeted_scfv_design/run_003_agcdr_antibmpnn/inputs/submitted_requests/message_18631_subcall_0.json",
  "sha256": "6bdbbbdb13134d1917354b84dce5f4d9c653eb69d47360f603a7af9c1abcfe79"
}
```

**Parameters recorded for this call**

| Setting | Value / exact saved value | Recorded explanation |
| --- | --- | --- |
| `chains_to_design` | `["H", "L"]` | Field meaning: Chains selected in the submitted design request.  |
| `generation_count` | `8` | Field meaning: Number of samples requested in that call.  |
| `input_path` | `users/68d12a5de5b6a2fdc0e3c443/1794655276746/antibody_framework_placed.pdb` | Field meaning: Tool-specific input field; it may contain a file location or sequence payload.  |
| `residue_positions_to_design` | `{"H": "26-33,51-58,97-109", "L": "24-29,50-55,89-97"}` | Field meaning: Per-chain residue positions supplied in the exact request.  |

**Execution and identifiers**

```json
{
  "session_id": "20261114_110304_1c10da",
  "message_id": 18631,
  "tool_call_id": "call_-7077265080491962406",
  "subcall_index": 0,
  "timestamp_utc": "2026-11-14T16:35:20.665064+00:00",
  "doc_id": "6af88dc99030bff416448460",
  "experiment_name": "task002_antibmpnn_on_agcdr_sample1",
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

### C03: AntiBMPNN

Purpose: task002_antibmpnn_on_agcdr1

Source: **boltzmann**; recorded state: **accepted**.

Exact record: [tool_details.json](../inputs/execution_records/tool_details.json) → `/records/C03`. Original call ID: `call_-7077273086311000571:subcall:0`.

Identifier/version: `AntiBMPNN`.

**Inputs**

```json
{
  "saved_request": "src/task_002_pdl1_epitope_targeted_scfv_design/run_003_agcdr_antibmpnn/inputs/submitted_requests/message_18639_subcall_0.json",
  "sha256": "1ecf123a24ba4ca077579508acdaf4a22ac2009300af5e0c002faed20009fbe3"
}
```

**Parameters recorded for this call**

| Setting | Value / exact saved value | Recorded explanation |
| --- | --- | --- |
| `chains_to_design` | `["H", "L"]` | Field meaning: Chains selected in the submitted design request.  |
| `generation_count` | `8` | Field meaning: Number of samples requested in that call.  |
| `input_path` | `users/680f678c1b1d883c92aa706c/1794674148445/agcdr_sample1_design_input.pdb` | Field meaning: Tool-specific input field; it may contain a file location or sequence payload.  |
| `residue_positions_to_design` | `{"H": "26-33,51-58,97-109", "L": "24-29,50-55,89-97"}` | Field meaning: Per-chain residue positions supplied in the exact request.  |

**Execution and identifiers**

```json
{
  "session_id": "20261114_110304_1c10da",
  "message_id": 18639,
  "tool_call_id": "call_-7077273086311000571",
  "subcall_index": 0,
  "timestamp_utc": "2026-11-14T16:35:53.872362+00:00",
  "doc_id": "6af88dea445ae94313c3c8c6",
  "experiment_name": "task002_antibmpnn_on_agcdr1",
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

### C04: Boltz2

Purpose: task002_agcdr1_cand0_eval

Source: **boltzmann**; recorded state: **accepted**.

Exact record: [tool_details.json](../inputs/execution_records/tool_details.json) → `/records/C04`. Original call ID: `call_-7077264771254318579:subcall:0`.

Identifier/version: `Boltz2`.

**Inputs**

```json
{
  "saved_request": "src/task_002_pdl1_epitope_targeted_scfv_design/run_003_agcdr_antibmpnn/inputs/submitted_requests/message_18649_subcall_0.json",
  "sha256": "a8f9d8b70dff9ae04a172b941883bb9e74d520a51d4a32bbca4b727a7ae06402"
}
```

**Parameters recorded for this call**

| Setting | Value / exact saved value | Recorded explanation |
| --- | --- | --- |
| `DNA_Sequences` | `[]` | Field meaning: Submitted DNA sequence list.  |
| `Protein_Sequences` | `{"record": "C04", "pointer": "/parameters/Protein_Sequences", "summary": "sequence lengths: 114, 242"}` | Field meaning: Submitted protein sequence list; order is preserved in the exact request.  |
| `RNA_Sequences` | `[]` | Field meaning: Submitted RNA sequence list.  |
| `SMILES` | `[]` | Field meaning: Submitted small-molecule representations.  |

**Execution and identifiers**

```json
{
  "session_id": "20261114_110304_1c10da",
  "message_id": 18649,
  "tool_call_id": "call_-7077264771254318579",
  "subcall_index": 0,
  "timestamp_utc": "2026-11-14T16:42:48.464688+00:00",
  "doc_id": "6af88f88d29658acc304edab",
  "experiment_name": "task002_agcdr1_cand0_eval",
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

### C05: Boltz2

Purpose: task002_agcdr1_cand1_eval

Source: **boltzmann**; recorded state: **accepted**.

Exact record: [tool_details.json](../inputs/execution_records/tool_details.json) → `/records/C05`. Original call ID: `call_-7077253535619867613:subcall:0`.

Identifier/version: `Boltz2`.

**Inputs**

```json
{
  "saved_request": "src/task_002_pdl1_epitope_targeted_scfv_design/run_003_agcdr_antibmpnn/inputs/submitted_requests/message_18651_subcall_0.json",
  "sha256": "685422830aa04d86c42741a4ce96452141651fb38fae7b68c969c39eaee4bcbb"
}
```

**Parameters recorded for this call**

| Setting | Value / exact saved value | Recorded explanation |
| --- | --- | --- |
| `DNA_Sequences` | `[]` | Field meaning: Submitted DNA sequence list.  |
| `Protein_Sequences` | `{"record": "C05", "pointer": "/parameters/Protein_Sequences", "summary": "sequence lengths: 114, 242"}` | Field meaning: Submitted protein sequence list; order is preserved in the exact request.  |
| `RNA_Sequences` | `[]` | Field meaning: Submitted RNA sequence list.  |
| `SMILES` | `[]` | Field meaning: Submitted small-molecule representations.  |

**Execution and identifiers**

```json
{
  "session_id": "20261114_110304_1c10da",
  "message_id": 18651,
  "tool_call_id": "call_-7077253535619867613",
  "subcall_index": 0,
  "timestamp_utc": "2026-11-14T16:42:55.581799+00:00",
  "doc_id": "6af88f8f445ae94313c3c96e",
  "experiment_name": "task002_agcdr1_cand1_eval",
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

### C06: Boltz2

Purpose: task002_agcdr1_cand2_eval

Source: **boltzmann**; recorded state: **accepted**.

Exact record: [tool_details.json](../inputs/execution_records/tool_details.json) → `/records/C06`. Original call ID: `call_-7077257933666380760:subcall:0`.

Identifier/version: `Boltz2`.

**Inputs**

```json
{
  "saved_request": "src/task_002_pdl1_epitope_targeted_scfv_design/run_003_agcdr_antibmpnn/inputs/submitted_requests/message_18653_subcall_0.json",
  "sha256": "19b21b89a8605b86a2222bd36785b649a45ecea9a5d4783948b0c970fc15b756"
}
```

**Parameters recorded for this call**

| Setting | Value / exact saved value | Recorded explanation |
| --- | --- | --- |
| `DNA_Sequences` | `[]` | Field meaning: Submitted DNA sequence list.  |
| `Protein_Sequences` | `{"record": "C06", "pointer": "/parameters/Protein_Sequences", "summary": "sequence lengths: 114, 242"}` | Field meaning: Submitted protein sequence list; order is preserved in the exact request.  |
| `RNA_Sequences` | `[]` | Field meaning: Submitted RNA sequence list.  |
| `SMILES` | `[]` | Field meaning: Submitted small-molecule representations.  |

**Execution and identifiers**

```json
{
  "session_id": "20261114_110304_1c10da",
  "message_id": 18653,
  "tool_call_id": "call_-7077257933666380760",
  "subcall_index": 0,
  "timestamp_utc": "2026-11-14T16:43:02.141317+00:00",
  "doc_id": "6af88f96239a6b9f38bec682",
  "experiment_name": "task002_agcdr1_cand2_eval",
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

### C07: Boltz2

Purpose: task002_agcdr1_cand3_eval

Source: **boltzmann**; recorded state: **accepted**.

Exact record: [tool_details.json](../inputs/execution_records/tool_details.json) → `/records/C07`. Original call ID: `call_-7077253879217255451:subcall:0`.

Identifier/version: `Boltz2`.

**Inputs**

```json
{
  "saved_request": "src/task_002_pdl1_epitope_targeted_scfv_design/run_003_agcdr_antibmpnn/inputs/submitted_requests/message_18655_subcall_0.json",
  "sha256": "a68e772f7d7b1549a30f4648d41c86ae65f2b06b518215b36949d7508757a3f0"
}
```

**Parameters recorded for this call**

| Setting | Value / exact saved value | Recorded explanation |
| --- | --- | --- |
| `DNA_Sequences` | `[]` | Field meaning: Submitted DNA sequence list.  |
| `Protein_Sequences` | `{"record": "C07", "pointer": "/parameters/Protein_Sequences", "summary": "sequence lengths: 114, 242"}` | Field meaning: Submitted protein sequence list; order is preserved in the exact request.  |
| `RNA_Sequences` | `[]` | Field meaning: Submitted RNA sequence list.  |
| `SMILES` | `[]` | Field meaning: Submitted small-molecule representations.  |

**Execution and identifiers**

```json
{
  "session_id": "20261114_110304_1c10da",
  "message_id": 18655,
  "tool_call_id": "call_-7077253879217255451",
  "subcall_index": 0,
  "timestamp_utc": "2026-11-14T16:43:08.894205+00:00",
  "doc_id": "6af88f9d445ae94313c3c983",
  "experiment_name": "task002_agcdr1_cand3_eval",
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

Purpose: task002_agcdr1_cand4_eval

Source: **boltzmann**; recorded state: **accepted**.

Exact record: [tool_details.json](../inputs/execution_records/tool_details.json) → `/records/C08`. Original call ID: `call_-7077256627996326947:subcall:0`.

Identifier/version: `Boltz2`.

**Inputs**

```json
{
  "saved_request": "src/task_002_pdl1_epitope_targeted_scfv_design/run_003_agcdr_antibmpnn/inputs/submitted_requests/message_18657_subcall_0.json",
  "sha256": "6de05d44ff13506455e17d7ca4b7ac91bb2e84bfc77745c1d2cee7053df86501"
}
```

**Parameters recorded for this call**

| Setting | Value / exact saved value | Recorded explanation |
| --- | --- | --- |
| `DNA_Sequences` | `[]` | Field meaning: Submitted DNA sequence list.  |
| `Protein_Sequences` | `{"record": "C08", "pointer": "/parameters/Protein_Sequences", "summary": "sequence lengths: 114, 241"}` | Field meaning: Submitted protein sequence list; order is preserved in the exact request.  |
| `RNA_Sequences` | `[]` | Field meaning: Submitted RNA sequence list.  |
| `SMILES` | `[]` | Field meaning: Submitted small-molecule representations.  |

**Execution and identifiers**

```json
{
  "session_id": "20261114_110304_1c10da",
  "message_id": 18657,
  "tool_call_id": "call_-7077256627996326947",
  "subcall_index": 0,
  "timestamp_utc": "2026-11-14T16:43:16.144890+00:00",
  "doc_id": "6af88fa49850a93adf67da68",
  "experiment_name": "task002_agcdr1_cand4_eval",
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

### C09: Boltz2

Purpose: task002_agcdr1_cand5_eval

Source: **boltzmann**; recorded state: **accepted**.

Exact record: [tool_details.json](../inputs/execution_records/tool_details.json) → `/records/C09`. Original call ID: `call_-7077250202725246968:subcall:0`.

Identifier/version: `Boltz2`.

**Inputs**

```json
{
  "saved_request": "src/task_002_pdl1_epitope_targeted_scfv_design/run_003_agcdr_antibmpnn/inputs/submitted_requests/message_18661_subcall_0.json",
  "sha256": "4407ba8af1366de5fc8b8cb06bef3e5b92f9d01dcaed13ef2492aa48a25ec4ab"
}
```

**Parameters recorded for this call**

| Setting | Value / exact saved value | Recorded explanation |
| --- | --- | --- |
| `DNA_Sequences` | `[]` | Field meaning: Submitted DNA sequence list.  |
| `Protein_Sequences` | `{"record": "C09", "pointer": "/parameters/Protein_Sequences", "summary": "sequence lengths: 114, 242"}` | Field meaning: Submitted protein sequence list; order is preserved in the exact request.  |
| `RNA_Sequences` | `[]` | Field meaning: Submitted RNA sequence list.  |
| `SMILES` | `[]` | Field meaning: Submitted small-molecule representations.  |

**Execution and identifiers**

```json
{
  "session_id": "20261114_110304_1c10da",
  "message_id": 18661,
  "tool_call_id": "call_-7077250202725246968",
  "subcall_index": 0,
  "timestamp_utc": "2026-11-14T16:43:27.661231+00:00",
  "doc_id": "6af88faf9850a93adf67da73",
  "experiment_name": "task002_agcdr1_cand5_eval",
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

### C10: Boltz2

Purpose: task002_agcdr1_cand6_eval

Source: **boltzmann**; recorded state: **accepted**.

Exact record: [tool_details.json](../inputs/execution_records/tool_details.json) → `/records/C10`. Original call ID: `call_-7077258517781937754:subcall:0`.

Identifier/version: `Boltz2`.

**Inputs**

```json
{
  "saved_request": "src/task_002_pdl1_epitope_targeted_scfv_design/run_003_agcdr_antibmpnn/inputs/submitted_requests/message_18663_subcall_0.json",
  "sha256": "3cb8e780a8aa80b4b30a23779b584cfca127d21f5f8e23e163840800071f9182"
}
```

**Parameters recorded for this call**

| Setting | Value / exact saved value | Recorded explanation |
| --- | --- | --- |
| `DNA_Sequences` | `[]` | Field meaning: Submitted DNA sequence list.  |
| `Protein_Sequences` | `{"record": "C10", "pointer": "/parameters/Protein_Sequences", "summary": "sequence lengths: 114, 242"}` | Field meaning: Submitted protein sequence list; order is preserved in the exact request.  |
| `RNA_Sequences` | `[]` | Field meaning: Submitted RNA sequence list.  |
| `SMILES` | `[]` | Field meaning: Submitted small-molecule representations.  |

**Execution and identifiers**

```json
{
  "session_id": "20261114_110304_1c10da",
  "message_id": 18663,
  "tool_call_id": "call_-7077258517781937754",
  "subcall_index": 0,
  "timestamp_utc": "2026-11-14T16:43:34.086612+00:00",
  "doc_id": "6af88fb6239a6b9f38bec694",
  "experiment_name": "task002_agcdr1_cand6_eval",
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

### C11: Boltz2

Purpose: task002_agcdr1_cand7_eval

Source: **boltzmann**; recorded state: **accepted**.

Exact record: [tool_details.json](../inputs/execution_records/tool_details.json) → `/records/C11`. Original call ID: `call_-7077257968026121543:subcall:0`.

Identifier/version: `Boltz2`.

**Inputs**

```json
{
  "saved_request": "src/task_002_pdl1_epitope_targeted_scfv_design/run_003_agcdr_antibmpnn/inputs/submitted_requests/message_18665_subcall_0.json",
  "sha256": "e9e1a424c72db3c3bfc3e8e3635e12e558c9a71692fd5164543a9283e6315ac1"
}
```

**Parameters recorded for this call**

| Setting | Value / exact saved value | Recorded explanation |
| --- | --- | --- |
| `DNA_Sequences` | `[]` | Field meaning: Submitted DNA sequence list.  |
| `Protein_Sequences` | `{"record": "C11", "pointer": "/parameters/Protein_Sequences", "summary": "sequence lengths: 114, 242"}` | Field meaning: Submitted protein sequence list; order is preserved in the exact request.  |
| `RNA_Sequences` | `[]` | Field meaning: Submitted RNA sequence list.  |
| `SMILES` | `[]` | Field meaning: Submitted small-molecule representations.  |

**Execution and identifiers**

```json
{
  "session_id": "20261114_110304_1c10da",
  "message_id": 18665,
  "tool_call_id": "call_-7077257968026121543",
  "subcall_index": 0,
  "timestamp_utc": "2026-11-14T16:43:41.179274+00:00",
  "doc_id": "6af88fbd445ae94313c3c9c0",
  "experiment_name": "task002_agcdr1_cand7_eval",
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

### C12: Boltz2

Purpose: task002_agcdr1_cand4b_eval

Source: **boltzmann**; recorded state: **accepted**.

Exact record: [tool_details.json](../inputs/execution_records/tool_details.json) → `/records/C12`. Original call ID: `call_-7077256524917105413:subcall:0`.

Identifier/version: `Boltz2`.

**Inputs**

```json
{
  "saved_request": "src/task_002_pdl1_epitope_targeted_scfv_design/run_003_agcdr_antibmpnn/inputs/submitted_requests/message_18683_subcall_0.json",
  "sha256": "c3e1828ff453584be26959b318e256e7ec6977b07f4e3dde32c581e507f373b2"
}
```

**Parameters recorded for this call**

| Setting | Value / exact saved value | Recorded explanation |
| --- | --- | --- |
| `DNA_Sequences` | `[]` | Field meaning: Submitted DNA sequence list.  |
| `Protein_Sequences` | `{"record": "C12", "pointer": "/parameters/Protein_Sequences", "summary": "sequence lengths: 114, 242"}` | Field meaning: Submitted protein sequence list; order is preserved in the exact request.  |
| `RNA_Sequences` | `[]` | Field meaning: Submitted RNA sequence list.  |
| `SMILES` | `[]` | Field meaning: Submitted small-molecule representations.  |

**Execution and identifiers**

```json
{
  "session_id": "20261114_110304_1c10da",
  "message_id": 18683,
  "tool_call_id": "call_-7077256524917105413",
  "subcall_index": 0,
  "timestamp_utc": "2026-11-14T16:54:53.733116+00:00",
  "doc_id": "6af8925d239a6b9f38bec737",
  "experiment_name": "task002_agcdr1_cand4b_eval",
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
