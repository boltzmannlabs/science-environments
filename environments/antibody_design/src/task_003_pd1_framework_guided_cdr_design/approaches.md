# Task 003 approaches

Task: `task_003_pd1_framework_guided_cdr_design`
Target: human PD-1 ligand-binding surface
Format: paired VH/VL Fab variable domains

## Considered approaches

| ID | Approach | Status | Suitability |
|---|---|---|---|
| W1 | RF-Antibody: `rfdiffusion_proteinmpnn` | Selected primary; not submitted | Best single workflow for paired framework-fixed CDR backbone and sequence generation. |
| W2 | Epitope AbGen: `epitope_abgen` followed by backbone-to-sequence generation | Selected comparison; not submitted | Explicitly conditions generation on PD-1/PD-L1 contact residues. |
| W3 | AgCDR-Diff: `agcdr_diff` followed by backbone-to-sequence generation | Fallback; not submitted | Requires pre-positioned antibody and antigen; produces backbones only. |
| W4 | AntiBMPNN sequence refinement | Conditional refinement; not submitted | Requires an existing CDR backbone and is not a standalone workflow for the empty framework template. |
| W5 | `boltzgen`, random generation, CDR generator, or IG-design | Not selected | Does not directly satisfy the fixed paired framework plus explicit epitope requirement under the available contracts. |

## Selection

W1 is the primary workflow because it is paired, target-aware, framework-conditioned,
and produces CDR backbones plus sequences in one platform job. W2 is retained as an
independent epitope-conditioned comparison. Both feed the same sequence QC, Boltz2,
ipSAE, property, stability/DDG and local validation ladder.

## Execution boundary

The platform upload reached partial validation: PDB syntax passed, while chain selection
and scientific suitability required explicit approval. The approval dialog timed out.
No Boltzmann design job was submitted. This is recorded as pending, not completed.
