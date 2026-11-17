# Execution summary — run_001_antibmpnn_sequence_only

Task: `task_002_pdl1_epitope_targeted_scfv_design`. Saved run status: **completed**.

Record organization updated 2026-11-16. This is a retrospective presentation of saved execution evidence.

[Compact config](../../../../results/task_002_pdl1_epitope_targeted_scfv_design/run_001_antibmpnn_sequence_only/run.json) · [Workflow](../workflow.md) · [Activity log](agent_scientist_log.md) · [Exact original config](../inputs/execution_records/full_config.json) · [Tool details](../inputs/execution_records/tool_details.json) · [File inventory and SHA-256](../inputs/execution_records/run_files.csv)

## Preparation and inputs

Objective: framework-conditioned, epitope-directed design of paired VH/VL candidates (scFv output) against human PD-L1 with H5/35TL as comparator only

Original input provenance, chain/mask contracts and readiness records are retained below. Current file locations, sizes and full SHA-256 values are in `../inputs/execution_records/run_files.csv`.

```json
[
  {
    "path": "src/task_002_pdl1_epitope_targeted_scfv_design/run_001_antibmpnn_sequence_only/inputs/antibody_framework_placed.pdb",
    "sha256": "c23013a8752488b0e5f22825361d4c5879796d23e4e4b7880a49e0a58801d2a1",
    "provenance": "Existing saved task input"
  },
  {
    "path": "src/task_002_pdl1_epitope_targeted_scfv_design/run_001_antibmpnn_sequence_only/inputs/antigen_pdl1_Vdomain.pdb",
    "sha256": "79612be97be4785cc9e83d2c6e1a33beffc8d5db052e477849daa0c327902768",
    "provenance": "Existing saved task input"
  },
  {
    "path": "src/task_002_pdl1_epitope_targeted_scfv_design/run_001_antibmpnn_sequence_only/inputs/eval_35TL_experimental.pdb",
    "sha256": "cffc4623e7139143f59ce1b10b1fc889851e2b9a182300a6a2c838c463808406",
    "provenance": "Existing saved task input"
  },
  {
    "path": "src/task_002_pdl1_epitope_targeted_scfv_design/run_001_antibmpnn_sequence_only/inputs/placed_complex_framework.pdb",
    "sha256": "59caf0aa38ffa4acaed1c7eec16e911e3c120f5f8e078b3fbac81ff917a2f8d3",
    "provenance": "Existing saved task input"
  },
  {
    "path": "src/task_002_pdl1_epitope_targeted_scfv_design/run_001_antibmpnn_sequence_only/inputs/pose_donor_5X8M_durvalumab.pdb",
    "sha256": "72c7afc6526ca5695246c76c533b3864666d1216623e487bf707afb02dcd64af",
    "provenance": "Existing saved task input"
  },
  {
    "path": "src/task_002_pdl1_epitope_targeted_scfv_design/run_001_antibmpnn_sequence_only/inputs/prep_record.json",
    "sha256": "e35dd37c551eba0cb254732b883461aa8f90f0ab8c51d5be7d64c5ae6fe9adb8",
    "provenance": "Existing saved task input"
  },
  {
    "path": "src/task_002_pdl1_epitope_targeted_scfv_design/run_001_antibmpnn_sequence_only/inputs/study_framework_scfv.pdb",
    "sha256": "cbdb24aac3fe9b15b738816421fa02b422d341fde5ccd6ffb12a763763516a93",
    "provenance": "Existing saved task input"
  },
  {
    "path": "src/task_002_pdl1_epitope_targeted_scfv_design/run_001_antibmpnn_sequence_only/inputs/study_target_pdl1_seedcomplex.pdb",
    "sha256": "d7351a441c34cbb9c799798425295106f25beca45428f96d8d8a8f63c586e132",
    "provenance": "Existing saved task input"
  }
]
```

## Recorded outcome

```json
{
  "status": "completed",
  "reason": "Execution and evaluation completed. The recorded result was negative; completion does not imply successful target engagement.",
  "inventory_rows": 9,
  "packaged_at": "2026-11-15T11:14:35+00:00",
  "historical_submission_attempts_recovered": 11
}
```

## Workflow steps and tools

