# REPORT — task_004_athol1_substrate (agent_with_specialist, fresh authorized execution)

## Scope and freeze
- Task: AtHOL1 (PDB 3LCC) variants for improved computational support of non-native ethyl iodide + SAH -> ethyl-SAH sulfonium + iodide.
- Settings: `retained-private-evidence/task_004_athol1_substrate.json` (config sha256 d7f12b8c...); approach agent_with_specialist; MLDE excluded; no added token/financial/wall-time cap.
- Native goal verified active: profile `enzyme-autonomy-v12`, `goals.max_turns: 20`, session 20261126_081616_9622ce. Goals were not exhausted; no /goal resume needed.
- Frozen inputs: parent 235-aa SEQRES construct (sha256 7a11b6534e3d4c598e2eabe3bb5b2c190400ffb83dd426d8b0b4a021895e4d52), SAH (PubChem CID 439155, isomeric SMILES frozen), ethyl iodide `CCI`, protected positions/edit mask derived only from 3LCC geometry + Schmidberger 2010 mechanism (PMID 20376845), budgets (24 unique sequences incl. parent, <=8 substitutions, <=2 revisions with >=1 results-driven, <=60 submission attempts, <=5 final candidates). See `RUN_PLAN.json`.
- Primary endpoint: CatPred predicted kcat, maximize, same protocol on parent and candidates (`CatPred_Seq_id_Sequences_CCI_v1`); Km/Ki returned alongside. Units undocumented in output (kcat column ~10^log10kcat). This is an ML kinetic predictor — not measured activity, not a reaction barrier, not an electric-field/TS quantity. The SubTuner-style electric-field endpoint is absent from the catalog and remains explicitly unresolved; no DFT/MD substitute was used after results.

## What was executed (all native Boltzmann jobs; no MLDE)
1. **Parent baseline**: CatPred kcat 1598.689 (log10 3.204, SD_total 0.668), Km 0.62, Ki 0.414; Enzymes tmPred 47.437 C; Netsolp solubility 0.6556. Boltz2 parent complex (protein+SAH+CCI) failed on worker infrastructure (`pre_affinity_1.npz` missing).
2. **Generation round 1**: native Random_Controlled_Mutagenesis doc 6b07f1a77f. Whole-sequence output was task-ineligible (lengths 228-242, ~77-140 substitutions, indels) despite `mutaions_per_epoch=1` and protected `indices`. enzyme-recovery diagnosed a tool-semantics mismatch/contract gap. Deterministic difflib edit-list extraction (fixed method, concat-mismatch only, editable positions, first 8 ascending) produced 8 valid length-235 derived variants R1D0-7 with full lineage; they are labelled derived reconstructions, not native full-length outputs.
3. **Round-1 screen**: CatPred on all 8 variants + matched parent; all eight were WORSE on kcat (best R1D5 1462.59, delta -136.10). Stability (tmPred within 46.78-49.95 C) and solubility (0.58-0.66) near parent. Explicit honest negative result.
4. **Results-driven revision (round 2)**: observation-linked decision in `decisions.md` changed the editable mask from broad surface positions to the 9-15 A second shell around the SAH SD sulfur (179 -> 72 editable positions), keeping first-shell/cosubstrate/catalytic/tag positions protected. New native RCM doc 6b07fb977f; same extraction method produced 8 derived variants R2D0-7. Testable expectation: substitutions closer to the cosubstrate pocket alter the endpoint more than remote surface substitutions.
5. **Re-evaluation + combined mutant**: one CatPred batch (doc 6b080496c4) with matched parent + all 17 variants + directly evaluated combination R1R2_COMB (same SMILES=CCI for all). R2D1 = 1863.208 (delta +264.517); every other variant and the combination were below parent. Final Enzymes/Netsolp screens: R2D1 Tm 47.4387 C (parent 47.4371), solubility 0.6694 (parent 0.6556) — no material stability/solubility degradation.
6. **Structure/geometry/quality**: Boltz2 protein-only retry also failed (empty PDB). No de novo candidate complex exists. Genuine native `Catalytic_Geometry` measurement_only on the parent experimental 3LCC+SAH structure: SAH SD -> channel water W435 = 3.293 A; SAH SD -> surface chloride CL301 = 22.728 A (confirming the crystallographic chloride is not the catalytic halide). Genuine `Mol_Probity` measurement_only on the parent: clashscore 1.44, 0% Ramachandran outliers, 98.13% favored, 1 rotamer outlier. Candidate structures in `structure_evidence/` are sequence-threaded SURROGATES on the parent SAH-bound scaffold, explicitly NOT candidate-specific predicted structures; ethyl iodide was not placed/predicted in a ternary complex.
7. **Seal + independent review**: only R2D1 sealed (rank 1, no padding); `selection_seal.json` sha256 787517b8... verified. Independent enzyme-evaluator reviewed the sealed bundle, wrote `evaluation.json`/`evaluation_observations.csv`, and ran the offline helper: `status incomplete`, R2D1 `unresolved`, eligibility `unknown` because the candidate-specific structure/quality/geometry gate is unresolved.

