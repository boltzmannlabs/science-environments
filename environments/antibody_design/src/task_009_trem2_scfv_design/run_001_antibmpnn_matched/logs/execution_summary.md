# Execution summary

**Run:** `run_001_antibmpnn_matched`  
**Status:** completed

This retrospective summary is compiled from the saved scientific inputs, output tables and accepted models. Step order follows the recorded workflow; wall-clock times are not reconstructed.

| Step | Tool and settings | Recorded result |
| --- | --- | --- |
| Verify reference | Saved structures, CDR numbering and TREM2 construct | Matched native control |
| Generate sequences | AntiBMPNN; 40 samples | 40 candidates |
| Apply sequence gates | CDR-only substitutions and identity checks | 40 pass; 39 unique sequences |
| Evaluate complexes | Boltz2, verified exact submitted VH/VL | 4 candidate predictions |

Candidate ipTM 0.3062–0.7969; matched native control 0.8987. cand13_T009-C13 is excluded from follow-up because of low interface confidence; its measured result is retained.

[Workflow](../workflow.md) · [Tool records](../inputs/execution_records/tool_details.json) · [Original configuration](../inputs/execution_records/full_config.json)
