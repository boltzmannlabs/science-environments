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
- [Parent sequence](sequences/sha256-463e2a8309e362f0cec6109553902d3c6362627d9781bd233258b7564b7937a3-e29eefc5_unreported_unreported_8cd64c_unreported_unreported.fasta)
- [Selected mutation sequences](sequences/sha256-48428d7469cba1d5c48d0f187896a4383b69fefdd8a39c6e096664457b37bf9d-bea6ab19_unreported_unreported_8cd64c_unreported_unreported.fasta)
- [Full mapped scan](steps/01_pythia_scoring/sha256-8415d11a2d455dc56aa085505f7f77df19e84801b87cb42ef5b3f1ce760edf8d-cdab9822_unreported_unreported_8cd64c_unreported_unreported.csv)
- [Declared sum-score library](steps/02_ranking/sha256-2d999a852ef63883924554f75fbc087e172b0b79280ca281eef7bba14722c998-78d208e4_unreported_unreported_8cd64c_unreported_unreported.csv)
- [Separate mean-score sensitivity](steps/02_ranking/sha256-0b7eb01cf31b1822098e2e06d1e1abbe80bc02acb0fb8c3e0804c1be5575065f-7174ff3f_unreported_unreported_8cd64c_unreported_unreported.csv)

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
