# Execution summary — run_001_rf_antibody

Task: `task_003_pd1_framework_guided_cdr_design`. Saved run status: **completed**.

Record organization updated 2026-11-16. This is a retrospective presentation of saved execution evidence.

[Compact config](../../../../results/task_003_pd1_framework_guided_cdr_design/run_001_rf_antibody/run.json) · [Workflow](../workflow.md) · [Activity log](agent_scientist_log.md) · [Exact original config](../inputs/execution_records/full_config.json) · [Tool details](../inputs/execution_records/tool_details.json) · [File inventory and SHA-256](../inputs/execution_records/run_files.csv)

## Preparation and inputs

Objective: Redesign the six CDRs on the fixed paper Table-1 humanized framework (IGHV3-23*01/IGKV1-5*01 + IGHJ4/IGKJ1) against the human PD-1 ligand-binding interface, using the staged 5GGS-derived Fv scaffold, and compare computational evidence with the published anti-PD-1-H965 design.

Original input provenance, chain/mask contracts and readiness records are retained below. Current file locations, sizes and full SHA-256 values are in `../inputs/execution_records/run_files.csv`.

```json
[
  {
    "input": "framework_table1.json",
    "source": "paper Table 1 (PMC12815924)",
    "path": "src/task_003_pd1_framework_guided_cdr_design/run_001_rf_antibody/inputs/framework_table1.json",
    "sha256": "e6ded0abaae598983c81cdf74f0eea3561142827dcf43eb3b9d18d88f91842d3",
    "historical_path": "inputs/framework_table1.json",
    "saved_sha256": "e6ded0abaae598983c81cdf74f0eea3561142827dcf43eb3b9d18d88f91842d3"
  },
  {
    "input": "pd1_panel_published.json",
    "source": "Suppl. Table 7, MOESM1",
    "path": "src/task_003_pd1_framework_guided_cdr_design/run_001_rf_antibody/inputs/pd1_panel_published.json",
    "sha256": "7dafe11c8415eb504ee50ae724dedde10876047945fec645ca1e4107f23b6a44",
    "historical_path": "inputs/pd1_panel_published.json",
    "saved_sha256": "7dafe11c8415eb504ee50ae724dedde10876047945fec645ca1e4107f23b6a44"
  },
  {
    "input": "fv_scaffold.pdb",
    "source": "built from 5GGS chains A/B backbone with Table-1 FR identity (build_complex.py)",
    "path": "src/task_003_pd1_framework_guided_cdr_design/run_001_rf_antibody/inputs/fv_scaffold.pdb",
    "sha256": "47dbf3452229f4d663f6defda2076071f33a8a409041ca119b70013a3c4a1218",
    "prepared": true,
    "historical_path": "inputs/fv_scaffold.pdb",
    "saved_sha256": "47dbf3452229f4d663f6defda2076071f33a8a409041ca119b70013a3c4a1218"
  },
  {
    "input": "pd1_antigen.pdb",
    "source": "5GGS chain Z residues 33-134",
    "path": "src/task_003_pd1_framework_guided_cdr_design/run_001_rf_antibody/inputs/pd1_antigen.pdb",
    "sha256": "1aecd0d0b0cf5ad55da4abaa93cbeaed84b4f19a0815aac3aba3ec3f8032c4a4",
    "prepared": true,
    "historical_path": "inputs/pd1_antigen.pdb",
    "saved_sha256": "1aecd0d0b0cf5ad55da4abaa93cbeaed84b4f19a0815aac3aba3ec3f8032c4a4"
  },
  {
    "input": "pd1_ecd_33_134.fasta",
    "source": "UniProt Q15116 33-134",
    "path": "src/task_003_pd1_framework_guided_cdr_design/run_001_rf_antibody/inputs/pd1_ecd_33_134.fasta",
    "sha256": "78f534a06675419e5eebae44248268e14932f3624ceaa05ca7f7d29a30aff4c0",
    "historical_path": "inputs/pd1_ecd_33_134.fasta",
    "saved_sha256": "78f534a06675419e5eebae44248268e14932f3624ceaa05ca7f7d29a30aff4c0"
  }
]
```

## Recorded outcome

```json
{
  "generated": 40,
  "eligible": 0,
  "reason_zero": "Systematic 7-residue H2 window and FR/CDR junction edits vs the locked Table-1 framework; honest zero, gates not weakened",
  "last_update": "2026-11-14T16:10:00Z",
  "package_inventory_note": "Canonical table contains the 40 RF exclusions only; mixed historical inventory archived. Native chain sequences retained exactly."
}
```

## Workflow steps and tools

Settings shown below are recorded values. Exact submitted arguments, payloads, resources, responses, validation and fallback details remain in `../inputs/execution_records/tool_details.json`. Historical output names are retained as evidence; use `run_files.csv` for current saved locations.

## S1_input_staging: Stage verified inputs (framework, PD-1 antigen, published panel, interface definition)

State: **completed**. Dependencies: `[]`.

Acceptance/checks: All inputs hash-recorded; framework byte-validated against all 10 published sequences

### C01: paper/supplement retrieval + parse_panel.py

Purpose: Extract Table-1 framework and Suppl. Table 7 panel programmatically

Source: **open_source**; recorded state: **completed**.

Exact record: [tool_details.json](../inputs/execution_records/tool_details.json) → `/records/C01`. Original call ID: `run_001_rf_antibody-S1-01`.

Identifier/version: `local code: code/parse_panel.py`.

