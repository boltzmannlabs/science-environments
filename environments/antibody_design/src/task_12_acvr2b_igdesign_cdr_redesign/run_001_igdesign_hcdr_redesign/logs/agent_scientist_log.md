# Recorded scientific activity

**Run:** `run_001_igdesign_hcdr_redesign`  
**Status:** completed

This retrospective summary is compiled from the saved scientific inputs, output tables and predicted structures. Step order follows the recorded workflow; wall-clock times are not reconstructed.

| Step | Tool and settings | Recorded result |
| --- | --- | --- |
| Prepare and verify inputs | PDB parsing + UniProt alignment | 5NGV chains H/L/A; ACVR2B fragment 93/93 = Q13705 mature 25-117 |
| Generate HCDR3-only pool | IgDesign; ACVR2B-holdout + ProteinMPNN holdout; 100 samples, T=0.5 | 44 unique |
| Generate HCDR123 pool | IgDesign; same conditioning; 100 samples, T=0.5 | 89 unique |
| Measure native recovery | Position-aligned per-CDR AAR | 1-shot / best-of-100 / mean per CDR |
| Select evaluation panel | Top 10 per scope by summed CE loss | 20 candidates |
| Predict structures | AlphaFold2-Multimer v3 (Boltzmann), rank-1 | native + 20 candidates |
| Measure scRMSD | Whole-Fv Kabsch onto 5NGV; C-alpha | 17/20 beat native HCDR123 (0.4434 A) |

HCDR3-only HCDR3 AAR is 0.875 (1-shot) and 0.875 (best-of-100), mean 0.750. HCDR123 AAR (best-of-100): HCDR1 1.000, HCDR2 0.875, HCDR3 1.000. Best HCDR123 scRMSD is T12-C008 at 0.3803 A (HCDR3-only) and T12-C011 at 0.3879 A (HCDR123 scope), versus native 0.4434 A.

[Workflow](../workflow.md) · [Tool records](../inputs/execution_records/tool_details.json) · [Original configuration](../inputs/execution_records/full_config.json)
