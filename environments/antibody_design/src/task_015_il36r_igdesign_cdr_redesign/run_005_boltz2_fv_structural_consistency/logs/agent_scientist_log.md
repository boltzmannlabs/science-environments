# Recorded scientific activity

**Run:** `run_005_boltz2_fv_structural_consistency`  
**Status:** completed

This retrospective summary is compiled from the saved scientific inputs, output tables and accepted models. Step order follows the recorded workflow; wall-clock times are not reconstructed.

| Step | Tool and settings | Recorded result |
| --- | --- | --- |
| Assemble panel | Saved boltz2_panel.json; 12 designs + reference | 13 exact sequence pairs |
| Predict Fv structures | Matched Boltz2 settings | 13 accepted models |
| Verify model identity | Exact VH and VL sequence checks | All 13 panel members verified |
| Measure structure and confidence | Framework Kabsch fit; N/Cα/C/O backbone vs experimental 6U6U | 12 ranked candidates and native control |

Lowest candidate Fv deviation is antibmpnn_hcdr3_top3, 0.4022 Å; native control 0.3178 Å. Lowest candidate HCDR3 deviation is igdesign_hcdr123_top2, 0.6926 Å. The AntiBMPNN subsets are the fixed recorded panels, selected in descending NLL order.

[Workflow](../workflow.md) · [Tool records](../inputs/execution_records/tool_details.json) · [Original configuration](../inputs/execution_records/full_config.json)
