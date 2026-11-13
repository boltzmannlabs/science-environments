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

## Run status

The original run retained two conditional candidates. Full functional/structural qualification remains open. These are computational predictions; experimental half-life was not measured.

## Files

- [Benchmark report](../../../benchmark/task_001_rml_stability/comparisions/benchmark_report.pdf)
- [Published reference values](../../../benchmark/task_001_rml_stability/references.md)
- [Candidate sequences](sequences/candidates.fasta)
- [Full-precision candidate predictions](reference_comparison/predictions.csv)
- [Our stability predictions](steps/07_ddgun_stability/README.md)

## Execution records

- [Actual workflow](WORKFLOW.md)
- [Usage and time](USAGE_AND_TIME.md)
- [Sequence identities](sequences/identities.json)
- [Reference property comparison](reference_comparison/README.md)
- [Step outputs](steps/)
