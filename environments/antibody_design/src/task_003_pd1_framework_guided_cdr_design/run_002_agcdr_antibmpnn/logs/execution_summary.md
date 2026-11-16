# Execution summary — run_002_agcdr_antibmpnn

Task: `task_003_pd1_framework_guided_cdr_design`. Saved run status: **completed**.

Record organization updated 2026-11-16. This is a retrospective presentation of saved execution evidence.

[Compact config](../../../../results/task_003_pd1_framework_guided_cdr_design/run_002_agcdr_antibmpnn/run.json) · [Workflow](../workflow.md) · [Activity log](agent_scientist_log.md) · [Exact original config](../inputs/execution_records/full_config.json) · [Tool details](../inputs/execution_records/tool_details.json) · [File inventory and SHA-256](../inputs/execution_records/run_files.csv)

## Preparation and inputs

Objective: Diversify CDR backbones on the fixed framework (agcdr_diff), redesign CDR sequences on each backbone (AntiBMPNN), enforce frozen gates, select 5 diverse candidates + H965 control, screen with Boltz2 and property predictors

Original input provenance, chain/mask contracts and readiness records are retained below. Current file locations, sizes and full SHA-256 values are in `../inputs/execution_records/run_files.csv`.

```json
[
  {
    "input": "fv_scaffold.pdb",
    "source": "as run_001",
    "path": "src/task_003_pd1_framework_guided_cdr_design/run_002_agcdr_antibmpnn/inputs/fv_scaffold.pdb",
    "sha256": "47dbf3452229f4d663f6defda2076071f33a8a409041ca119b70013a3c4a1218",
    "historical_path": "inputs/fv_scaffold.pdb",
    "saved_sha256": "47dbf3452229f4d663f6defda2076071f33a8a409041ca119b70013a3c4a1218"
  },
  {
    "input": "pd1_antigen.pdb",
    "source": "as run_001",
    "path": "src/task_003_pd1_framework_guided_cdr_design/run_002_agcdr_antibmpnn/inputs/pd1_antigen.pdb",
    "sha256": "1aecd0d0b0cf5ad55da4abaa93cbeaed84b4f19a0815aac3aba3ec3f8032c4a4",
    "historical_path": "inputs/pd1_antigen.pdb",
    "saved_sha256": "1aecd0d0b0cf5ad55da4abaa93cbeaed84b4f19a0815aac3aba3ec3f8032c4a4"
  },
  {
    "input": "agcdr_backbones.zip",
    "source": "20 renumbered Fv backbones from agcdr_diff output (H:117/L:108 per-residue numbering)",
    "path": "src/task_003_pd1_framework_guided_cdr_design/run_002_agcdr_antibmpnn/inputs/candidates/agcdr_backbones.zip",
    "saved_path_status": "not_resolved_from_historical_reference",
    "historical_path": "candidates/agcdr_backbones.zip",
    "saved_sha256": "830379782dd1acd6b922096615940c401c181c5b9462e59e7017a0bd42ded938"
  },
  {
    "input": "properties_input.csv",
    "source": "5 selected candidates + H965 control",
    "path": "src/task_003_pd1_framework_guided_cdr_design/run_002_agcdr_antibmpnn/inputs/properties_input.csv",
    "sha256": "4edc554748fafddc76328974341f3e5a93d12fe60639d2a024cb573c08d4c0b8",
    "historical_path": "inputs/properties_input.csv",
    "saved_sha256": "4edc554748fafddc76328974341f3e5a93d12fe60639d2a024cb573c08d4c0b8"
  }
]
```

## Recorded outcome

```json
{
  "generated": 160,
  "gate_pass": 115,
  "selected": 5,
  "screened": 6,
  "top_candidate": "PD1T3-019 ipTM PD1:VH 0.945 vs H965 control 0.895 (same-predictor comparison; not affinity)",
  "last_update": "2026-11-14T16:10:00Z"
}
```

## Workflow steps and tools

Settings shown below are recorded values. Exact submitted arguments, payloads, resources, responses, validation and fallback details remain in `../inputs/execution_records/tool_details.json`. Historical output names are retained as evidence; use `run_files.csv` for current saved locations.

## S1_backbone_diversification: Sample CDR backbone conformations with framework+antigen preserved

State: **completed**. Dependencies: `[]`.

Acceptance/checks: Terminal job; 20 backbone samples; framework preserved

