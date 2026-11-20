# Recorded scientific activity

**Run:** `run_001_antibmpnn_fixed_backbone`  
**Status:** completed

This retrospective summary is compiled from the saved scientific inputs, output tables and accepted models. Step order follows the recorded workflow; wall-clock times are not reconstructed.

| Step | Tool and settings | Recorded result |
| --- | --- | --- |
| Generate sequences | AntiBMPNN; 20 per scope | 40 samples |
| Verify and deduplicate | VL identity, VH length, protected residues and mask checks | 40 pass; 11 HCDR3 + 15 HCDR123 unique sequences |
| Select panel | Five sequences per scope | 10 candidate sequence pairs |
| Evaluate geometry | Boltz2; exact sequence checks; Cα framework fit | 10 candidate models + native control |

Best recovery is 0.6923 (HCDR3) and 0.7241 (HCDR123). Geometry leader t014r001_hcdr123_scope_s05 has AAR 0.6897, nine substitutions, Fv deviation 0.3978 Å and HCDR3 deviation 1.3367 Å from the predicted native Fv.

[Workflow](../workflow.md) · [Tool records](../inputs/execution_records/tool_details.json) · [Original configuration](../inputs/execution_records/full_config.json)
