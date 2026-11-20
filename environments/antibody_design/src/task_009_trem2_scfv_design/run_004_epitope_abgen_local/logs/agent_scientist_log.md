# Recorded scientific activity

**Run:** `run_004_epitope_abgen_local`  
**Status:** completed

This retrospective summary is compiled from the saved scientific inputs, output tables and accepted models. Step order follows the recorded workflow; wall-clock times are not reconstructed.

| Step | Tool and settings | Recorded result |
| --- | --- | --- |
| Prepare features | Explicit chain-local CDR masks; saved epitope and feature tensors | 10/10 recorded mask checks |
| Generate backbones | epitope_abgen local core; 4 samples; seed 2026; max_tokens 384 | 4 finite backbone samples |
| Generate sequences | Local AntiBMPNN; 40 sequences per backbone | 160 sequences; 94 pass gates (0/25/32/37) |
| Evaluate complexes | Matched Boltz2; exact sequence identity check | 3 accepted predictions; s2_cand13 retained |

Best candidate s2_cand13: ipTM 0.6039 vs matched reference 0.8987. Sample-0 designs fail the CDR cysteine gate. The evaluated panel has one replacement for an unverified prediction, so only the three saved verified models enter the benchmark.

[Workflow](../workflow.md) · [Tool records](../inputs/execution_records/tool_details.json) · [Original configuration](../inputs/execution_records/full_config.json)
