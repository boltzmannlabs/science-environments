# Execution summary — run_002_rf_antibody

Task: `task_002_pdl1_epitope_targeted_scfv_design`. Saved run status: **completed**.

Record organization updated 2026-11-16. This is a retrospective presentation of saved execution evidence.

[Compact config](../../../../results/task_002_pdl1_epitope_targeted_scfv_design/run_002_rf_antibody/run.json) · [Workflow](../workflow.md) · [Activity log](agent_scientist_log.md) · [Exact original config](../inputs/execution_records/full_config.json) · [Tool details](../inputs/execution_records/tool_details.json) · [File inventory and SHA-256](../inputs/execution_records/run_files.csv)

## Preparation and inputs

Objective: framework-conditioned, epitope-directed design of paired VH/VL candidates (scFv output) against human PD-L1 with H5/35TL as comparator only

Original input provenance, chain/mask contracts and readiness records are retained below. Current file locations, sizes and full SHA-256 values are in `../inputs/execution_records/run_files.csv`.

```json
[
  {
    "path": "src/task_002_pdl1_epitope_targeted_scfv_design/run_002_rf_antibody/inputs/antibody_framework_placed.pdb",
    "sha256": "c23013a8752488b0e5f22825361d4c5879796d23e4e4b7880a49e0a58801d2a1",
    "provenance": "Existing saved task input"
  },
  {
    "path": "src/task_002_pdl1_epitope_targeted_scfv_design/run_002_rf_antibody/inputs/antigen_pdl1_Vdomain.pdb",
    "sha256": "79612be97be4785cc9e83d2c6e1a33beffc8d5db052e477849daa0c327902768",
    "provenance": "Existing saved task input"
  },
  {
    "path": "src/task_002_pdl1_epitope_targeted_scfv_design/run_002_rf_antibody/inputs/eval_35TL_experimental.pdb",
    "sha256": "cffc4623e7139143f59ce1b10b1fc889851e2b9a182300a6a2c838c463808406",
    "provenance": "Existing saved task input"
  },
  {
    "path": "src/task_002_pdl1_epitope_targeted_scfv_design/run_002_rf_antibody/inputs/placed_complex_framework.pdb",
    "sha256": "59caf0aa38ffa4acaed1c7eec16e911e3c120f5f8e078b3fbac81ff917a2f8d3",
    "provenance": "Existing saved task input"
  },
  {
    "path": "src/task_002_pdl1_epitope_targeted_scfv_design/run_002_rf_antibody/inputs/pose_donor_5X8M_durvalumab.pdb",
    "sha256": "72c7afc6526ca5695246c76c533b3864666d1216623e487bf707afb02dcd64af",
    "provenance": "Existing saved task input"
  },
  {
    "path": "src/task_002_pdl1_epitope_targeted_scfv_design/run_002_rf_antibody/inputs/prep_record.json",
    "sha256": "e35dd37c551eba0cb254732b883461aa8f90f0ab8c51d5be7d64c5ae6fe9adb8",
    "provenance": "Existing saved task input"
  },
  {
    "path": "src/task_002_pdl1_epitope_targeted_scfv_design/run_002_rf_antibody/inputs/study_framework_scfv.pdb",
    "sha256": "cbdb24aac3fe9b15b738816421fa02b422d341fde5ccd6ffb12a763763516a93",
    "provenance": "Existing saved task input"
  },
  {
    "path": "src/task_002_pdl1_epitope_targeted_scfv_design/run_002_rf_antibody/inputs/study_target_pdl1_seedcomplex.pdb",
    "sha256": "d7351a441c34cbb9c799798425295106f25beca45428f96d8d8a8f63c586e132",
    "provenance": "Existing saved task input"
  }
]
```

## Recorded outcome

```json
{
  "status": "completed",
  "inventory_rows": 1,
  "packaged_at": "2026-11-15T11:14:35+00:00",
  "historical_submission_attempts_recovered": 6
}
```

## Workflow steps and tools

Settings shown below are recorded values. Exact submitted arguments, payloads, resources, responses, validation and fallback details remain in `../inputs/execution_records/tool_details.json`. Historical output names are retained as evidence; use `run_files.csv` for current saved locations.

## W3_generation_and_evaluation: RF-Antibody generation, excluded outputs

State: **completed**. Dependencies: `[]`.

Acceptance/checks: Original task constraints and the saved route-specific success/exclusion records.

### C01: rfdiffusion_proteinmpnn

Purpose: task002_rfab_pd11_run1

Source: **boltzmann**; recorded state: **unknown**.

Exact record: [tool_details.json](../inputs/execution_records/tool_details.json) → `/records/C01`. Original call ID: `call_-7077301742332803893:subcall:0`.

Identifier/version: `rfdiffusion_proteinmpnn`.

**Inputs**

