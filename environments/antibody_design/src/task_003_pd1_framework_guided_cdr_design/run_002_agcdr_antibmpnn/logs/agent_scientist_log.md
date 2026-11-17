# Agent-Scientist activity — run_002_agcdr_antibmpnn

Task: `task_003_pd1_framework_guided_cdr_design`. Saved status: **completed**. Evidence presentation updated 2026-11-16.

[Execution summary](execution_summary.md) · [Exact calls, inputs and responses](../inputs/execution_records/tool_details.json) · [Observable narrative export](../inputs/execution_records/observable_events.jsonl)

## Existing recorded activity

# agent_scientist_log — run_002_agcdr_antibmpnn (retrospective export)

Exported from the live Agent-Scientist session that executed run_002_agcdr_antibmpnn on 2026-11-14 (session 20261114_110401_625a94). Observable events; times UTC approximate to the minute.

- 13:0x Pivot decision recorded (run_001_rf_antibody zero-eligible). agcdr_diff submitted (doc 6af879a3d29658acc304e059; fv_scaffold + pd1_antigen; num_samples 20, num_steps 50).
- 13:1x Completed: 20 backbones, CDR RMSD ~10.9 A, framework preserved. Downloaded/unzipped.
- 13:2x Backbone ZIP built; first upload (doc 6af87a62445ae94313c3b0f1) FAILED — per-atom numbering produced 468 "residues". Fixed to per-residue (H:117/L:108); resubmitted AntiBMPNN (doc 6af87c36445ae94313c3b280, 160 seqs) -> completed.
- 13:3x process_agcdr.py: mask verified 160/160 position-by-position; gates -> 115 unique eligible (agcdr_pool.json).
- 13:4x select_screening.py (rule frozen earlier): 5 selected, min pairwise CDR Hamming 32/60.
- 13:5x Boltz2 x6 submitted: H965 control 6af87d71445ae94313c3b729 first, then 5 candidates (6af87d93…, 6af87d99…, 6af87da3…, 6af87da9…, 6af87db1…). All completed.
- 15:0x Downloads: boltzmann_download 400 on outputs.zip; status re-poll + direct curl inside 300 s window -> all 6 archives + 3 property CSVs retrieved.
- 15:1x Platform behavior noted: Boltz2 emits pairwise predictions (PD1:VH results_1, PD1:VL results_2), not ternary. Metrics kept per pair.
- 15:2x Construct drift noticed and disclosed: control antigen 33-145 S93 form vs candidates 33-134 C93 form.
- 15:3x assemble_metrics.py -> metrics_raw.json; build_bundle.py -> results bundle (shortlist.csv, metrics.json, report.md, structures x12, raw_outputs x15).
- 16:0x Reorganized into monoclonal.md per-run layout (this tree) without re-execution.

Stops: none.


## Retrospective packaging — 2026-11-15T11:14:35+00:00

Existing run files were inventoried and organized under this run ID. No tool jobs were started. Source session: `20261114_110401_625a94`; the [saved observable events](../inputs/execution_records/observable_events.jsonl) provide the supporting activity record. This entry is a retrospective storage action, not fabricated historical execution.

## Call and submission timeline

Each row is an existing record. Recovered submission rows belong to their parent call; they may include failed attempts and are not additional completed workflow steps. Unknown timestamps remain explicitly unrecorded.

| Time recorded | Record | Tool | State | Job / call identity |
| --- | --- | --- | --- | --- |
| 2026-11-14T15:09:22.882422+00:00 | `C01.R01` | agcdr_diff | Success | `6af879a3d29658acc304e059` |
| 2026-11-14T15:12:33.813948+00:00 | `C02.R01` | AntiBMPNN | failed | `6af87a62445ae94313c3b0f1` |
| 2026-11-14T15:20:21.836008+00:00 | `C02.R02` | AntiBMPNN | Success | `6af87c36445ae94313c3b280` |
| 2026-11-14T15:25:37.129487+00:00 | `C04.R01` | Boltz2 | Success | `6af87d71445ae94313c3b729` |
| 2026-11-14T15:26:11.758358+00:00 | `C04.R02` | Boltz2 | Success | `6af87d939030bff416447c9a` |
| 2026-11-14T15:26:17.676409+00:00 | `C04.R03` | Boltz2 | Success | `6af87d99239a6b9f38bebe2d` |
| 2026-11-14T15:26:27.172600+00:00 | `C04.R04` | Boltz2 | Success | `6af87da39030bff416447cb6` |
| 2026-11-14T15:26:33.405726+00:00 | `C04.R05` | Boltz2 | Success | `6af87da99de6b44b075d81f2` |
| 2026-11-14T15:26:40.909146+00:00 | `C04.R06` | Boltz2 | Success | `6af87db19850a93adf67d249` |
| 2026-11-14T15:27:16.035003+00:00 | `C05.R01` | Antibody_Prediction | Success | `6af87dd4d29658acc304e596` |
| 2026-11-14T15:27:22.005850+00:00 | `C05.R02` | Antibody_Prediction | Success | `6af87dda445ae94313c3b7bb` |
| 2026-11-14T15:27:40.943404+00:00 | `C05.R03` | Antibody_Prediction | Success | `6af87ded445ae94313c3b850` |
| not recorded | `C01` | agcdr_diff (Antibody RFD3) | completed | `run_002_agcdr_antibmpnn-S1-01` |
| not recorded | `C02` | AntiBMPNN | completed | `run_002_agcdr_antibmpnn-S2-01` |
| not recorded | `C03` | select_screening.py | completed | `run_002_agcdr_antibmpnn-S3-01` |
| not recorded | `C04` | Boltz2 | completed | `run_002_agcdr_antibmpnn-S4-01..06` |
| not recorded | `C05` | Antibody_Prediction (AB_PROP) | completed | `run_002_agcdr_antibmpnn-S5-01..03` |
