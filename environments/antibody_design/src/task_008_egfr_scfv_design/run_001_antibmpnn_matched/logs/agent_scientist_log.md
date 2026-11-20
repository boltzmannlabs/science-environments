# Recorded scientific activity

**Run:** `run_001_antibmpnn_matched`  
**Status:** completed

This retrospective summary is compiled from the saved scientific inputs, output tables and accepted models. Step order follows the recorded workflow; wall-clock times are not reconstructed.

| Step | Tool and settings | Recorded result |
| --- | --- | --- |
| Prepare reference | PDB extraction; ANARCI Chothia numbering | Exact parent VH/VL sequence match |
| Generate sequences | AntiBMPNN; 20 samples; H/L CDR edits | 20 recorded candidates |
| Screen sequences | Mask, uniqueness, cysteine, glycosylation-sequon and sequence-property checks | 6 selected candidates |
| Evaluate complexes | Boltz2; same EGFR construct and conditions for designs and reference | 6 candidate models + native control |

Highest candidate ipTM: cet_008_r1_s15, 0.8549; matched native control 0.9065. No candidate improves the reference interface score.

[Workflow](../workflow.md) · [Tool records](../inputs/execution_records/tool_details.json) · [Original configuration](../inputs/execution_records/full_config.json)
