# Recorded scientific activity

**Run:** `run_004_antibmpnn_hcdr123_redesign`  
**Status:** completed

This retrospective summary is compiled from the saved scientific inputs, output tables and accepted models. Step order follows the recorded workflow; wall-clock times are not reconstructed.

| Step | Tool and settings | Recorded result |
| --- | --- | --- |
| Prepare complex | Saved H/L/antigen structure and declared edit mask | Exact native-chain mapping |
| Generate sequences | AntiBMPNN; 40 samples | 40 native output rows |
| Record evaluation panel | Three sequences selected in descending reported score order | Fixed panel; lower NLL is preferred |
| Evaluate panel | Shared Boltz2 evaluation | See run_005 |

Three recorded sequence pairs were evaluated in run_005. AntiBMPNN selection used descending negative log likelihood, so the fixed panel is not a best-likelihood selection from the generation pool.

[Workflow](../workflow.md) · [Tool records](../inputs/execution_records/tool_details.json) · [Original configuration](../inputs/execution_records/full_config.json)
