# Agent-Scientist activity — run_002_diffab_local

Task: `task_004_lcat_reference_fab_cdrh3_reconstruction`. Saved status: **completed**. Evidence presentation updated 2026-11-16.

[Execution summary](execution_summary.md) · [Exact calls, inputs and responses](../inputs/execution_records/tool_details.json) · [Observable narrative export](../inputs/execution_records/observable_events.jsonl)

## Existing recorded activity

# agent_scientist_log — run_002_diffab_local

| Time (UTC) | Activity |
| --- | --- |
| 15:35 | User authorized end-to-end execution of all designed workflows via open-source/platform tools |
| 15:36 | Verified diffab conda env + local repo (codesign_single.pt present); GPU 0 free |
| 15:44 | Prepared inputs: native complex (in-context protocol), H3 span info file, n=32 sampling config (seed 20261114) |
| 15:45 | Preflight dry-run: H_CDR3 located at 0-based 95-113 len 19 — matches benchmark mask exactly |
| 15:48:27 | DiffAb generation launched (background); completed 15:49:31 (~55 s, 32 samples) |
| 15:50 | Verified outputs: 32 full-atom complexes, Chothia-renumbered, terminally cropped (H 125/126, L 106/109), H3 len 19 all, 32 unique H3 sequences, 0 native copies |
| 16:00 | Graft builder v1: H3 block transplant to native IMGT scaffold; column-format bug found (insertion code written into wrong columns -> Bio.PDB ValueError 111A) |
| 16:05 | Graft v2 correct: resnum + icode columns proper; all 32 regrafted; Bio.PDB parse OK (chains A/C/B 377/126/109) |
| 16:07 | Scoring run 1: 32 DiffAb scored; AntiBMPNN models failed antigen parse — my model builder had emitted only chain C |
| 16:08 | Rebuilt AntiBMPNN models correctly (native complex with mutated H3 residues) |
| 16:10 | Scoring run 2 complete (64 candidates); DockQ all 0 — diagnosed via native-vs-native control: evaluator shells ./DockQ/DockQ.py relative to repo cwd; driver lacked chdir |
| 16:12 | Control verified: native-vs-native AAR 1.0, TM 1.0 (evaluator sound); DockQ path bug confirmed |
| 16:14 | chdir fix applied; full rescore: DockQ populated (diffab mean 0.5877) |
| 16:20 | Records + results tree written |

Errors/recoveries: (1) graft icode column bug — fixed, regrafted all 32; (2) AntiBMPNN model builder emitted only chain C — rebuilt correctly; (3) DockQ cwd bug — chdir fix + control test + full rescore.


## Retrospective packaging — 2026-11-15T11:14:35+00:00

Existing run files were inventoried and organized under this run ID. No tool jobs were started. Source session: `20261114_110408_5c556e`; the [saved observable events](../inputs/execution_records/observable_events.jsonl) provide the supporting activity record. This entry is a retrospective storage action, not fabricated historical execution.

## Call and submission timeline

Each row is an existing record. Recovered submission rows belong to their parent call; they may include failed attempts and are not additional completed workflow steps. Unknown timestamps remain explicitly unrecorded.

| Time recorded | Record | Tool | State | Job / call identity |
| --- | --- | --- | --- | --- |
| 2026-11-14T15:48:27Z | `C01` | DiffAb | completed | `d1` |
| 2026-11-14T16:05Z | `C02` | graft_diffab.py | completed | `d1b` |
| 2026-11-14T16:07-16:10Z | `C04` | AbFlow evaluator | completed | `d3` |
| 2026-11-14T16:07Z | `C03` | local python | completed | `d2` |
| 2026-11-14T16:20Z | `C05` | local python | completed | `d4` |
