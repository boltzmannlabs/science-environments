# Execution summary

**Run:** `run_002_esmfold_proteinmpnn_evaluation`  
**Status:** completed

This retrospective summary is compiled from the saved scientific inputs, output tables and accepted models. Step order follows the recorded workflow; wall-clock times are not reconstructed.

| Step | Tool and settings | Recorded result |
| --- | --- | --- |
| Prepare panel | Saved FASTA and run_001 shortlist | 7 sequences |
| Predict scFv structures | ESMFold | 7 accepted single-chain models |
| Score sequences | ProteinMPNN score-only on each sequence’s own ESMFold backbone | Negative log likelihood; lower is preferred |
| Summarize | Whole-scFv confidence and sequence properties | Seven-row metrics table |

Candidate ESMFold pLDDT 85.07–85.84; reference 85.40. Lowest candidate own-backbone ProteinMPNN NLL: cet_008_r1_s18, 1.4510; reference 1.4692.

[Workflow](../workflow.md) · [Tool records](../inputs/execution_records/tool_details.json) · [Original configuration](../inputs/execution_records/full_config.json)