```json
{
  "saved_request": "src/task_002_pdl1_epitope_targeted_scfv_design/run_002_rf_antibody/inputs/submitted_requests/message_18023_subcall_0.json",
  "sha256": "3480ddb3e4b8c38d68fbf9fab5a5a8138d09628a7a3f1272c657684e75385046"
}
```

**Parameters recorded for this call**

| Setting | Value / exact saved value | Recorded explanation |
| --- | --- | --- |
| `antibody_pdb_path` | `users/68d12a5de5b6a2fdc0e3c443/1794655276746/antibody_framework_placed.pdb` | Field meaning: Antibody structure input location.  |
| `antigen_pdb_path` | `users/68d12a5de5b6a2fdc0e3c443/1794655271659/antigen_pdl1_Vdomain.pdb` | Field meaning: Antigen structure input location.  |
| `num_sequences` | `8` | Field meaning: Number of sequences requested.  |

**Execution and identifiers**

```json
{
  "session_id": "20261114_110304_1c10da",
  "message_id": 18023,
  "tool_call_id": "call_-7077301742332803893",
  "subcall_index": 0,
  "timestamp_utc": "2026-11-14T15:57:14.342556+00:00",
  "experiment_name": "task002_rfab_pd11_run1",
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

### C02: rfdiffusion_proteinmpnn

Purpose: task002_rfab_pdl1_run1

Source: **boltzmann**; recorded state: **not_started**.

Exact record: [tool_details.json](../inputs/execution_records/tool_details.json) → `/records/C02`. Original call ID: `call_-7077311912815356043:subcall:0`.

Identifier/version: `rfdiffusion_proteinmpnn`.

**Inputs**

```json
{
  "saved_request": "src/task_002_pdl1_epitope_targeted_scfv_design/run_002_rf_antibody/inputs/submitted_requests/message_18026_subcall_0.json",
  "sha256": "93ed645bf9c62d84e7d7ff63ba1fe3ad03007474cb9bca7e6144228c39171338"
}
```

**Parameters recorded for this call**

| Setting | Value / exact saved value | Recorded explanation |
| --- | --- | --- |
| `antibody_pdb_path` | `users/68d12a5de5b6a2fdc0e3c443/1794655276746/antibody_framework_placed.pdb` | Field meaning: Antibody structure input location.  |
| `antigen_pdb_path` | `users/68d12a5de5b6a2fdc0e3c443/1794655271659/antigen_pdl1_Vdomain.pdb` | Field meaning: Antigen structure input location.  |
| `num_sequences` | `8` | Field meaning: Number of sequences requested.  |

**Execution and identifiers**

```json
{
  "session_id": "20261114_110304_1c10da",
  "message_id": 18026,
  "tool_call_id": "call_-7077311912815356043",
  "subcall_index": 0,
  "timestamp_utc": "2026-11-14T15:57:18.441285+00:00",
  "experiment_name": "task002_rfab_pdl1_run1",
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

### C03: rfdiffusion_proteinmpnn

Purpose: task002_rfab_pdl1_run1

Source: **boltzmann**; recorded state: **not_started**.

Exact record: [tool_details.json](../inputs/execution_records/tool_details.json) → `/records/C03`. Original call ID: `call_-7077301673613326577:subcall:0`.

Identifier/version: `rfdiffusion_proteinmpnn`.

**Inputs**

```json
{
  "saved_request": "src/task_002_pdl1_epitope_targeted_scfv_design/run_002_rf_antibody/inputs/submitted_requests/message_18030_subcall_0.json",
  "sha256": "4ce0df59628174647568ce3837d1d9ea4b36b16bef2c6d9a1db1fbc069a900f2"
}
```

**Parameters recorded for this call**

| Setting | Value / exact saved value | Recorded explanation |
| --- | --- | --- |
| `antibody_pdb_path` | `users/68d12a5de5b6a2fdc0e3c443/1794655276746/antibody_framework_placed.pdb` | Field meaning: Antibody structure input location.  |
| `antibody_type` | `scfv` | Field meaning: Requested antibody format/type.  |
| `antigen_pdb_path` | `users/68d12a5de5b6fdc0e3c443/1794655271659/antigen_pdl1_Vdomain.pdb` | Field meaning: Antigen structure input location.  |
| `num_sequences` | `8` | Field meaning: Number of sequences requested.  |

**Execution and identifiers**

```json
{
  "session_id": "20261114_110304_1c10da",
  "message_id": 18030,
  "tool_call_id": "call_-7077301673613326577",
  "subcall_index": 0,
  "timestamp_utc": "2026-11-14T15:57:22.343994+00:00",
  "experiment_name": "task002_rfab_pdl1_run1",
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

### C04: rfdiffusion_proteinmpnn

Purpose: task002_rfab_pdl1_run1

Source: **boltzmann**; recorded state: **unknown**.

Exact record: [tool_details.json](../inputs/execution_records/tool_details.json) → `/records/C04`. Original call ID: `call_-7077303529039196934:subcall:0`.

Identifier/version: `rfdiffusion_proteinmpnn`.

**Inputs**

```json
{
  "saved_request": "src/task_002_pdl1_epitope_targeted_scfv_design/run_002_rf_antibody/inputs/submitted_requests/message_18033_subcall_0.json",
  "sha256": "dc4bcb7799f34731f26686e45e7e4b5bdfffcb874eba1f5003ce36470b4b0246"
}
```

**Parameters recorded for this call**

| Setting | Value / exact saved value | Recorded explanation |
| --- | --- | --- |
| `antibody_pdb_path` | `users/68d12a5de5b6a2fdc0e3c443/1794655276746/antibody_framework_placed.pdb` | Field meaning: Antibody structure input location.  |
| `antibody_type` | `scFv` | Field meaning: Requested antibody format/type.  |
| `antigen_pdb_path` | `users/68d12a5de5b6a2fdc0e3c443/1794655271659/antigen_pdl1_Vdomain.pdb` | Field meaning: Antigen structure input location.  |
| `num_sequences` | `8` | Field meaning: Number of sequences requested.  |

**Execution and identifiers**

```json
{
  "session_id": "20261114_110304_1c10da",
  "message_id": 18033,
  "tool_call_id": "call_-7077303529039196934",
  "subcall_index": 0,
  "timestamp_utc": "2026-11-14T15:57:26.413184+00:00",
  "experiment_name": "task002_rfab_pdl1_run1",
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

### C05: rfdiffusion_proteinmpnn

Purpose: task002_rfab_pdl1_run1

Source: **boltzmann**; recorded state: **approval_required**.

Exact record: [tool_details.json](../inputs/execution_records/tool_details.json) → `/records/C05`. Original call ID: `call_-7077287689199807721:subcall:0`.

Identifier/version: `rfdiffusion_proteinmpnn`.

**Inputs**

```json
{
  "saved_request": "src/task_002_pdl1_epitope_targeted_scfv_design/run_002_rf_antibody/inputs/submitted_requests/message_18043_subcall_0.json",
  "sha256": "c4b6e4197f0d4c51c07287516f5c85c9efd177aaf6d1d761b29d8bf9be3b8365"
}
```

**Parameters recorded for this call**

| Setting | Value / exact saved value | Recorded explanation |
| --- | --- | --- |
| `antibody_pdb_path` | `users/68d12a5de5b6a2fdc0e3c443/1794655276746/antibody_framework_placed.pdb` | Field meaning: Antibody structure input location.  |
| `antibody_type` | `antibody` | Field meaning: Requested antibody format/type.  |
| `antigen_pdb_path` | `users/68d12a5de5b6a2fdc0e3c443/1794655271659/antigen_pdl1_Vdomain.pdb` | Field meaning: Antigen structure input location.  |
| `num_sequences` | `8` | Field meaning: Number of sequences requested.  |

**Execution and identifiers**

```json
{
  "session_id": "20261114_110304_1c10da",
  "message_id": 18043,
  "tool_call_id": "call_-7077287689199807721",
  "subcall_index": 0,
  "timestamp_utc": "2026-11-14T15:57:44.050333+00:00",
  "experiment_name": "task002_rfab_pdl1_run1",
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

### C06: rfdiffusion_proteinmpnn

Purpose: task002_rfab_pdl1_run1

Source: **boltzmann**; recorded state: **accepted**.

Exact record: [tool_details.json](../inputs/execution_records/tool_details.json) → `/records/C06`. Original call ID: `call_-7077401351214330016:subcall:0`.

Identifier/version: `rfdiffusion_proteinmpnn`.

**Inputs**

```json
{
  "saved_request": "src/task_002_pdl1_epitope_targeted_scfv_design/run_002_rf_antibody/inputs/submitted_requests/message_18047_subcall_0.json",
  "sha256": "1192bd6b95753167f7a91b664394303b3e08edb597d410cfdecaccc6741380a6"
}
```

**Parameters recorded for this call**

| Setting | Value / exact saved value | Recorded explanation |
| --- | --- | --- |
| `antibody_pdb_path` | `users/68d12a5de5b6a2fdc0e3c443/1794655276746/antibody_framework_placed.pdb` | Field meaning: Antibody structure input location.  |
| `antibody_type` | `antibody` | Field meaning: Requested antibody format/type.  |
| `antigen_pdb_path` | `users/68d12a5de5b6a2fdc0e3c443/1794655271659/antigen_pdl1_Vdomain.pdb` | Field meaning: Antigen structure input location.  |
| `num_sequences` | `8` | Field meaning: Number of sequences requested.  |

**Execution and identifiers**

```json
{
  "session_id": "20261114_110304_1c10da",
  "message_id": 18047,
  "tool_call_id": "call_-7077401351214330016",
  "subcall_index": 0,
  "timestamp_utc": "2026-11-14T15:57:48.530937+00:00",
  "doc_id": "6af884fc9de6b44b075d8594",
  "experiment_name": "task002_rfab_pdl1_run1",
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
