# RML stability: agent-alone results

## What is compared

Our retained RML_R2_02 and RML_R2_01 predictions are compared with our selected parent. No paper winner is reconstructed for this update. Published FoldX and docking values remain separate reference measurements with their predictor names.

## Parent used

3TGL mature RML, 269 residues.

The preparation step had not established the study’s exact laboratory sequence. Both approaches therefore used the same deposited 3TGL sequence as a traceable public parent. The paper describes a 6QPR-based homology model; that model template does not by itself identify its complete starting sequence.

## Change from our selected parent

| Sequence | Predicted Tm (°C) | Change from parent (°C) |
|---|---:|---:|
| Selected parent | 46.9782 | 0.0000 |
| RML_R2_02 | 48.0504 | +1.0722 |
| RML_R2_01 | 47.9878 | +1.0096 |

## Calculations

Vina scores depend on the receptor, ligand preparation and search settings. DDGun reports unfolding ΔΔG: positive indicates stabilization; FoldX folding ΔΔG uses the opposite favorable sign.

The benchmark keeps published numbers and values calculated in this work separately labeled. Parent-relative changes use the exact parent recorded for each candidate.

## Findings
Closed with limitations. Design and independent review retained; qualification/common metric gaps remain.

## Files

- [Benchmark report](../../../benchmark/evaluation/task_001_rml_stability/comparisons/benchmark_report.md)
- [Published reference values](../../../benchmark/reference_data/task_001_rml_stability/references.md)
- [Candidate sequences](sequences/sha256-54b38dda9b894abf177686071b3a7418cc34a9e22774a8b1aef2a9a9ed620cb1-b89bca6b_unreported_unreported_92629f_unreported_unreported.fasta)
- [Full-precision candidate predictions](reference_comparison/sha256-bcca74cc9947fde0d317995462ca7f278be1f18f2f5b689cc554dff084f66174-ad5cb62c_unreported_unreported_92629f_unreported_unreported.csv)
- [Our stability predictions](steps/07_ddgun_stability/README.md)

## Execution records

- [Actual workflow](WORKFLOW.md)
- [Sequence identities](sequences/identities.json)
- [Reference property comparison](reference_comparison/README.md)
- [Step outputs](steps)

## Usage and time

Native persisted usage snapshot: 27 November 2026. Parent continuations and linked specialists are counted separately.

| Counting scope | Sessions | Tokens (input + output + cache) |
|---|---:|---:|
| Parent continuation lineage | 9 | 647,551,665 |
| Delegated specialists | 0 | 0 |
| Parent + specialists, deduplicated | 9 | 647,551,665 |

Reasoning tokens are already included in output. These are persisted session counts, not monetary charges or continuous compute time. Earlier usage files retain their original snapshot and are not added to this table. See the [execution record](../../../runs/task_001_rml_stability/run_002_20261104_183717_92629f/run.json) for session membership, exclusions and component totals.

Recorded activity span: 77.00 hours, including pauses and follow-ups.

## Execution identity

Run: `20261104_183717_92629f`. [Execution record](../../../runs/task_001_rml_stability/run_002_20261104_183717_92629f/run.json) · [Provenance](provenance.json).
