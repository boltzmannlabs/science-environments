# TREM2 reference-backbone AntiBMPNN redesign

**Task:** `task_009_trem2_scfv_design`  
**Run:** `run_001_antibmpnn_matched`  
**Status:** completed

## Inputs and constraints

Saved reference scFv, prepared TREM2 construct and chain-local CDR mask. VH/VL framework residues and the scFv linker are protected; exact masks and numbering are retained in inputs/cdr_mask.json and inputs/imgt_numbering.json.

[Saved inputs](inputs/) include the prepared scientific inputs and submitted request settings. The [configuration snapshot](inputs/execution_records/full_config.json) retains the original execution configuration. Native sampling configurations are also retained with the corresponding raw output files.

## Workflow steps

| Step | Tool and settings | Recorded result |
| --- | --- | --- |
| Verify reference | Saved structures, CDR numbering and TREM2 construct | Matched native control |
| Generate sequences | AntiBMPNN; 40 samples | 40 candidates |
| Apply sequence gates | CDR-only substitutions and identity checks | 40 pass; 39 unique sequences |
| Evaluate complexes | Boltz2, verified exact submitted VH/VL | 4 candidate predictions |

## Measurements and outcome

Candidate ipTM 0.3062–0.7969; matched native control 0.8987. cand13_T009-C13 is excluded from follow-up because of low interface confidence; its measured result is retained.

See the [completed report](../../../results/task_009_trem2_scfv_design/run_001_antibmpnn_matched/report.md) and [task benchmark](../../../benchmark/monoclonal_antibody_design/task_009_trem2_scfv_design/comparison.md) for numerical tables and comparator definitions. This workflow describes the saved execution; no prediction was rerun during documentation preparation.

## Execution evidence

- [Tool and method records](inputs/execution_records/tool_details.json)
- [Recorded activity summary](logs/agent_scientist_log.md)
- [Execution summary](logs/execution_summary.md)
- [Artifact inventory](inputs/saved_artifacts.csv)
