# Agent-Scientist activity — run_004_abflow_multi_cdr

Task: `task_004_lcat_reference_fab_cdrh3_reconstruction`. Saved status: **completed**. Evidence presentation updated 2026-11-16.

[Execution summary](execution_summary.md) · [Exact calls, inputs and responses](../inputs/execution_records/tool_details.json) · [Observable narrative export](../inputs/execution_records/observable_events.jsonl)

## Existing recorded activity

# agent_scientist_log — run_004_abflow_multi_cdr

Chronological observable agent activity (timestamps UTC, session 2026-11-14).

| Time | Activity |
| --- | --- |
| 15:27 | Identified multi_cdr_design.ckpt in authors' checkpoint release (ls AbFlow/checkpoints); verified test.sh accepts any ckpt; verified cal_metrics.py unchanged for multi-CDR output (H3-scoring path shared with run_001) |
| 15:28:42 | Generation executed: generate_candidates.py --ckpt multi_cdr_design.ckpt --seed 2023 --batch-size 1 -> gen_mcdr_1shot/ (1 candidate, exit 0, ~9 s GPU) |
| 15:28:46 | First freeze attempt re-froze hard-coded pools (script default); identified script needed pool argument |
| 15:29:33 | freeze_rankings.py patched to accept pool dirs (sys import + argv); gen_mcdr_1shot frozen: pmets 0.7684, hash check all-verified |
| 15:29:35 | freeze_record.json protocol label corrected to the Table-2 track label (documentation fix; ordering unchanged) |
| 15:30 | score_candidates.py extended to the mcdr pool (list + summary entry); scored via authors' cal_metrics with abflow_benchmark env PATH fix for lddt binary |
| 15:31 | Scoring complete: AAR H3 0.4211, CAAR 0.2500, TM 0.9593, lDDT 0.7686, RMSD(AppC) 19.84 A, DockQ 0.345 |
| 15:31 | Constraint compliance verified on candidate: VH FW 106/107, changes confined to CDR positions, H3 len 19, no native copy |
| 15:40 | Config JSON, run.yaml, workflow.md, logs, results tree written; planning tables updated to 4 designed / 2 selected / 2 executed |

Warnings/errors and recoveries: (1) `--n 1` arg rejected (argparse) — rerun without it using the 1-entry input file; no scientific impact. (2) freeze script hard-coded pools — patched, re-froze mcdr pool only; existing pools' records refreshed with identical rule (timestamp-only change). (3) lddt PATH (known from run_001) — env bin prepended.


## Retrospective packaging — 2026-11-15T11:14:35+00:00

Existing run files were inventoried and organized under this run ID. No tool jobs were started. Source session: `20261114_110408_5c556e`; the [saved observable events](../inputs/execution_records/observable_events.jsonl) provide the supporting activity record. This entry is a retrospective storage action, not fabricated historical execution.

## Call and submission timeline

Each row is an existing record. Recovered submission rows belong to their parent call; they may include failed attempts and are not additional completed workflow steps. Unknown timestamps remain explicitly unrecorded.

| Time recorded | Record | Tool | State | Job / call identity |
| --- | --- | --- | --- | --- |
| 2026-11-14T11:17:00Z | `C01` | build_run.py | completed | `mc1` |
| 2026-11-14T15:28:42Z | `C02` | AbFlow | completed | `mc2` |
| 2026-11-14T15:29:33Z | `C03` | freeze_rankings.py | completed | `mc3` |
| 2026-11-14T15:31Z | `C04` | AbFlow evaluator | completed | `mc4` |
| 2026-11-14T15:40Z | `C06` | local python | completed | `mc5` |
| 2026-11-14T16:35Z | `C05` | AbFlow evaluator | completed | `mc4b` |
