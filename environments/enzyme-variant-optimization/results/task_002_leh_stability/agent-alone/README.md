# LEH stability: agent-alone results

## What is compared

Our LEH_R004 and LEH_R003 predictions are compared with the selected native parent. Published T85I/T85V FoldX examples are reference values; they are not used as a reconstructed best combined sequence.

## Parent used

1NWW / UniProt Q9ZAG3, native 149-residue LEH; biological dimer.

A deposited native sequence provided a shared, traceable parent. Its complete correspondence to the study’s expression construct, including tags, was not established.

## Change from our selected parent

| Sequence | Predicted Tm (°C) | Change from parent (°C) |
|---|---:|---:|
| Selected parent | 52.1827 | 0.0000 |
| LEH_R004 | 53.4325 | +1.2498 |
| LEH_R003 | 52.5379 | +0.3552 |

## Calculations

DDGun values are unfolding ΔΔG in kcal/mol; published FoldX examples are folding ΔΔG in kJ/mol. Their signs, units and methods stay separate.

The benchmark keeps published numbers and values calculated in this work separately labeled. Parent-relative changes use the exact parent recorded for each candidate.

## Run status

The original structural assessment did not qualify the retained models. Their raw predictions are reported, with model findings retained in the execution records.

## Files

- [Benchmark report](../../../benchmark/task_002_leh_stability/comparisions/benchmark_report.pdf)
- [Published reference values](../../../benchmark/task_002_leh_stability/references.md)
- [Candidate sequences](sequences/candidates.fasta)
- [Full-precision candidate predictions](reference_comparison/predictions.csv)
- [Our stability predictions](steps/07_ddgun_stability/README.md)

## Execution records

- [Actual workflow](WORKFLOW.md)
- [Usage and time](USAGE_AND_TIME.md)
- [Sequence identities](sequences/identities.json)
- [Reference property comparison](reference_comparison/README.md)
- [Step outputs](steps/)
