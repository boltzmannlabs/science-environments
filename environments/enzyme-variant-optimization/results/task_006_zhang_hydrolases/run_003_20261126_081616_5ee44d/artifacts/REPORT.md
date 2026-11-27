# task_006_zhang_hydrolases — computational reproduction report

**Workspace:** `run/v1/agent_with_specialist/` (config `v1`, approach `agent_with_specialist`)
**Settings:** `settings/task_006_zhang_hydrolases.json`; native goal session `20261126_081616_5ee44d`, `goals.max_turns=20` verified active.
**Scope:** computational stages only. MLDE excluded. No docking/MolProbity/redesign gates inherited.

## 1. Constructs (Stage 1 — complete)

Exact sequences extracted from the authoritative Zhang et al. supplement (`refs/original_supplement.docx`, DOI 10.1016/j.ijbiomac.2024.138274, section 3.3 FASTA records):

| Construct | Length | Sequence SHA256 | Role |
|---|---|---|---|
| cellulase_WT | 312 | `d345d0fa5fd6c7a3c7bab7013e9b4f78efb3e76f8cc410cad11026ea88c6fd57` | WT |
| cellulase_M2 | 312 | `d1e2ad6d3703189900a7a006037d492964d2ce2cc21f202ab170f223fd92fdeb` | retrospective background WT+G177P/L302R |
| beta_glucanase_WT | 215 | `1be527a773d049420b217cf4e7eded5f21468e74c9608033cdb34bec1184bb87` | WT |
| beta_glucanase_M5 | 215 | `82b31bef7b7a00d881900c44de25da61b16ef31d5cb820c9cd5d85c43dc65a20` | retrospective background WT+N38S/L45E/N65I/A142S/S196K |

Verbatim M5/M7 sequences also extracted and used to verify the documented final transitions. All background edits confirmed position-by-position; each additional mutation is labeled relative to its actual background, never as a WT single mutant.

## 2. Frozen protocol (Stage 2 — complete)

`RUN_PLAN.json`, `INPUT_MANIFEST.json`, `PYTHIA_RUN_PLAN.json`, `ESM_RUN_PLAN.json`, `ESM_INPUT_MANIFEST.json` were frozen before inference, with runner/checkpoint/sequence hashes. Conventions fixed before results: Pythia per-component negative LLR `−log(p/p_wt)`, aggregate C+P, strict `< −3.0`; ESM-2 masked-marginal `negative_log_likelihood_ratio = logp_wt − logp_mt`, strict `< −1.5`, alternate sign retained. Site exclusions declared unresolved (none invented). Reference prediction tables were used only after sealing.

## 3. WT structures (Stage 3 — complete, qualified)

Native `Protein_Structure_Prediction` (AlphaFold monomer), doc_id `6b07ee408b9d410520f9d79e` (17 min runtime, 15 platform credits). Downloaded artifacts: `predicted_structures.zip`, `result_summary.csv`. Both PDBs parse to the exact WT sequence, contiguous residue numbering 1–312 and 1–215, no tags/gaps/substitutions (`structures/structure_QA.json`). pLDDT 96.5/98.2; pTM 0.942/0.945 (preparation evidence, not a benchmarked property). **Qualification:** these are new same-construct models, not the original paper coordinate files; exact historical structural settings remain unresolved.

## 4. Pythia scans (Stage 4 — complete)

Source-pinned Wublab/Pythia commit `e1943402`, C/P checkpoints SHA256 `3cbfbfcc…`/`17523c65…`, CPU-only inference with verified source/structure/checkpoint hashes.

| Enzyme | Positions | Nonidentity substitutions | Identity controls | Strict C+P < −3.0 hits (unfiltered) |
|---|---|---|---|---|
| cellulase WT | 312 | 5,928 | 312 | 91 substitutions / 43 positions |
| β-glucanase WT | 215 | 4,085 | 215 | 64 substitutions / 25 positions |

Full grids and raw logits/probabilities retained in `pythia_runs/<run_id>/`. `paper_site_eligibility=unresolved` on every row; no paper-qualified library invented.

## 5. ESM-2 scans (Stage 5 — complete)

