# Recorded scientific activity

**Run:** `run_002_igdesign_native_reconstruction`  
**Status:** completed

This retrospective summary is compiled from the saved scientific inputs, output tables and accepted models. Step order follows the recorded workflow; wall-clock times are not reconstructed.

| Step | Tool and settings | Recorded result |
| --- | --- | --- |
| Generate samples | IgDesign; 1 + 100 samples per scope | 202 samples |
| Verify and deduplicate | Native framework/VL preservation and sequence identity | 158 unique sequences |
| Measure native recovery | Position-aligned designed-scope AAR | 1-shot and best-of-100 endpoints |
| Evaluate geometry | Five designs per scope; Boltz2; Cα framework fit | 10 candidate models + native control |

Designed-scope AAR is 0.6923/0.8462 for HCDR3 1-shot/best-of-100 and 0.7241/0.7931 for HCDR123. t014r002_hcdr3_best100_012 has HCDR3 deviation 1.3144 Å and Fv deviation 0.4382 Å from the predicted native Fv.

[Workflow](../workflow.md) · [Tool records](../inputs/execution_records/tool_details.json) · [Original configuration](../inputs/execution_records/full_config.json)
