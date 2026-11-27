# Zhang cellulase / β-glucanase: specialist-assisted results

## Outcome

Computational structure prediction, mutation scoring and available-output reviews completed. Ten AlphaFold2 predictions cover two WT constructs; the four nonidentity mutation scans contain 20,026 rows. Exact historical settings and site-exclusion eligibility remain unresolved. These are computational results, not new experimental improvements.

## Executed scans

| Background | Method | Nonidentity substitutions |
|---|---|---:|
| cellulase-WT | Pythia | 5,928 |
| beta-glucanase-WT | Pythia | 4,085 |
| cellulase-M2 | ESM-2 | 5,928 |
| beta-glucanase-M5 | ESM-2 | 4,085 |

## Score leaders

These are retrospective lowest scores under the listed conventions, not qualified final selections. Pythia leaders use the C+P summed score; ESM-2 leaders use WT-minus-mutant NLLR. ESM sign conventions remain separate columns in the full exports.

| Background | Method | Mutation | Score |
|---|---|---|---:|
| cellulase-WT | Pythia | T131D | -13.25570536 |
| beta-glucanase-WT | Pythia | N65L | -9.04114771 |
| cellulase-M2 | ESM-2 | T257K | -8.87229919 |
| beta-glucanase-M5 | ESM-2 | P10D | -6.70656013 |

## Records

- [Workflow and tools](WORKFLOW.md)
- [Exact scoring backgrounds](sequences/sha256-7da35e0547e4cd0bafaf7d13496b4880bc95ddc2bd3eb3adbb05818c0aebe71b-2d9c0b7b_unreported_unreported_bbf4c0_unreported_unreported.fasta)
- [Retrospective score-leader sequences](sequences/sha256-6e9d5fb27a08fada539d796a5ee64b94854fc71be630dc38f58cfca8b44839ed-493a42a8_unreported_unreported_bbf4c0_unreported_unreported.fasta)
- [Ten structure-model quality records](steps/01_structure_prediction/sha256-186d2563db2aa046f4aa35e7f991446ccd71876d4a45596374aab719904c8e8e-768aacf2_unreported_unreported_bbf4c0_unreported_unreported.csv)
- [WT Pythia scans](steps/02_pythia_scoring)
- [M2/M5 ESM-2 scans](steps/03_esm_scoring)
- [Score-leader definitions](steps/04_ranking/sha256-2bd104e43303cb73d44b27cddf3b4299a3c439b380fa85369384705b50e28e7f-70f88dec_unreported_unreported_bbf4c0_unreported_unreported.csv)
- [Published-score agreement](steps/04_ranking/sha256-264fc8577fcec58059dbc8b0752faa3b44978495190065764fab7239c0086b80-465dfac9_unreported_unreported_bbf4c0_unreported_unreported.csv)

Proposer/critic reviews and final available-output checks were retained. Pythia and ESM-2 use different declared backgrounds. Original intermediate backgrounds were supplied retrospectively; no blind discovery or experimental gain is inferred. Agent-alone supplemental property predictions are not attributed to this arm.

## Usage and time

Model: GPT-6.1-Sol via Codex. Final recorded snapshot: 16 November 2026.

| Measurement | Value |
|---|---:|
| Uncached input + output tokens | 1,622,460 |
| Cache-read tokens | 68,075,904 |
| Recorded activity span, hours | 12.78 |

The span includes pauses and follow-ups. Cached context is counted across calls; these numbers are not monetary charges or continuous scientific compute time.

## Execution identity

Run: `20261107_033146_bbf4c0`. [Execution record](../../../runs/task_006_zhang_hydrolases/run_001_20261107_033146_bbf4c0/run.json) · [Provenance](provenance.json).
