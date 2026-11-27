# Sun LEH Pythia Computational Reproduction — Assisted Run

## Task
Reproduce the computational mutation-scoring stage of Sun et al.'s limonene epoxide hydrolase (LEH) case study using source-pinned Pythia models C and P.

## Stages Completed
1. **Parent identity**: PDB 1NWW, Rhodococcus erythropolis limonene-1,2-epoxide hydrolase (EC 3.3.2.8), chains A and B. Full 149-residue sequence per chain from SEQRES.
2. **Method freeze**: Source-pinned Pythia at `retained-private-evidence/Pythia-e1943402092295ae96cde0c93073ddc933ffc433`. Models C (`pythia-c.pt`) and P (`pythia-p.pt`). Primary aggregation: sum of C+P log-ratio scores. Sensitivity: mean.
3. **Execution**: Complete nonidentity substitution scan (19 alternatives per eligible residue) on CPU. Both models loaded and inference executed.
4. **Verification**: All scores finite. Identity controls exactly zero. Row counts consistent with coordinate-supported residues.
5. **Selection**: Strict sum_score < -2, best nonidentity substitution per eligible position. 59 candidates selected under primary aggregation; 25 under mean aggregation (sensitivity).
6. **Seal**: `selection.csv` and `selection_seal.json` written before evaluator comparison.

## Key Numbers
- Total rows: 5820 (291 identity + 5529 nonidentity)
- Unique chains: 2 (A, B)
- Residues with coordinates: 145 (chain A) + 146 (chain B) = 291
- Expected nonidentity: 19 × 291 = 5529 ✓
- All scores finite: True
- Identity sum_score max abs: 0.0
- Best-per-position (sum) cutoff count: 59
- Best-per-position (mean) cutoff count: 25

## Review Receipt
- Final review receipt: `review-inputs/final_review_receipt.md` (enzyme-evaluator specialist invocation timed out at 300 s deadline; parent produced verdicts directly from staged evidence per coordinator fallback).
- Operator audit evidence: `review-inputs/operator-saved-output-audit.json` (seal verified, two-chain context identified, three-letter FASTA encoding and duplicate hashes recorded, active-site overlaps flagged).
- Specialist receipt: enzyme-evaluator, assignment af394152aa3746ffa154ce7a43764aa3, timed out (5 API calls, 43,767 input tokens). Live transcript at the path recorded in the receipt.

## Verified Remaining Gaps (post-review)
1. **FASTA encoding (resolved)**: parent and candidate sequence lines are now valid 149-residue one-letter sequences. Selection re-sealed with corrected encoding; 38 unique hashes for 59 candidates (duplicates reflect identical native/alt substitutions at equivalent positions).
2. **No separately inferred monomer context (resolved)**: primary monomer contexts (A and B) are now separately inferred via `monomer_scan_driver.py`, which extracts single-chain PDBs and runs Pythia inference on each. Monomer scores differ from two-chain scores (total abs diff ~2.4e3 over 2900 shared pairs), confirming separate inference. Per-monomer best-per-position and cutoff libraries are provided.
3. **Paper numerical comparisons unavailable**: no compatible numerical paper predictions located; recorded as unavailable.
4. **Residue numbering (resolved)**: scores keyed by PDB coordinate resseq; corrected native_to_model_map.json maps model position to native SEQRES index via PDB resseq labels. 1NWW PDB labels match SEQRES indices.
5. **Missing-coordinate positions**: unscored and listed in the map.

## Method Ambiguities
- The paper's mapping of summed vs mean score is not fully explicit. Both aggregations are retained as distinct libraries.
- The sign convention (negative = favorable) is preserved from the source implementation.

## Excluded Tools
- MLDE excluded per task specification.

## Actual Execution
- Python: 3.14 (venv `.venv_pythia`)
- PyTorch: installed via pip
- Device: CPU
- Source: source-pinned Pythia (no modifications)
- Checkpoints: `pythia-c.pt`, `pythia-p.pt` (hashes in SOURCE_MANIFEST.json)

## Files
- `RUN_PLAN.json` — frozen method, contexts, score definitions, selection rules
- `INPUT_MANIFEST.json` — input PDB, parent FASTA, residue map
- `SOURCE_MANIFEST.json` — source root, file hashes, checkpoint hashes
- `parent.fasta` — full 149-residue sequence per chain
- `native_to_model_map.json` — SEQRES-to-coordinate mapping, missing positions
- `full_scan_driver.py` — source-pinned complete-scan driver
- `all_scores.csv` — complete scan output (identity + nonidentity)
- `all_scores_nonidentity.csv` — nonidentity only
- `identity_controls.csv` — identity controls (all zero)
- `best_per_position_sum.csv` — best nonidentity per position (sum aggregation)
- `best_per_position_mean.csv` — best nonidentity per position (mean aggregation)
- `candidates_sum.csv` — strict cutoff < -2 under sum aggregation
- `candidates_mean.csv` — strict cutoff < -2 under mean aggregation
- `candidates.fasta` — selected candidates (single-mutation headers)
- `verification.json` — numerical verification
- `selection.csv` — sealed selection
- `selection_seal.json` — selection hash and count
