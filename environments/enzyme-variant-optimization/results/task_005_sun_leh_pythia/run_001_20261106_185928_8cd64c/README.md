# Sun LEH / Pythia: specialist-assisted results

## Outcome

Computational execution and available-output review completed. The full scan contains 2,755 mapped nonidentity substitutions over 145 represented positions. The declared sum-score cutoff below −2 selects 33 mutations; the separate mean-score sensitivity selects 13. Exact historical coordinates/assembly and scaling provenance remain unresolved.

## Raw score leaders

| Mutation | Pythia summed score | Pythia mean score |
|---|---:|---:|
| D101V | -12.93692160 | -6.46846080 |
| T85V | -7.93473864 | -3.96736932 |
| M52W | -7.78284550 | -3.89142275 |

Scores are unitless. D101V changes catalytic Asp101; a high-ranked score does not establish retained activity. Four N-terminal positions without coordinates were not scored.

## Records

- [Workflow and tools](WORKFLOW.md)
- [Parent sequence](sequences/parent.fasta)
- [Selected mutation sequences](sequences/selected_mutations.fasta)
- [Full mapped scan](steps/01_pythia_scoring/all_scores.csv)
- [Declared sum-score library](steps/02_ranking/selected_sum_lt_minus2.csv)
- [Separate mean-score sensitivity](steps/02_ranking/selected_mean_lt_minus2.csv)

The saved proposer and critic reviewed the initial plan and final result batches. The scan is a computational scoring execution, not an experimental reproduction. No agent-alone supplemental property calculations are copied into this arm.

## Usage and time

Model: GPT-6.1-Sol via Codex. Final recorded snapshot: 16 November 2026.

| Measurement | Value |
|---|---:|
| Uncached input + output tokens | 708,625 |
| Cache-read tokens | 17,280,896 |
| Recorded activity span, hours | 0.89 |

The span includes pauses and follow-ups. Cached context is counted across calls; these numbers are not monetary charges or continuous scientific compute time.

## Execution identity

Run: `20261106_185928_8cd64c`. [Execution record](../../../runs/task_005_sun_leh_pythia/run_001_20261106_185928_8cd64c/run.json) · [Provenance](provenance.json).
