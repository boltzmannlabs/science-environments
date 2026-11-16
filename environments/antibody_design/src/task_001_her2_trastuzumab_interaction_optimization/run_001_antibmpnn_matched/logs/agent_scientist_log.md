# Agent-Scientist activity — run_001_antibmpnn_matched

Task: `task_001_her2_trastuzumab_interaction_optimization`. Saved status: **complete**. Evidence presentation updated 2026-11-16.

[Execution summary](execution_summary.md) · [Exact calls, inputs and responses](../inputs/execution_records/tool_details.json) · [Observable narrative export](../inputs/execution_records/observable_events.jsonl)

## Existing recorded activity

# agent_scientist_log.md — run_001_antibmpnn_matched

- 2026-11-14T11:09:09Z Session start. Task md + benchmark md + monoclonal.md guide read. 3 workflows designed (run_001 selected, run_002 not_selected, run_003 not_run); configs + run.yaml written.
- 2026-11-14T11:10Z Stage 0 executed: 1N8Z downloaded (sha256 ed934d36...), chains verified A=trastuzumab light(214), B=heavy(220), C=HER2(581/607 modeled; gaps 102-110,303-305,361-364,581-590); VH/VL 100% identity to trastuzumab consensus; Fv+HER2 split PDBs prepared and hash-pinned. Biological assembly = as-deposited (identity BIOMT).
- 2026-11-14T11:20-11:28Z AntiBMPNN attempts 1-4 FAILED (docs 6af844059de6b44b075d79e0, 6af844589030bff41644751b, 6af844ca9850a93adf67cad5, 6af8453c239a6b9f38beb6dd): "Expected exactly one heavy/VHH domain; detected 0". fetch_tool_log -> HTTP 404. Benign control 1MCP (doc 6af84579239a6b9f38beb714, $1) SUCCEEDED -> service healthy, input format at fault.
- 2026-11-14T11:29Z Root cause: stage0 renumbered residues per ATOM line (VH=924 "residues"). stage0b rewritten with per-residue numbering + SEQRES + TER/END; complex_hl_a_seqres.pdb verified H=VH(120)/L=VL(107)/A=HER2(581).
- 2026-11-14T11:32Z AntiBMPNN attempt 5 (doc 6af8461a9850a93adf67cb88, generation_count 40) SUBMITTED -> SUCCESS. Results zip downloaded via fresh signed URL (40,806 bytes).
- 2026-11-14T11:33Z stage2 verification: 40/40 lengths unchanged, all mutations inside Kabat CDR mask, framework byte-identical, no new Cys; 38 unique (2 duplicate pairs); NG/NS/NT/DG/DS/DT motifs all inherited from reference CDRs.
- 2026-11-14T11:34Z Boltz2 REFERENCE submitted (doc 6af84747445ae94313c3a9ae) -> Success ~11:50Z. Pairwise scheduling discovered: record 1 = HER2+VH, record 2 = HER2+VL. Confidence: ipTM 0.220/0.340.
- 2026-11-14T12:00Z Candidate submissions blocked: HTTP 500 "Insufficient credits" on old account. User supplied new API key in chat (value NOT logged here); key written to profile .env; jobs now under account users/680f678c1b1d883c92aa706c.
- 2026-11-14T12:05-12:20Z 8 candidate Boltz2 jobs submitted + completed (docs in inputs/boltz2_submissions.json); artifacts downloaded (pdbs_outputs.zip, outputs.zip, paths.csv each). Signed-URL expiry (300 s) bit once during batch download; resolved by re-poll + immediate download per job.
- 2026-11-14T12:30-12:45Z Prodigy v1 (9 jobs, nested pdbs_outputs.zip): ALL FAILED ("Signed URL download failed: 404", then "Input contains no nonempty PDB files at the supported archive level"). Diagnosis: nested boltz_pdb/ directory level. One corrected resubmission each with flat zips (PDBs at archive root) -> ALL 9 SUCCEEDED; prodigy.csv per construct.
- 2026-11-14T13:00-13:10Z stage6 evaluation: Prodigy dG + derived Kd, epitope recovery vs crystal contacts (16 HER2 residues 532-603), CDR pLDDT from plddt npz, interface clash counts (<2.2 A heavy-atom pairs). Files: raw/evaluation.{csv,json}, raw/clash_counts.json, raw/boltz2_confidence.{csv,json}.
- 2026-11-14T13:30-13:40Z stage7 artifact build per monoclonal.md section 6: candidates.csv (38), shortlist.csv (8; pre-stated rank key: mean Prodigy dG, then ipTM rec2, then fewer mutations), sequences.fasta (78 chains), metrics.csv (81 rows), benchmark_comparison.csv (published REF15 endpoints + our metrics; cross-protocol verdict not_comparable per benchmark md), report.md (renamed from results.md, sections 7-9 added). 18 structure PDBs staged in structures/.
- Disclosure: mid-run account change (reference Boltz2 job on old account, candidate jobs on new account) — identical Boltz2/Prodigy protocol on both; recorded in report.md section 5.
- 2026-11-14T14:05Z Logs + execution_summary finalized; config JSON stages[] to be backfilled with tool_calls detail (see execution_summary).