### C01: agcdr_diff (Antibody RFD3)

Purpose: CDR backbone diffusion conditioned on Fv scaffold + PD-1 antigen

Source: **boltzmann**; recorded state: **completed**.

Exact record: [tool_details.json](../inputs/execution_records/tool_details.json) → `/records/C01`. Original call ID: `run_002_agcdr_antibmpnn-S1-01`.

Identifier/version: `boltzmann job agcdr_diff, doc 6af879a3d29658acc304e059`.

**Inputs**

```json
{
  "saved_request": "src/task_003_pd1_framework_guided_cdr_design/run_002_agcdr_antibmpnn/inputs/submitted_requests/message_17379_subcall_0.json",
  "sha256": "88fb9f98e1396f2246584bb171783adcd52bfdb7bc480fe62a1f91d53c4382a1"
}
```

**Parameters recorded for this call**

| Setting | Value / exact saved value | Recorded explanation |
| --- | --- | --- |
| `num_samples` | `20` | 20 backbone samples within budget |
| `num_steps` | `50` | 50 diffusion steps (platform-recommended) |

**Execution and identifiers**

```json
{
  "job_id": "6af879a3d29658acc304e059",
  "runtime": "platform"
}
```

**Returned outputs / historical output names**

```json
{
  "backbones": 20,
  "cdr_rmsd_vs_scaffold_A": 10.9,
  "framework_preserved": true
}
```

**Validation and checks**

```json
"Reports + structures downloaded; framework residues unchanged"
```

Original submission records: `C01.R01`. These are evidence for this call, not additional completed jobs.

### C01.R01: agcdr_diff

Purpose: See the stage purpose.

Source: **boltzmann**; recorded state: **Success**.

Exact record: [tool_details.json](../inputs/execution_records/tool_details.json) → `/records/C01.R01`. Original call ID: `call_-7077345860236867814:subcall:0`.

Identifier/version: `agcdr_diff`.

**Inputs**

```json
{
  "saved_request": "src/task_003_pd1_framework_guided_cdr_design/run_002_agcdr_antibmpnn/inputs/submitted_requests/message_17379_subcall_0.json",
  "sha256": "88fb9f98e1396f2246584bb171783adcd52bfdb7bc480fe62a1f91d53c4382a1"
}
```

**Parameters recorded for this call**

| Setting | Value / exact saved value | Recorded explanation |
| --- | --- | --- |
| `antibody_pdb_path` | `users/680f678c1b1d883c92aa706c/1794668173943/fv_scaffold.pdb` | Field meaning: Antibody structure input location.  |
| `antigen_pdb_path` | `users/680f678c1b1d883c92aa706c/1794668182656/pd1_antigen.pdb` | Field meaning: Antigen structure input location.  |
| `num_samples` | `20` | Field meaning: Number of samples requested.  |
| `num_steps` | `50` | Field meaning: Requested sampling-step count.  |

**Execution and identifiers**

