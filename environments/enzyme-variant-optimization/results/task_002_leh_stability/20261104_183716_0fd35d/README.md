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

Closed: no supported final candidate. Reviewed empty selection retained.

## Files

- [Benchmark report](../../../benchmark/evaluation/task_002_leh_stability/comparisons/benchmark_report.md)
- [Published reference values](../../../benchmark/reference_data/task_002_leh_stability/references.md)
- [Candidate sequences](sequences/candidates.fasta)
- [Full-precision candidate predictions](reference_comparison/predictions.csv)
- [Our stability predictions](steps/07_ddgun_stability/README.md)

## Execution records

- [Actual workflow](WORKFLOW.md)
- [Sequence identities](sequences/identities.json)
- [Reference property comparison](reference_comparison/README.md)
- [Step outputs](steps)

## Usage and time

| Measurement | Value |
|---|---:|
| Uncached input + output | 10,068,190 |
| Cache-read tokens | 561,620,864 |
| Reported cumulative total, lower bound | 571,689,054 |
| Recorded activity span, hours | 86.37 |

Recorded native activity includes pauses and follow-ups. Token totals include repeated cached context; these are not compute hours or cost estimates. Snapshot: 16 November 2026.

## Execution identity

Run: `20261104_183716_0fd35d`. [Execution record](../../../runs/task_002_leh_stability/20261104_183716_0fd35d/run.json) · [Provenance](provenance.json).