`esm2_t33_650M_UR50D` (651,043,254 params), official checkpoint SHA256 `ea9d0522…`, CPU fp32, ≤4 threads. Full masked-marginal procedure: 527 single-mask forward passes over M2 and M5; 10,013 nonidentity substitutions and 527 identity controls; both `negative_log_likelihood_ratio` and `mutant_minus_wt_logit` retained.

| Background | Substitutions | Strict neg-LLR < −1.5 hits (unfiltered) |
|---|---|---|
| cellulase_M2 | 5,928 | 41 |
| beta_glucanase_M5 | 4,085 | 55 |

Raw per-position logits (`raw_masked_logits.jsonl`) and six CSV tables per case retained in `esm_runs/esm_full_005/`.

## 6. Verification and seal (Stages 6–7 — complete)

`tools/verify_all.py` independently recomputed every score from retained raw outputs: grid coverage, finiteness, identity controls = 0, C+P arithmetic, both ESM signs, strict-cutoff flags and reconstructed variants. `verification.json`: `all_passed=true`.

`selection.csv` contains 251 unfiltered strict-cutoff hits (91+64 Pythia, 41+55 ESM-2) with contiguous unique ranks and full background-relative variant sequences in `candidates.fasta`. `selection_seal.json` hash `596a87290ece1132ba91cb98a8b48e4fd27142c7fcd3ec400f5667e9ab45b89f` matches the sealed file byte-for-byte; reference tables were not read before sealing.

## 7. Post-seal numerical comparison (Stage 8 — complete, qualified)

Same-variant joins by enzyme + background + exact mutation (reference Tables S1/S3/S5/S7, used only after sealing):

| Stage/background | Matched rows | MAE | Max abs diff | Our best | Paper best |
|---|---|---|---|---|---|
| Pythia cellulase WT | 47 | 1.786 | 11.249 | −11.648 | −12.587 |
| Pythia β-glucanase WT | 24 | 1.335 | 5.191 | −8.849 | −10.762 |
| ESM-2 cellulase M2 | 20 | **0.0002** | 0.0005 | −8.872 | −8.872 |
| ESM-2 β-glucanase M5 | 17 | 0.417 | 5.862 (I65Y) | −6.707 | −8.583 |

The declared negative-LLR convention reproduces the paper's negative ESM scores almost exactly; the opposite sign is retained only as a diagnostic column. Pythia divergence is consistent with the new AF2 structures differing from the paper's original coordinates. Best-versus-best fields are kept in a separate analysis; no sign-chosen-after-results claim is made. Experimental Tm/activity columns are not prediction targets.

## 8. Failures and recovery

Two recoverable runtime failures were diagnosed by enzyme-recovery, corrected without changing scientific inputs, and re-run with fresh IDs: (1) Pythia CPU guard tested the wheel's build-time CUDA flag instead of runtime visibility; (2) torch 2.9's `weights_only=True` default rejected `argparse.Namespace` in the trusted official ESM checkpoint — fixed with a call-scoped safe-globals allowlist. Failed run IDs preserved; no duplicate or acceptance-unknown submissions. Details in `errors.md`, `errors.jsonl`, `jobs.json`, and `specialist_receipts/`.

## 9. Independent review and boundary

`enzyme-evaluator` independently verified all nine requirement groups against actual artifacts (receipt: `specialist_receipts/EVALUATOR_RECEIPT.md`): all complete. **This is computational completion, not exact historical reproduction and not experimental improvement.** Unresolved: original paper site exclusions; original ESM checkpoint/settings; original structural coordinates; Pythia score divergence; β-M5 I65Y outlier. No finite monomer substrate was used to claim cellulose/β-glucan polymer activity.

## 10. Resource accounting

Native AlphaFold job: 1,014 s, 15 platform credits, doc_id `6b07ee408b9d410520f9d79e`. Local Pythia: 2 forward passes, ~1.6 s model time. Local ESM-2: 527 masked passes, ~523 s model time, max RSS 5.6 GiB, CPU-only, GPU untouched. Specialist token/tool usage itemized in `usage.json`. SCI LLM (`hy4-flash-free`/`opencode-go`) is reasoning/orchestration only, recorded separately from all scientific predictors.
