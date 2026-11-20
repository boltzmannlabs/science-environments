# Recorded scientific activity

**Run:** `run_001_antibmpnn_matched`  
**Status:** completed

This retrospective summary is compiled from the saved scientific inputs, output tables and accepted models. Step order follows the recorded workflow; wall-clock times are not reconstructed.

| Step | Tool and settings | Recorded result |
| --- | --- | --- |
| Generate sequences | AntiBMPNN; temperature 0.1; 100 per scope | 200 generated sequences |
| Assemble evaluation panel | 2 AntiBMPNN designs + 4 designs imported from run_002 + native control | 7 fixed sequence pairs |
| Predict structures | Boltz2 Fv and ESMFold VH–linker–VL | 14 accepted models |
| Measure recovery and geometry | Native AAR; Cα scRMSD after framework fit | Candidate consistency vs same-predictor native model; native control vs 5I5K crystal |

AntiBMPNN maximum HCDR3 AAR is 0.4000 in each 100-sample scope. The closest candidate Fv is ig_hcdr3_s002 for Boltz2 (0.371 Å) and ig_hcdr3_s031 for ESMFold (0.139 Å).

[Workflow](../workflow.md) · [Tool records](../inputs/execution_records/tool_details.json) · [Original configuration](../inputs/execution_records/full_config.json)
