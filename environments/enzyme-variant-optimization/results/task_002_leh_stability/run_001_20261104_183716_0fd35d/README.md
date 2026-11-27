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

## Findings
Closed: no supported final candidate. Reviewed empty selection retained.

## Files

- [Benchmark report](../../../benchmark/evaluation/task_002_leh_stability/comparisons/benchmark_report.md)
- [Published reference values](../../../benchmark/reference_data/task_002_leh_stability/references.md)
- [Candidate sequences](sequences/sha256-2ca205df230cd9785a368d997eb59f8cf50d518a8303dd0d1fd221569a9a7a85-b89bca6b_unreported_unreported_0fd35d_unreported_unreported.fasta)
- [Full-precision candidate predictions](reference_comparison/sha256-aaba3d1b64c5fc66d63ecc6167f9d57ca0378f06da99ef281381b15d1cffbfae-ad5cb62c_unreported_unreported_0fd35d_unreported_unreported.csv)
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
| Parent continuation lineage | 13 | 546,739,653 |
| Delegated specialists | 0 | 0 |
| Parent + specialists, deduplicated | 13 | 546,739,653 |

Reasoning tokens are already included in output. These are persisted session counts, not monetary charges or continuous compute time. Earlier usage files retain their original snapshot and are not added to this table. See the [execution record](../../../runs/task_002_leh_stability/run_001_20261104_183716_0fd35d/run.json) for session membership, exclusions and component totals.

Recorded activity span: 86.37 hours, including pauses and follow-ups.

## Execution identity

Run: `20261104_183716_0fd35d`. [Execution record](../../../runs/task_002_leh_stability/run_001_20261104_183716_0fd35d/run.json) · [Provenance](provenance.json).