## Numerical parent comparison (same CatPred batch, same SMILES)
| candidate | predicted kcat | signed delta vs parent | Tm (degC) | Netsolp solubility |
| --- | --- | --- | --- | --- |
| PARENT_3LCC | 1598.689 | 0 | 47.437 | 0.6556 |
| R2D1 | 1863.208 | **+264.517** | 47.439 | 0.6694 |
| all other 16 variants + R1R2_COMB | 772.6-1515.8 | -82.9 to -826.1 | (round1 from screen) | (from screen) |

R2D1 edits: T30A, L71W, V72Y, V81N, V82P, S99F, L101H, A102E (8 substitutions; focus shell 9-15 A from SAH SD; no protected position or tag changed).

## Stage completion status
- Completed: parent preparation/baseline, tool generation (both rounds), property screening, results-driven revision and re-evaluation including direct combined mutant, endpoint comparison, sealing, independent sealed evidence review.
- Partial/unresolved: candidate-specific reaction-complex structures with both reacting partners; candidate-specific MolProbity; candidate-specific Catalytic_Geometry; transition-state/electric-field reaction endpoint. These are reported as unresolved, not substituted or assigned zero.
- No qualifying improvement in experimental catalysis is claimed; the +264.5 delta is an in-silico predictor value with undocumented units and unverified applicability to AtHOL1 + ethyl iodide.

## Quarantine and integrity
An unintended web-search snippet exposed a published winner mutation and a prior-engineering pocket residue list; both were quarantined in `private/UNINTENDED_EXPOSURE.md` and excluded from masks, generation, controls, ranking and observations. The independent evaluator confirmed zero occurrences in design inputs/candidates/observations/selection.

## Specialist receipts and usage
- `native_receipts/method_receipt.md`, `recovery_receipts.md`, `evaluator_receipt.md`; full reports `planning_report.md` and `evaluation.json`.
- Specialist model usage: 5,045,634 input + 81,174 output tokens across 93 tool calls (enzyme-method 1.27M/24k; recovery 0.35M/7.6k + 0.87M/18k; evaluator 2.56M/31k). Cost fields returned 0.0 with status unknown.
- Scientific platform usage: 12 native jobs; known billing $16 (jobs without returned billing listed in `usage.json`, not assumed zero). All under the 60-attempt budget. Cumulative accounting including specialists is in `usage.json`; no credentials/signed URLs retained in `jobs.json`.

## Interpretation / next experimental questions
This is a computational case comparison with a single repeat; no general performance claim. The only supported numerical improvement is R2D1 on a CatPred proxy. Because candidate-specific structural evidence is missing, R2D1's eligibility is `unknown`. Next questions: obtain a candidate-specific protein+SAH+ethyl-iodide complex (working structure predictor or co-substrate-aware docking with verified states) and a source-backed catalytic/electric-field method; then test whether R2D1's focus-shell substitutions (V81N/V82P/L71W/V72Y etc.) preserve the reactive geometry relative to the parent W435 channel.
