# Agent-Scientist activity — run_003_prodigy_ipsae_evaluation

Task: `task_003_pd1_framework_guided_cdr_design`. Saved status: **completed**. Evidence presentation updated 2026-11-16.

[Execution summary](execution_summary.md) · [Exact calls, inputs and responses](../inputs/execution_records/tool_details.json) · [Observable narrative export](../inputs/execution_records/observable_events.jsonl)

## Existing recorded activity

# agent_scientist_log — run_003_prodigy_ipsae_evaluation (live)

- 16:02-16:03Z Prepared run_003_prodigy_ipsae_evaluation packages from run_002_agcdr_antibmpnn Boltz2 outputs: boltz2_models.zip (12 PDBs, sha256 c7031461…) and boltz2_models_conf.zip (12 models + pae/plddt npz + confidence json, 60 files, sha256 29a7e779…).
- 16:03Z boltz2_models.zip upload OK (partial validation: inventory >256 KiB receipt budget). Submit REJECTED: "validation rules or dependent inputs changed" — ZIP receipt not usable at submit time.
- 16:04Z Split into prodigy_set1/2.zip (6 models each); same submit rejection. Conclusion: multi-structure ZIP receipts unusable for Prodigy submits (recorded as connector limitation).
- 16:04:30Z Single-PDB submit without chain_list: backend 422 — connector serialized chain_list:"" and experiment_name:"" (visible in error payload). Connector serialization bug, recorded.
- 16:04:56Z Working route found: upload single PDB WITH experiment_data {chain_list:["A","B"]}, receipt covers the parameter; submit accepted. cand2-VH first (doc 6af886a89de6b44b075d8685).
- 16:05-16:07Z Remaining 11 Prodigy jobs submitted one-by-one the same way (doc IDs in config). All accepted with checked-level validation.
- 16:07:31Z ipsae-protein submitted (doc 6af88746d29658acc304eb69; boltz2_models_conf.zip uploaded with partial validation accepted for this tool; model_type boltz2; cutoffs 10/10).
- Polling all 13 jobs; no duplicates submitted.

## Closeout (2026-11-14)

- All 13 jobs completed and downloaded; results tabulated in metrics.csv (24 metric rows) and report.md.
- Consolidated remaining tabular deliverables per monoclonal.md: candidates.csv (5 candidates evaluated in this phase + control reference), shortlist.csv (ipSAE-sum ranking: PD1T3-019 > 038 > 054 > 011 > 069), sequences.fasta (evaluated set, from run_002_agcdr_antibmpnn), benchmark_comparison.csv (3 rows; predicted-vs-measured marked not_comparable, raw Prodigy units not interpreted).
- Status: complete; no remaining requirements within this run's scope.


## Retrospective packaging — 2026-11-15T11:14:35+00:00

Existing run files were inventoried and organized under this run ID. No tool jobs were started. Source session: `20261114_110401_625a94`; the [saved observable events](../inputs/execution_records/observable_events.jsonl) provide the supporting activity record. This entry is a retrospective storage action, not fabricated historical execution.

## Call and submission timeline

Each row is an existing record. Recovered submission rows belong to their parent call; they may include failed attempts and are not additional completed workflow steps. Unknown timestamps remain explicitly unrecorded.

| Time recorded | Record | Tool | State | Job / call identity |
| --- | --- | --- | --- | --- |
| 2026-11-14T16:04:56.213784+00:00 | `C01.R01` | Prodigy | Success | `6af886a89de6b44b075d8685` |
| 2026-11-14T16:05:28.041638+00:00 | `C01.R02` | Prodigy | Success | `6af886c89850a93adf67d73b` |
| 2026-11-14T16:05:38.397878+00:00 | `C01.R03` | Prodigy | Success | `6af886d2239a6b9f38bec324` |
| 2026-11-14T16:05:51.644853+00:00 | `C01.R04` | Prodigy | Success | `6af886df9850a93adf67d773` |
| 2026-11-14T16:06:01.750447+00:00 | `C01.R05` | Prodigy | Success | `6af886ea9de6b44b075d86f1` |
| 2026-11-14T16:06:12.487223+00:00 | `C01.R06` | Prodigy | Success | `6af886f4239a6b9f38bec38d` |
| 2026-11-14T16:06:22.998525+00:00 | `C01.R07` | Prodigy | Success | `6af886ff9de6b44b075d872a` |
| 2026-11-14T16:06:32.829029+00:00 | `C01.R08` | Prodigy | Success | `6af887099de6b44b075d8750` |
| 2026-11-14T16:06:42.969693+00:00 | `C01.R09` | Prodigy | Success | `6af88713239a6b9f38bec3dd` |
| 2026-11-14T16:06:53.390711+00:00 | `C01.R10` | Prodigy | Success | `6af8871d239a6b9f38bec3fb` |
| 2026-11-14T16:07:03.575566+00:00 | `C01.R11` | Prodigy | Success | `6af887289de6b44b075d8791` |
| 2026-11-14T16:07:14.072758+00:00 | `C01.R12` | Prodigy | Success | `6af887329850a93adf67d827` |
| 2026-11-14T16:07:31.370722+00:00 | `C02.R01` | ipsae-protein | Success | `6af88746d29658acc304eb69` |
| not recorded | `C01` | Prodigy (Binding Affinity) | completed | `run_003_prodigy_ipsae_evaluation-S1-01..12` |
| not recorded | `C02` | ipsae-protein (ipSAE Generation) | completed | `6af88746d29658acc304eb69` |
