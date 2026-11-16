# Agent-Scientist activity — run_003_antibmpnn_native_backbone

Task: `task_004_lcat_reference_fab_cdrh3_reconstruction`. Saved status: **completed**. Evidence presentation updated 2026-11-16.

[Execution summary](execution_summary.md) · [Exact calls, inputs and responses](../inputs/execution_records/tool_details.json) · [Observable narrative export](../inputs/execution_records/observable_events.jsonl)

## Existing recorded activity

# agent_scientist_log — run_003_antibmpnn_native_backbone

| Time (UTC) | Activity |
| --- | --- |
| 15:35 | User authorized executing remaining workflows including the blocked one as a declared variant |
| 15:46 | Prepared masked input: H3 -> 19x GLY (backbone-only), native complex otherwise intact |
| 15:48 | boltzmann_upload (receipt 803979853c624d9da28e8799ccec346d): partial validation (PDB syntax checked; chain suitability requires review) — reviewed locally: chain C verified, 96-114 = H3 |
| 15:48:53 | Submit 1 (doc 6af882e5239a6b9f38bec0b4): accepted, then FAILED validation: designed chain contains unsupported residues ['-'] — IMGT insertion codes (111A...) parsed as gaps |
| 15:52 | Bounded recovery: sequential renumbering (same atoms, same mask, same target); verified 19 GLY at 96-114, chains 377/109/126 |
| 15:56 | Upload 2 (receipt 6632033784ec47cda454eaed4007f31a) + submit 2 (doc 6af884b7239a6b9f38bec1e5): accepted |
| 15:58 | Job Success (98 s, boltzmann7, billed 1 unit); results zip downloaded via fresh signed URL (connector download returned 400 twice — known platform quirk; status refresh + direct fetch in one step) |
| 15:59 | Verified: 32 sequences, 32 unique H3s, 0 native copies, framework+VL native (tool crops 1 terminal framework residue in CSV output — domain recognition; restored from native on graft) |
| 16:04 | Evaluation models rebuilt: designed H3 on native backbone (N/CA/C/O/CB); frozen ranking = AntiBMPNN model score asc |
| 16:10 | Scored with authors' evaluator (after DockQ cwd fix): AAR H3 mean 0.5526, rank-1 0.5789; structural metrics trivially 0/1 (fixed backbone) — reported as by-construction |
| 16:20 | Records + results tree written |

Notes: platform partial-validation approvals were given for both upload and submit after local verification of the unchecked aspects. DockQ>1 artifact on identical backbones recorded as not-comparable.


## Retrospective packaging — 2026-11-15T11:14:35+00:00

Existing run files were inventoried and organized under this run ID. No tool jobs were started. Source session: `20261114_110408_5c556e`; the [saved observable events](../inputs/execution_records/observable_events.jsonl) provide the supporting activity record. This entry is a retrospective storage action, not fabricated historical execution.

## Call and submission timeline

Each row is an existing record. Recovered submission rows belong to their parent call; they may include failed attempts and are not additional completed workflow steps. Unknown timestamps remain explicitly unrecorded.

| Time recorded | Record | Tool | State | Job / call identity |
| --- | --- | --- | --- | --- |
| 2026-11-14T15:48:53.325696+00:00 | `C01.R01` | AntiBMPNN | failed | `6af882e5239a6b9f38bec0b4` |
| 2026-11-14T15:52Z | `C01` | local python | completed | `a0` |
| 2026-11-14T15:56:38.893454+00:00 | `C02.R01` | AntiBMPNN | Success | `6af884b7239a6b9f38bec1e5` |
| 2026-11-14T16:04Z | `C03` | local python | completed | `a2` |
| 2026-11-14T16:07-16:10Z | `C04` | AbFlow evaluator | completed | `a3` |
| 2026-11-14T16:20Z | `C05` | local python | completed | `a4` |
| not recorded | `C02` | AntiBMPNN | completed | `6af884b7239a6b9f38bec1e5` |