Settings shown below are recorded values. Exact submitted arguments, payloads, resources, responses, validation and fallback details remain in `../inputs/execution_records/tool_details.json`. Historical output names are retained as evidence; use `run_files.csv` for current saved locations.

## W2_generation_and_evaluation: Sequence-only baseline

State: **completed**. Dependencies: `[]`.

Acceptance/checks: Original task constraints and the saved route-specific success/exclusion records.

### C01: AntiBMPNN

Purpose: task002_antibmpnn_cdr_run1

Source: **boltzmann**; recorded state: **unknown**.

Exact record: [tool_details.json](../inputs/execution_records/tool_details.json) → `/records/C01`. Original call ID: `call_-7077301742332803893:subcall:1`.

Identifier/version: `AntiBMPNN`.

**Inputs**

```json
{
  "saved_request": "src/task_002_pdl1_epitope_targeted_scfv_design/run_001_antibmpnn_sequence_only/inputs/submitted_requests/message_18023_subcall_1.json",
  "sha256": "c67a03114dc365451c53d7d6d18bab7fa473c70d4c1689c519f3f32fa0e09442"
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
  "message_id": 18023,
  "tool_call_id": "call_-7077301742332803893",
  "subcall_index": 1,
  "timestamp_utc": "2026-11-14T15:57:14.342556+00:00",
  "experiment_name": "task002_antibmpnn_cdr_run1",
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

Purpose: task002_antibmpnn_cdr_run1

Source: **boltzmann**; recorded state: **accepted**.

Exact record: [tool_details.json](../inputs/execution_records/tool_details.json) → `/records/C02`. Original call ID: `call_-7077313149765936123:subcall:0`.

Identifier/version: `AntiBMPNN`.

**Inputs**

```json
{
  "saved_request": "src/task_002_pdl1_epitope_targeted_scfv_design/run_001_antibmpnn_sequence_only/inputs/submitted_requests/message_18049_subcall_0.json",
  "sha256": "07d4e4568451dcfb6b78b2d0ff55b950c1cf5de069a93eacb46eb73f1bdee7c2"
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
  "message_id": 18049,
  "tool_call_id": "call_-7077313149765936123",
  "subcall_index": 0,
  "timestamp_utc": "2026-11-14T15:57:54.864222+00:00",
  "doc_id": "6af885039850a93adf67d61f",
  "experiment_name": "task002_antibmpnn_cdr_run1",
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

### C03: Boltz2

Purpose: task002_eval_cand0_boltz2

Source: **boltzmann**; recorded state: **accepted**.

Exact record: [tool_details.json](../inputs/execution_records/tool_details.json) → `/records/C03`. Original call ID: `call_-7077299818187453982:subcall:0`.

Identifier/version: `Boltz2`.

**Inputs**

```json
{
  "saved_request": "src/task_002_pdl1_epitope_targeted_scfv_design/run_001_antibmpnn_sequence_only/inputs/submitted_requests/message_18236_subcall_0.json",
  "sha256": "896374dc541c180461bc9cf480be9e434b81f75b9c745cf9657b0bab9c876268"
}
```

**Parameters recorded for this call**

| Setting | Value / exact saved value | Recorded explanation |
| --- | --- | --- |
| `DNA_Sequences` | `[]` | Field meaning: Submitted DNA sequence list.  |
| `Protein_Sequences` | `{"record": "C03", "pointer": "/parameters/Protein_Sequences", "summary": "sequence lengths: 114, 242"}` | Field meaning: Submitted protein sequence list; order is preserved in the exact request.  |
| `RNA_Sequences` | `[]` | Field meaning: Submitted RNA sequence list.  |
| `SMILES` | `[]` | Field meaning: Submitted small-molecule representations.  |

**Execution and identifiers**

```json
{
  "session_id": "20261114_110304_1c10da",
  "message_id": 18236,
  "tool_call_id": "call_-7077299818187453982",
  "subcall_index": 0,
  "timestamp_utc": "2026-11-14T16:05:39.011532+00:00",
  "doc_id": "6af886d39030bff41644818c",
  "experiment_name": "task002_eval_cand0_boltz2",
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

Purpose: task002_eval_cand1_boltz2

Source: **boltzmann**; recorded state: **accepted**.

Exact record: [tool_details.json](../inputs/execution_records/tool_details.json) → `/records/C04`. Original call ID: `call_-7077286211731059585:subcall:0`.

Identifier/version: `Boltz2`.

**Inputs**

```json
{
  "saved_request": "src/task_002_pdl1_epitope_targeted_scfv_design/run_001_antibmpnn_sequence_only/inputs/submitted_requests/message_18239_subcall_0.json",
  "sha256": "d8da3479d8288b9aa6d267576ea0dba70db61e1eca0d223989fcd61cad5c54e7"
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
  "message_id": 18239,
  "tool_call_id": "call_-7077286211731059585",
  "subcall_index": 0,
  "timestamp_utc": "2026-11-14T16:05:46.120444+00:00",
  "doc_id": "6af886da9030bff4164481a8",
  "experiment_name": "task002_eval_cand1_boltz2",
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

Purpose: task002_eval_cand2_boltz2

Source: **boltzmann**; recorded state: **accepted**.

Exact record: [tool_details.json](../inputs/execution_records/tool_details.json) → `/records/C05`. Original call ID: `call_-7077294767305914855:subcall:0`.

Identifier/version: `Boltz2`.

**Inputs**

```json
{
  "saved_request": "src/task_002_pdl1_epitope_targeted_scfv_design/run_001_antibmpnn_sequence_only/inputs/submitted_requests/message_18244_subcall_0.json",
  "sha256": "7ad0110d3e510df82cb6c081b299669450ebc18c2c8dd1e990cdf7ffe2a2564e"
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
  "message_id": 18244,
  "tool_call_id": "call_-7077294767305914855",
  "subcall_index": 0,
  "timestamp_utc": "2026-11-14T16:05:52.541400+00:00",
  "doc_id": "6af886e09de6b44b075d86d4",
  "experiment_name": "task002_eval_cand2_boltz2",
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

Purpose: task002_eval_cand3_boltz2

Source: **boltzmann**; recorded state: **accepted**.

Exact record: [tool_details.json](../inputs/execution_records/tool_details.json) → `/records/C06`. Original call ID: `call_-7077302017210704910:subcall:0`.

Identifier/version: `Boltz2`.

**Inputs**

```json
{
  "saved_request": "src/task_002_pdl1_epitope_targeted_scfv_design/run_001_antibmpnn_sequence_only/inputs/submitted_requests/message_18249_subcall_0.json",
  "sha256": "b0ee4bce9cf1d1d0523d7f65e807d4fe9c3ede6549c8ea9c8892ce5334f91777"
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
  "message_id": 18249,
  "tool_call_id": "call_-7077302017210704910",
  "subcall_index": 0,
  "timestamp_utc": "2026-11-14T16:05:59.322103+00:00",
  "doc_id": "6af886e7239a6b9f38bec364",
  "experiment_name": "task002_eval_cand3_boltz2",
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

Purpose: task002_eval_cand0_v2

Source: **boltzmann**; recorded state: **accepted**.

Exact record: [tool_details.json](../inputs/execution_records/tool_details.json) → `/records/C07`. Original call ID: `call_-7077283359872772470:subcall:0`.

Identifier/version: `Boltz2`.

**Inputs**

```json
{
  "saved_request": "src/task_002_pdl1_epitope_targeted_scfv_design/run_001_antibmpnn_sequence_only/inputs/submitted_requests/message_18570_subcall_0.json",
  "sha256": "3bdb2461e04885c64c55944e346e84e2aa72e42715e3a3786f3e498f40ef24f0"
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
  "message_id": 18570,
  "tool_call_id": "call_-7077283359872772470",
  "subcall_index": 0,
  "timestamp_utc": "2026-11-14T16:23:09.846424+00:00",
  "doc_id": "6af88aed9850a93adf67d954",
  "experiment_name": "task002_eval_cand0_v2",
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

Purpose: task002_eval_cand2_v2

Source: **boltzmann**; recorded state: **accepted**.

Exact record: [tool_details.json](../inputs/execution_records/tool_details.json) → `/records/C08`. Original call ID: `call_-7077277931034111425:subcall:0`.

Identifier/version: `Boltz2`.

**Inputs**

```json
{
  "saved_request": "src/task_002_pdl1_epitope_targeted_scfv_design/run_001_antibmpnn_sequence_only/inputs/submitted_requests/message_18572_subcall_0.json",
  "sha256": "82ccff275e3f26e3b58d59c7684d0deb2c2964601b0e90164758e02ce76aa464"
}
```

**Parameters recorded for this call**

| Setting | Value / exact saved value | Recorded explanation |
| --- | --- | --- |
| `DNA_Sequences` | `[]` | Field meaning: Submitted DNA sequence list.  |
| `Protein_Sequences` | `{"record": "C08", "pointer": "/parameters/Protein_Sequences", "summary": "sequence lengths: 114, 242"}` | Field meaning: Submitted protein sequence list; order is preserved in the exact request.  |
| `RNA_Sequences` | `[]` | Field meaning: Submitted RNA sequence list.  |
| `SMILES` | `[]` | Field meaning: Submitted small-molecule representations.  |

**Execution and identifiers**

```json
{
  "session_id": "20261114_110304_1c10da",
  "message_id": 18572,
  "tool_call_id": "call_-7077277931034111425",
  "subcall_index": 0,
  "timestamp_utc": "2026-11-14T16:23:18.173990+00:00",
  "doc_id": "6af88af6239a6b9f38bec57b",
  "experiment_name": "task002_eval_cand2_v2",
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

Purpose: task002_eval_cand3_v2

Source: **boltzmann**; recorded state: **accepted**.

Exact record: [tool_details.json](../inputs/execution_records/tool_details.json) → `/records/C09`. Original call ID: `call_-7077282054202712505:subcall:0`.

Identifier/version: `Boltz2`.

**Inputs**

```json
{
  "saved_request": "src/task_002_pdl1_epitope_targeted_scfv_design/run_001_antibmpnn_sequence_only/inputs/submitted_requests/message_18574_subcall_0.json",
  "sha256": "cc311f55620a119301e863c665c34e556b2a662eaab5af2e24ffe27bb5c38d4a"
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
  "message_id": 18574,
  "tool_call_id": "call_-7077282054202712505",
  "subcall_index": 0,
  "timestamp_utc": "2026-11-14T16:23:24.257324+00:00",
  "doc_id": "6af88afc9de6b44b075d88fd",
  "experiment_name": "task002_eval_cand3_v2",
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

Purpose: task002_eval_cand4_v2

Source: **boltzmann**; recorded state: **accepted**.

Exact record: [tool_details.json](../inputs/execution_records/tool_details.json) → `/records/C10`. Original call ID: `call_-7077277072040654863:subcall:0`.

Identifier/version: `Boltz2`.

**Inputs**

```json
{
  "saved_request": "src/task_002_pdl1_epitope_targeted_scfv_design/run_001_antibmpnn_sequence_only/inputs/submitted_requests/message_18576_subcall_0.json",
  "sha256": "934a0a32af474a45baaa4d1dee4bfc0777233d6059fc8d45117c44d8928d26e7"
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
  "message_id": 18576,
  "tool_call_id": "call_-7077277072040654863",
  "subcall_index": 0,
  "timestamp_utc": "2026-11-14T16:23:33.204544+00:00",
  "doc_id": "6af88b05445ae94313c3c6cc",
  "experiment_name": "task002_eval_cand4_v2",
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

Purpose: task002_eval_cand1_v2

Source: **boltzmann**; recorded state: **accepted**.

Exact record: [tool_details.json](../inputs/execution_records/tool_details.json) → `/records/C11`. Original call ID: `call_-7077282741397484488:subcall:0`.

Identifier/version: `Boltz2`.

**Inputs**

```json
{
  "saved_request": "src/task_002_pdl1_epitope_targeted_scfv_design/run_001_antibmpnn_sequence_only/inputs/submitted_requests/message_18578_subcall_0.json",
  "sha256": "0f5effe56da0c9b609b27a9634efc175274312fc9e183667fd4f159853131b46"
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
  "message_id": 18578,
  "tool_call_id": "call_-7077282741397484488",
  "subcall_index": 0,
  "timestamp_utc": "2026-11-14T16:23:48.790766+00:00",
  "doc_id": "6af88b14d29658acc304ecc0",
  "experiment_name": "task002_eval_cand1_v2",
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
