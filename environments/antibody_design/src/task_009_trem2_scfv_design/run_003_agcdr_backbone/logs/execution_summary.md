# Execution summary

**Run:** `run_003_agcdr_backbone`  
**Status:** completed

This retrospective summary is compiled from the saved scientific inputs, output tables and accepted models. Step order follows the recorded workflow; wall-clock times are not reconstructed.

| Step | Tool and settings | Recorded result |
| --- | --- | --- |
| Diversify backbone | AgCDR; 8 samples, 10 steps | 8 backbone samples |
| Select backbone | Recorded sample-7 backbone | One backbone for sequence generation |
| Generate sequences | Local AntiBMPNN; 40 samples | 40 candidate sequences |
| Evaluate complexes | Boltz2; exact sequence identity check | 4 predictions; cand032 retained |

Best candidate cand032: ipTM 0.7413, pTM 0.8636; matched reference ipTM 0.8987. The full evaluated range is 0.3633–0.7413.

[Workflow](../workflow.md) · [Tool records](../inputs/execution_records/tool_details.json) · [Original configuration](../inputs/execution_records/full_config.json)
