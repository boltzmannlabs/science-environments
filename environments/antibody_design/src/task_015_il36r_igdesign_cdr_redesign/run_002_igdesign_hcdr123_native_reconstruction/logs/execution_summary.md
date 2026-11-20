# Execution summary

**Run:** `run_002_igdesign_hcdr123_native_reconstruction`  
**Status:** completed

This retrospective summary is compiled from the saved scientific inputs, output tables and accepted models. Step order follows the recorded workflow; wall-clock times are not reconstructed.

| Step | Tool and settings | Recorded result |
| --- | --- | --- |
| Generate 1-shot | IgDesign; saved one-sample configuration | 1 sample |
| Generate 100-sample pool | IgDesign; separate saved configuration | 100 samples |
| Measure recovery | Per-CDR position identity | 101 samples; separate per-CDR maxima |
| Select evaluation entries | Ascending summed CDR cross-entropy loss | 3 panel members evaluated in run_005 |

1-shot HCDR1/2/3 AAR: 0.7500/0.6250/0.5833. Per-CDR maxima over 100 samples: 1.0000/0.7500/0.8333; these maxima need not occur in one sequence.

[Workflow](../workflow.md) · [Tool records](../inputs/execution_records/tool_details.json) · [Original configuration](../inputs/execution_records/full_config.json)
