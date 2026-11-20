# Recorded scientific activity

**Run:** `run_002_igdesign_local`  
**Status:** completed

This retrospective summary is compiled from the saved scientific inputs, output tables and accepted models. Step order follows the recorded workflow; wall-clock times are not reconstructed.

| Step | Tool and settings | Recorded result |
| --- | --- | --- |
| Prepare conditioning | Reference complex and heavy-CDR mask | Paired light-chain and antigen context |
| Generate sequences | IgDesign; 100 samples | 100 native candidate rows |
| Apply sequence gates | Protected-residue and sequence checks | 95 passing unique candidates |
| Evaluate complexes | Boltz2; exact model sequence verification | 4 accepted candidate predictions |

Best candidate cand067: ipTM 0.8618, pTM 0.9198; matched reference ipTM 0.8987. Four candidates span ipTM 0.7326–0.8618.

[Workflow](../workflow.md) · [Tool records](../inputs/execution_records/tool_details.json) · [Original configuration](../inputs/execution_records/full_config.json)