## Retrospective packaging — 2026-11-15T11:14:35+00:00

Existing run files were inventoried and organized under this run ID. No tool jobs were started. Source session: `20261114_110112_c07285`; the [saved observable events](../inputs/execution_records/observable_events.jsonl) provide the supporting activity record. This entry is a retrospective storage action, not fabricated historical execution.

## Call and submission timeline

Each row is an existing record. Recovered submission rows belong to their parent call; they may include failed attempts and are not additional completed workflow steps. Unknown timestamps remain explicitly unrecorded.

| Time recorded | Record | Tool | State | Job / call identity |
| --- | --- | --- | --- | --- |
| 2026-11-14T11:20:37.730417+00:00 | `C03.R01` | AntiBMPNN | failed | `6af844059de6b44b075d79e0` |
| 2026-11-14T11:22:00.318391+00:00 | `C03.R02` | AntiBMPNN | failed | `6af844589030bff41644751b` |
| 2026-11-14T11:23:54.354766+00:00 | `C03.R03` | AntiBMPNN | failed | `6af844ca9850a93adf67cad5` |
| 2026-11-14T11:25:48.096608+00:00 | `C03.R04` | AntiBMPNN | failed | `6af8453c239a6b9f38beb6dd` |
| 2026-11-14T11:26:49.668764+00:00 | `C04.R01` | AntiBMPNN | Success | `6af84579239a6b9f38beb714` |
| 2026-11-14T11:29:30.581045+00:00 | `C05.R01` | AntiBMPNN | Success | `6af8461a9850a93adf67cb88` |
| 2026-11-14T11:34:31.466881+00:00 | `C07.R01` | Boltz2 | Success | `6af84747445ae94313c3a9ae` |
| not recorded | `C01` | stage0_fetch_verify.py | complete | `S0-1` |
| not recorded | `C02` | stage0b_fix_numbering.py | complete | `S0-2` |
| not recorded | `C03` | AntiBMPNN | failed | `S1-a1..a4` |
| not recorded | `C04` | AntiBMPNN | complete | `6af84579239a6b9f38beb714` |
| not recorded | `C05` | AntiBMPNN | complete | `6af8461a9850a93adf67cb88` |
| not recorded | `C06` | stage2_verify_mask.py | complete | `S2-1` |
| not recorded | `C07` | Boltz2 | complete | `6af84747445ae94313c3a9ae` |
| not recorded | `C08` | Boltz2 | complete | `6af87767239a6b9f38beba67` |
| not recorded | `C09` | Boltz2 | complete | `6af87769239a6b9f38beba72` |
| not recorded | `C10` | Boltz2 | complete | `6af8776c9850a93adf67ce91` |
| not recorded | `C11` | Boltz2 | complete | `6af8776e9de6b44b075d7e2f` |
| not recorded | `C12` | Boltz2 | complete | `6af87770445ae94313c3add0` |
| not recorded | `C13` | Boltz2 | complete | `6af87773239a6b9f38beba85` |
| not recorded | `C14` | Boltz2 | complete | `6af877759de6b44b075d7e3e` |
| not recorded | `C15` | Boltz2 | complete | `6af877789030bff416447921` |
| not recorded | `C16` | Prodigy | failed | `S4-v1` |
| not recorded | `C17` | Prodigy | complete | `6af883e0d29658acc304e85a` |
| not recorded | `C18` | Prodigy | complete | `6af883e39de6b44b075d8496` |
| not recorded | `C19` | Prodigy | complete | `6af883e4d29658acc304e869` |
| not recorded | `C20` | Prodigy | complete | `6af883e69850a93adf67d51a` |
| not recorded | `C21` | Prodigy | complete | `6af883e89030bff416447f91` |
| not recorded | `C22` | Prodigy | complete | `6af883ea445ae94313c3bcee` |
| not recorded | `C23` | Prodigy | complete | `6af883eb9850a93adf67d541` |
| not recorded | `C24` | Prodigy | complete | `6af883eed29658acc304e8a3` |
| not recorded | `C25` | Prodigy | complete | `6af883ef239a6b9f38bec13b` |
| not recorded | `C26` | stage4_extract_confidence.py | complete | `S5-1` |
| not recorded | `C27` | stage6_evaluate.py | complete | `S5-2` |
| not recorded | `C28` | clash scan | complete | `S5-3` |
| not recorded | `C29` | stage7_artifacts.py | complete | `S5-4` |
