# Recorded scientific activity

**Run:** `run_002_igdesign_reconstruction`  
**Status:** completed

This retrospective summary is compiled from the saved scientific inputs, output tables and accepted models. Step order follows the recorded workflow; wall-clock times are not reconstructed.

| Step | Tool and settings | Recorded result |
| --- | --- | --- |
| Generate HCDR3 pool | IgDesign; separate 1-shot and 100-sample executions | 101 samples |
| Generate HCDR123 pool | IgDesign; separate 1-shot and 100-sample executions | 101 samples |
| Measure native recovery | Position-aligned per-CDR AAR | 202 sample-level metric rows |
| Select shared evaluation panel | Four recorded designs | Boltz2 and ESMFold evaluation retained in run_001 |

HCDR3-only 1-shot AAR is 0.4667; the separate 100-sample pool has mean 0.5193 and maximum 0.6667. HCDR123 pool mean HCDR3 AAR is 0.5160; maximum 0.6667.

[Workflow](../workflow.md) · [Tool records](../inputs/execution_records/tool_details.json) · [Original configuration](../inputs/execution_records/full_config.json)