**Inputs**

```json
{
  "paper_html": "pmc.ncbi.nlm.nih.gov/articles/PMC12815924/",
  "supplements": "41467_2025_67361_MOESM{1,2,3}_ESM.pdf"
}
```


**Returned outputs / historical output names**

```json
{
  "framework_table1.json": "inputs/framework_table1.json",
  "panel": "inputs/pd1_panel_published.json (10 binders incl. H965 KD 81.6 nM)"
}
```

**Validation and checks**

```json
"FR blocks byte-identical across all 10 panel sequences; H698 L3 len 8 recorded as published deviation"
```

## S2_design_rf_antibody: Generate CDR designs on the staged Fv scaffold

State: **completed**. Dependencies: `["S1_input_staging"]`.

Acceptance/checks: Job terminal; paired designs returned

### C02: rfdiffusion_proteinmpnn (RF-Antibody)

Purpose: CDR backbone + sequence design conditioned on Fv scaffold + PD-1 antigen

Source: **boltzmann**; recorded state: **completed**.

Exact record: [tool_details.json](../inputs/execution_records/tool_details.json) → `/records/C02`. Original call ID: `run_001_rf_antibody-S2-01`.

Identifier/version: `boltzmann job rfdiffusion_proteinmpnn, doc 6af8769f239a6b9f38beba18`.

**Inputs**

```json
{
  "antibody_pdb_path": "users/680f678c1b1d883c92aa706c/1794668173943/fv_scaffold.pdb",
  "antigen_pdb_path": "users/680f678c1b1d883c92aa706c/1794668182656/pd1_antigen.pdb",
  "num_sequences": 20,
  "antibody_type": "antibody"
}
```

**Parameters recorded for this call**

| Setting | Value / exact saved value | Recorded explanation |
| --- | --- | --- |
| `num_sequences` | `20 designs requested (returned 40 paired VH/VL)` | design budget; 20 requested returned 40 pairs (2 per design) |
| `antibody_type` | `paired antibody format` | paired VH/VL, not nanobody |

**Execution and identifiers**

```json
{
  "submitted": "2026-11-14T15:0x:xxZ",
  "job_id": "6af8769f239a6b9f38beba18",
  "runtime": "~1m49s"
}
```

**Recorded resources**

```json
{
  "mode": "remote (platform GPU)"
}
```

**Returned outputs / historical output names**

```json
{
  "raw": "outputs/rf_antibody/ (unzipped platform archive)",
  "pairs": 40
}
```

**Validation and checks**

```json
"Archive downloaded and unzipped; 40 paired designs parsed"
```

Original submission records: `C02.R01`. These are evidence for this call, not additional completed jobs.

### C02.R01: rfdiffusion_proteinmpnn

Purpose: See the stage purpose.

Source: **boltzmann**; recorded state: **Success**.

Exact record: [tool_details.json](../inputs/execution_records/tool_details.json) → `/records/C02.R01`. Original call ID: `call_-7077364551934535859:subcall:0`.

Identifier/version: `rfdiffusion_proteinmpnn`.

**Inputs**

```json
{
  "saved_request": "src/task_003_pd1_framework_guided_cdr_design/run_001_rf_antibody/inputs/submitted_requests/message_17052_subcall_0.json",
  "sha256": "ba2cf441e9cc18c5395bdf22bebb92bd5196afdf1bddb9f8c577ef7d86fdc6f6"
}
```

**Parameters recorded for this call**

| Setting | Value / exact saved value | Recorded explanation |
| --- | --- | --- |
| `antibody_pdb_path` | `users/680f678c1b1d883c92aa706c/1794668173943/fv_scaffold.pdb` | Field meaning: Antibody structure input location.  |
| `antibody_type` | `antibody` | Field meaning: Requested antibody format/type.  |
| `antigen_pdb_path` | `users/680f678c1b1d883c92aa706c/1794668182656/pd1_antigen.pdb` | Field meaning: Antigen structure input location.  |
| `num_sequences` | `20` | Field meaning: Number of sequences requested.  |

**Execution and identifiers**

```json
{
  "session_id": "20261114_110401_625a94",
  "message_id": 17052,
  "tool_call_id": "call_-7077364551934535859",
  "subcall_index": 0,
  "timestamp_utc": "2026-11-14T14:56:31.683889+00:00",
  "doc_id": "6af8769f239a6b9f38beba18",
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

## S3_gate_enforcement: Enforce frozen gates on RF-Antibody outputs

State: **completed**. Dependencies: `["S2_design_rf_antibody"]`.

Acceptance/checks: Every candidate has explicit gate verdicts

### C03: process_rf_align.py

Purpose: NW-align each design to Table-1 layout; extract CDRs; enforce gates

Source: **open_source**; recorded state: **completed**.

Exact record: [tool_details.json](../inputs/execution_records/tool_details.json) → `/records/C03`. Original call ID: `run_001_rf_antibody-S3-01`.

Identifier/version: `local code: code/process_rf_align.py`.

**Inputs**

```json
{
  "rf_output": "outputs/rf_antibody/ab_des_output_{0,1}_mpnn.csv"
}
```


**Returned outputs / historical output names**

```json
{
  "pool": "candidates/rf_antibody_pool.json",
  "eligible": 0,
  "failed_gates": "39/40 H2 length 7 + FR junction edits; 1 extraction failure"
}
```

**Validation and checks**

```json
"All 40 verdicts recorded with failure reasons"
```