```json
{
  "session_id": "20261114_110401_625a94",
  "message_id": 17379,
  "tool_call_id": "call_-7077345860236867814",
  "subcall_index": 0,
  "timestamp_utc": "2026-11-14T15:09:22.882422+00:00",
  "doc_id": "6af879a3d29658acc304e059",
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

## S2_antibmpnn_on_backbones: Design CDR sequences on each diversified backbone

State: **completed**. Dependencies: `["S1_backbone_diversification"]`.

Acceptance/checks: Terminal job; mask verified position-by-position; gates enforced

### C02: AntiBMPNN

Purpose: CDR-masked sequence design on 20 agcdr backbones

Source: **boltzmann**; recorded state: **completed**.

Exact record: [tool_details.json](../inputs/execution_records/tool_details.json) → `/records/C02`. Original call ID: `run_002_agcdr_antibmpnn-S2-01`.

Identifier/version: `boltzmann job AntiBMPNN, doc 6af87c36445ae94313c3b280 (first attempt 6af87a62445ae94313c3b0f1 failed on per-atom numbering)`.

**Inputs**

```json
null
```

**Parameters recorded for this call**

| Setting | Value / exact saved value | Recorded explanation |
| --- | --- | --- |
| `generation_count` | `8` | 8 sequences per backbone x 20 = 160 |
| `mask_H` | `26-32,52-57,98-105 (H1/H2/H3)` | Field meaning: Recorded heavy-chain mask.  |
| `mask_L` | `24-34,50-56,89-98 (L1/L2/L3)` | Field meaning: Recorded light-chain mask.  |

**Execution and identifiers**

```json
{
  "job_id": "6af87c36445ae94313c3b280"
}
```

**Returned outputs / historical output names**

```json
{
  "sequences": 160,
  "gate_pass": 115
}
```

**Validation and checks**

```json
"Mask verified 160/160 position-by-position; FR byte-identity asserted per row; no-Cys/length/novelty gates applied"
```

**Failures, retries and fallback**

```json
{
  "prior_call": "6af87a62445ae94313c3b0f1",
  "observed_error": "per-atom residue numbering made 468 'residues'",
  "recovery": "renumbered per-residue (H:117/L:108) and resubmitted",
  "reason_for_switch": "platform expects residue-indexed positions",
  "protocol_differences": "none scientific; numbering only"
}
```

Original submission records: `C02.R01`, `C02.R02`. These are evidence for this call, not additional completed jobs.

### C02.R01: AntiBMPNN

Purpose: See the stage purpose.

Source: **boltzmann**; recorded state: **failed**.

Exact record: [tool_details.json](../inputs/execution_records/tool_details.json) → `/records/C02.R01`. Original call ID: `call_-7077345413560269194:subcall:0`.

Identifier/version: `AntiBMPNN`.

**Inputs**

```json
{
  "saved_request": "src/task_003_pd1_framework_guided_cdr_design/run_002_agcdr_antibmpnn/inputs/submitted_requests/message_17424_subcall_0.json",
  "sha256": "d987b0770125378ccb84b5662f4f72b5d08e6dee77e3219f0a0d386d645f0474"
}
```

**Parameters recorded for this call**

| Setting | Value / exact saved value | Recorded explanation |
| --- | --- | --- |
| `chains_to_design` | `["H", "L"]` | Field meaning: Chains selected in the submitted design request.  |
| `generation_count` | `8` | Field meaning: Number of samples requested in that call.  |
| `input_path` | `users/680f678c1b1d883c92aa706c/1794669148021/agcdr_backbones.zip` | Field meaning: Tool-specific input field; it may contain a file location or sequence payload.  |
| `residue_positions_to_design` | `{"H": "26-32,52-57,99-106", "L": "24-34,50-56,89-98"}` | Field meaning: Per-chain residue positions supplied in the exact request.  |

**Execution and identifiers**

```json
{
  "session_id": "20261114_110401_625a94",
  "message_id": 17424,
  "tool_call_id": "call_-7077345413560269194",
  "subcall_index": 0,
  "timestamp_utc": "2026-11-14T15:12:33.813948+00:00",
  "doc_id": "6af87a62445ae94313c3b0f1",
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

### C02.R02: AntiBMPNN

Purpose: See the stage purpose.

Source: **boltzmann**; recorded state: **Success**.

Exact record: [tool_details.json](../inputs/execution_records/tool_details.json) → `/records/C02.R02`. Original call ID: `call_-7077349983405466191:subcall:0`.

Identifier/version: `AntiBMPNN`.

**Inputs**

```json
{
  "saved_request": "src/task_003_pd1_framework_guided_cdr_design/run_002_agcdr_antibmpnn/inputs/submitted_requests/message_17492_subcall_0.json",
  "sha256": "761577b153a33c4849f023af79d5bf507037289ff320dcc4c136f6abf478b364"
}
```

**Parameters recorded for this call**

| Setting | Value / exact saved value | Recorded explanation |
| --- | --- | --- |
| `chains_to_design` | `["H", "L"]` | Field meaning: Chains selected in the submitted design request.  |
| `generation_count` | `8` | Field meaning: Number of samples requested in that call.  |
| `input_path` | `users/680f678c1b1d883c92aa706c/1794669616517/agcdr_backbones.zip` | Field meaning: Tool-specific input field; it may contain a file location or sequence payload.  |
| `residue_positions_to_design` | `{"H": "26-32,52-57,99-106", "L": "24-34,50-56,89-98"}` | Field meaning: Per-chain residue positions supplied in the exact request.  |

**Execution and identifiers**

```json
{
  "session_id": "20261114_110401_625a94",
  "message_id": 17492,
  "tool_call_id": "call_-7077349983405466191",
  "subcall_index": 0,
  "timestamp_utc": "2026-11-14T15:20:21.836008+00:00",
  "doc_id": "6af87c36445ae94313c3b280",
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

## S3_selection: Select 5 diverse candidates for screening (frozen rule)

State: **completed**. Dependencies: `["S2_antibmpnn_on_backbones"]`.

Acceptance/checks: Rule pre-registered; min pairwise CDR Hamming >= 32/60

### C03: select_screening.py

Purpose: Medoid-seeded greedy max-min CDR Hamming selection

Source: **open_source**; recorded state: **completed**.

Exact record: [tool_details.json](../inputs/execution_records/tool_details.json) → `/records/C03`. Original call ID: `run_002_agcdr_antibmpnn-S3-01`.

Identifier/version: `local code: code/select_screening.py`.

**Inputs**

```json
{
  "pool": "candidates/agcdr_pool.json (115 eligible)"
}
```


**Returned outputs / historical output names**

```json
{
  "selected": 5,
  "min_pairwise_hamming": 32,
  "output": "candidates/screening_selection.json"
}
```

**Validation and checks**

```json
"Selection executed before any Boltz2 score existed (rule frozen in configs/workflow.md)"
```

## S4_boltz2_screening: Complex plausibility per selected candidate + H965 control

State: **completed**. Dependencies: `["S3_selection"]`.

Acceptance/checks: 6 terminal Boltz2 jobs; confidence + models retrieved

### C04: Boltz2

Purpose: PD-1:VH and PD-1:VL pairwise complex predictions per submission

Source: **boltzmann**; recorded state: **completed**.

Exact record: [tool_details.json](../inputs/execution_records/tool_details.json) → `/records/C04`. Original call ID: `run_002_agcdr_antibmpnn-S4-01..06`.

Identifier/version: `docs 6af87d71445ae94313c3b729 (H965 control), 6af87d939030bff416447c9a (cand1), 6af87d99239a6b9f38bebe2d (cand2), 6af87da39030bff416447cb6 (cand3), 6af87da99de6b44b075d81f2 (cand4), 6af87db19850a93adf67d249 (cand5)`.

**Inputs**

```json
null
```

**Parameters recorded for this call**

| Setting | Value / exact saved value | Recorded explanation |
| --- | --- | --- |
| `sequences` | `PD-1 + candidate VH/VL (control uses H965 VH/VL; control antigen 33-145 S93 form, candidates 33-134 C93 form — disclosed)` | Field meaning: Protein sequence inputs; exact values are preserved in the evidence.  |

**Execution and identifiers**

```json
{
  "jobs": 6,
  "all_terminal": true
}
```

**Returned outputs / historical output names**

```json
{
  "per_job": "PD1:VH + PD1:VL predictions (models, confidence JSON, PAE/plddt npz)"
}
```

**Validation and checks**

```json
"All 6 archives downloaded within signed-URL windows; chain identities verified by length and sequence prefix"
```

**Failures, retries and fallback**

```json
{
  "observed_error": "boltzmann_download 400 on outputs.zip; signed URLs expire 300 s",
  "recovery": "status re-poll + immediate curl; connector 400 recorded, not silently absorbed",
  "reason_for_switch": "artifact retrieval",
  "protocol_differences": "none"
}
```

Original submission records: `C04.R01`, `C04.R02`, `C04.R03`, `C04.R04`, `C04.R05`, `C04.R06`. These are evidence for this call, not additional completed jobs.

### C04.R01: Boltz2

Purpose: See the stage purpose.

Source: **boltzmann**; recorded state: **Success**.

Exact record: [tool_details.json](../inputs/execution_records/tool_details.json) → `/records/C04.R01`. Original call ID: `call_-7077325519271749134:subcall:0`.

Identifier/version: `Boltz2`.

**Inputs**

```json
{
  "saved_request": "src/task_003_pd1_framework_guided_cdr_design/run_002_agcdr_antibmpnn/inputs/submitted_requests/message_17555_subcall_0.json",
  "sha256": "037e0f318a2d956fa333616d686b308bb4fd66ca838f56bcd59eed7c3f767a11"
}
```

**Parameters recorded for this call**

| Setting | Value / exact saved value | Recorded explanation |
| --- | --- | --- |
| `Protein_Sequences` | `{"record": "C04.R01", "pointer": "/parameters/Protein_Sequences", "summary": "sequence lengths: 113, 117, 108"}` | Field meaning: Submitted protein sequence list; order is preserved in the exact request.  |

**Execution and identifiers**

```json
{
  "session_id": "20261114_110401_625a94",
  "message_id": 17555,
  "tool_call_id": "call_-7077325519271749134",
  "subcall_index": 0,
  "timestamp_utc": "2026-11-14T15:25:37.129487+00:00",
  "doc_id": "6af87d71445ae94313c3b729",
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

### C04.R02: Boltz2

Purpose: See the stage purpose.

Source: **boltzmann**; recorded state: **Success**.

Exact record: [tool_details.json](../inputs/execution_records/tool_details.json) → `/records/C04.R02`. Original call ID: `call_-7077332734816811866:subcall:0`.

Identifier/version: `Boltz2`.

**Inputs**

```json
{
  "saved_request": "src/task_003_pd1_framework_guided_cdr_design/run_002_agcdr_antibmpnn/inputs/submitted_requests/message_17573_subcall_0.json",
  "sha256": "97f59f205e561c699bd22f483b7dd97ca502b8cd71b58f5df7e886738b662350"
}
```

**Parameters recorded for this call**

| Setting | Value / exact saved value | Recorded explanation |
| --- | --- | --- |
| `Protein_Sequences` | `{"record": "C04.R02", "pointer": "/parameters/Protein_Sequences", "summary": "sequence lengths: 102, 117, 108"}` | Field meaning: Submitted protein sequence list; order is preserved in the exact request.  |

**Execution and identifiers**

```json
{
  "session_id": "20261114_110401_625a94",
  "message_id": 17573,
  "tool_call_id": "call_-7077332734816811866",
  "subcall_index": 0,
  "timestamp_utc": "2026-11-14T15:26:11.758358+00:00",
  "doc_id": "6af87d939030bff416447c9a",
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

### C04.R03: Boltz2

Purpose: See the stage purpose.

Source: **boltzmann**; recorded state: **Success**.

Exact record: [tool_details.json](../inputs/execution_records/tool_details.json) → `/records/C04.R03`. Original call ID: `call_-7077324935156196439:subcall:0`.

Identifier/version: `Boltz2`.

**Inputs**

```json
{
  "saved_request": "src/task_003_pd1_framework_guided_cdr_design/run_002_agcdr_antibmpnn/inputs/submitted_requests/message_17577_subcall_0.json",
  "sha256": "af872b22d10699cd17ea797e53b9e13702de2135d2461e2635c07f3fd3d8cdd8"
}
```

**Parameters recorded for this call**

| Setting | Value / exact saved value | Recorded explanation |
| --- | --- | --- |
| `Protein_Sequences` | `{"record": "C04.R03", "pointer": "/parameters/Protein_Sequences", "summary": "sequence lengths: 102, 117, 108"}` | Field meaning: Submitted protein sequence list; order is preserved in the exact request.  |

**Execution and identifiers**

```json
{
  "session_id": "20261114_110401_625a94",
  "message_id": 17577,
  "tool_call_id": "call_-7077324935156196439",
  "subcall_index": 0,
  "timestamp_utc": "2026-11-14T15:26:17.676409+00:00",
  "doc_id": "6af87d99239a6b9f38bebe2d",
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

### C04.R04: Boltz2

Purpose: See the stage purpose.

Source: **boltzmann**; recorded state: **Success**.

Exact record: [tool_details.json](../inputs/execution_records/tool_details.json) → `/records/C04.R04`. Original call ID: `call_-7077339881642386245:subcall:0`.

Identifier/version: `Boltz2`.

**Inputs**

```json
{
  "saved_request": "src/task_003_pd1_framework_guided_cdr_design/run_002_agcdr_antibmpnn/inputs/submitted_requests/message_17579_subcall_0.json",
  "sha256": "92f0cb7935622106f49abef069c6919aa692e91520410c191b7791afc028467c"
}
```

**Parameters recorded for this call**

| Setting | Value / exact saved value | Recorded explanation |
| --- | --- | --- |
| `Protein_Sequences` | `{"record": "C04.R04", "pointer": "/parameters/Protein_Sequences", "summary": "sequence lengths: 102, 117, 108"}` | Field meaning: Submitted protein sequence list; order is preserved in the exact request.  |

**Execution and identifiers**

```json
{
  "session_id": "20261114_110401_625a94",
  "message_id": 17579,
  "tool_call_id": "call_-7077339881642386245",
  "subcall_index": 0,
  "timestamp_utc": "2026-11-14T15:26:27.172600+00:00",
  "doc_id": "6af87da39030bff416447cb6",
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

### C04.R05: Boltz2

Purpose: See the stage purpose.

Source: **boltzmann**; recorded state: **Success**.

Exact record: [tool_details.json](../inputs/execution_records/tool_details.json) → `/records/C04.R05`. Original call ID: `call_-7077341977586425933:subcall:0`.

Identifier/version: `Boltz2`.

**Inputs**

```json
{
  "saved_request": "src/task_003_pd1_framework_guided_cdr_design/run_002_agcdr_antibmpnn/inputs/submitted_requests/message_17583_subcall_0.json",
  "sha256": "47ae3a379cb6d101cbc0b182bd9776d94454bca219d81b2d9dafd4584b9d0fd1"
}
```

**Parameters recorded for this call**

| Setting | Value / exact saved value | Recorded explanation |
| --- | --- | --- |
| `Protein_Sequences` | `{"record": "C04.R05", "pointer": "/parameters/Protein_Sequences", "summary": "sequence lengths: 102, 117, 108"}` | Field meaning: Submitted protein sequence list; order is preserved in the exact request.  |

**Execution and identifiers**

```json
{
  "session_id": "20261114_110401_625a94",
  "message_id": 17583,
  "tool_call_id": "call_-7077341977586425933",
  "subcall_index": 0,
  "timestamp_utc": "2026-11-14T15:26:33.405726+00:00",
  "doc_id": "6af87da99de6b44b075d81f2",
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

### C04.R06: Boltz2

Purpose: See the stage purpose.

Source: **boltzmann**; recorded state: **Success**.

Exact record: [tool_details.json](../inputs/execution_records/tool_details.json) → `/records/C04.R06`. Original call ID: `call_-7077331910183088437:subcall:0`.

Identifier/version: `Boltz2`.

**Inputs**

```json
{
  "saved_request": "src/task_003_pd1_framework_guided_cdr_design/run_002_agcdr_antibmpnn/inputs/submitted_requests/message_17589_subcall_0.json",
  "sha256": "64ebf7f3b816e5c00a05774859b9b03831e7e590a1eb305b64d51a4d5e83f84b"
}
```

**Parameters recorded for this call**

| Setting | Value / exact saved value | Recorded explanation |
| --- | --- | --- |
| `Protein_Sequences` | `{"record": "C04.R06", "pointer": "/parameters/Protein_Sequences", "summary": "sequence lengths: 102, 117, 108"}` | Field meaning: Submitted protein sequence list; order is preserved in the exact request.  |

**Execution and identifiers**

```json
{
  "session_id": "20261114_110401_625a94",
  "message_id": 17589,
  "tool_call_id": "call_-7077331910183088437",
  "subcall_index": 0,
  "timestamp_utc": "2026-11-14T15:26:40.909146+00:00",
  "doc_id": "6af87db19850a93adf67d249",
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

## S5_properties: Thermal stability, solubility, CDR prediction on 5 candidates + H965

State: **completed**. Dependencies: `["S3_selection"]`.

Acceptance/checks: 3 terminal property jobs

### C05: Antibody_Prediction (AB_PROP)

Purpose: Property prediction for candidates + control

Source: **boltzmann**; recorded state: **completed**.

Exact record: [tool_details.json](../inputs/execution_records/tool_details.json) → `/records/C05`. Original call ID: `run_002_agcdr_antibmpnn-S5-01..03`.

Identifier/version: `docs 6af87dd4d29658acc304e596 (Thermal_Stability_ESM), 6af87dda445ae94313c3b7bb (Solubility_ESM), 6af87ded445ae94313c3b850 (CDR_Prediction)`.

**Inputs**

```json
null
```


**Execution and identifiers**

```json
{
  "jobs": 3,
  "all_terminal": true
}
```

**Returned outputs / historical output names**

```json
{
  "csv": "output-{1,2,3}.csv"
}
```

**Validation and checks**

```json
"6 rows each (5 candidates + H965); CDR_Prediction CDRs consistent with design mask"
```

**Failures, retries and fallback**

```json
{
  "attempts": "submitted and rejected by enum validation"
}
```

Original submission records: `C05.R01`, `C05.R02`, `C05.R03`. These are evidence for this call, not additional completed jobs.

### C05.R01: Antibody_Prediction

Purpose: See the stage purpose.

Source: **boltzmann**; recorded state: **Success**.

Exact record: [tool_details.json](../inputs/execution_records/tool_details.json) → `/records/C05.R01`. Original call ID: `call_-7077338094935992575:subcall:0`.

Identifier/version: `Antibody_Prediction`.

**Inputs**

```json
{
  "saved_request": "src/task_003_pd1_framework_guided_cdr_design/run_002_agcdr_antibmpnn/inputs/submitted_requests/message_17610_subcall_0.json",
  "sha256": "d78e3578c13f2b35a5a5010e880cb5dda47cfeeb60a2cbfc4127aef816c7add3"
}
```

**Parameters recorded for this call**

| Setting | Value / exact saved value | Recorded explanation |
| --- | --- | --- |
| `dataPath` | `users/680f678c1b1d883c92aa706c/1794670032131/properties_input.csv` | Field meaning: Tool input-data location.  |
| `property_name` | `["Thermal_Stability_ESM"]` | Field meaning: Requested property model/output.  |
| `scheme` | `imgt` | Field meaning: Recorded residue-numbering scheme.  |

**Execution and identifiers**

```json
{
  "session_id": "20261114_110401_625a94",
  "message_id": 17610,
  "tool_call_id": "call_-7077338094935992575",
  "subcall_index": 0,
  "timestamp_utc": "2026-11-14T15:27:16.035003+00:00",
  "doc_id": "6af87dd4d29658acc304e596",
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

### C05.R02: Antibody_Prediction

Purpose: See the stage purpose.

Source: **boltzmann**; recorded state: **Success**.

Exact record: [tool_details.json](../inputs/execution_records/tool_details.json) → `/records/C05.R02`. Original call ID: `call_-7077337991856776849:subcall:0`.

Identifier/version: `Antibody_Prediction`.

**Inputs**

```json
{
  "saved_request": "src/task_003_pd1_framework_guided_cdr_design/run_002_agcdr_antibmpnn/inputs/submitted_requests/message_17619_subcall_0.json",
  "sha256": "c4417475f4cfa05636983ef636447c9ec3b80c06d68dcd00cc87744d4497ac6f"
}
```

**Parameters recorded for this call**

| Setting | Value / exact saved value | Recorded explanation |
| --- | --- | --- |
| `dataPath` | `users/680f678c1b1d883c92aa706c/1794670032131/properties_input.csv` | Field meaning: Tool input-data location.  |
| `property_name` | `["Solubility_ESM"]` | Field meaning: Requested property model/output.  |
| `scheme` | `imgt` | Field meaning: Recorded residue-numbering scheme.  |

**Execution and identifiers**

```json
{
  "session_id": "20261114_110401_625a94",
  "message_id": 17619,
  "tool_call_id": "call_-7077337991856776849",
  "subcall_index": 0,
  "timestamp_utc": "2026-11-14T15:27:22.005850+00:00",
  "doc_id": "6af87dda445ae94313c3b7bb",
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

### C05.R03: Antibody_Prediction

Purpose: See the stage purpose.

Source: **boltzmann**; recorded state: **Success**.

Exact record: [tool_details.json](../inputs/execution_records/tool_details.json) → `/records/C05.R03`. Original call ID: `call_-7077337991856780775:subcall:0`.

Identifier/version: `Antibody_Prediction`.

**Inputs**

```json
{
  "saved_request": "src/task_003_pd1_framework_guided_cdr_design/run_002_agcdr_antibmpnn/inputs/submitted_requests/message_17631_subcall_0.json",
  "sha256": "1e4e1395c59d7e8f2cfd21c6986780125ec7a6e227babfdb2e05df9f88a34ac8"
}
```

**Parameters recorded for this call**

| Setting | Value / exact saved value | Recorded explanation |
| --- | --- | --- |
| `dataPath` | `users/680f678c1b1d883c92aa706c/1794670032131/properties_input.csv` | Field meaning: Tool input-data location.  |
| `property_name` | `["CDR_Prediction"]` | Field meaning: Requested property model/output.  |
| `scheme` | `imgt` | Field meaning: Recorded residue-numbering scheme.  |

**Execution and identifiers**

```json
{
  "session_id": "20261114_110401_625a94",
  "message_id": 17631,
  "tool_call_id": "call_-7077337991856780775",
  "subcall_index": 0,
  "timestamp_utc": "2026-11-14T15:27:40.943404+00:00",
  "doc_id": "6af87ded445ae94313c3b850",
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
