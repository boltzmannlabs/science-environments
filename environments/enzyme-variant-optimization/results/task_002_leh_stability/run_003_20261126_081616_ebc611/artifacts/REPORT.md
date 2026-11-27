# task_002_leh_stability — Final Report (v12, agent_with_specialist)

## Findings
All eight required stages executed with native Boltzmann tools and specialist reviews. Workflow complete. **No qualifying candidate**: a valid negative outcome, not an execution failure.

Parent: LEH from *Rhodococcus erythropolis* DCL14, PDB 1NWW, 149-aa SEQRES construct, chains A/B biological dimer. Chemistry from primary sources (RHEA:10700, CHEBI:16431, EMBO J 2003 PMC156771). HPN heptanamide in 1NWW is a surrogate, not the substrate; the authentic epoxide SMILES was used for complex modeling. Protected: Arg99/Asp101/Asp132 catalytic triad, Tyr53/Asn55 water positioning, A/B interface. MLDE excluded.

## Numerical parent comparison (frozen primary endpoint)
`Enzymes / tmPred_enzymes` (TemBERTureTm.mean3.3c17a7a2.encoder6c5c8a55.v1, degC, verified, predicted — NOT measured Tm):

- Parent baseline: **52.1827 °C** (replica std 2.8223 °C).
- Frozen bar: 52.1827 + 2.82 = **55.003 °C** (threshold = one parent replica std; coarse screen, not a significance test).
- Initial batch (12 unique variants): best `LEH_R1_setA_2` = 53.040 °C (**+0.858 °C**, below bar); 11/12 below parent.
- Result-driven revision (12 new variants, ThermoMPNN-negative site panel): best `LEH_R2_setD_3` = 53.264 °C (**+1.081 °C**, below bar and below replica noise).
- No variant reached the bar; sealed selection is empty.

## Generation and revision provenance
- `Random_Controlled_Mutagenesis` (attempt 7) returned 135–159-aa sequences with 117–145 substitutions — task-ineligible. enzyme-recovery diagnosed a contract/backend mismatch (no corrective parameterization), receipt `results/specialist_receipts/enzyme-recovery_mutagenesis_failure.json`.
- Switched to `stability-binding-ddg` with a renumbered chain (PDB residues 5–149 → 1–145). One failed subprocess (attempt 8, numbering mismatch), corrected by renumbering; MTSK prefix restored to each tool-generated 145-aa variant to keep the 149-aa construct (plain transfer of tool-generated edits, not LLM-side mutagenesis). 12 + 12 unique variants, 4 substitutions each, protected positions intact.
- enzyme-method receipts: initial route `.../enzyme-method_planning_receipt.json`; round-1 interpretation and revision plan `.../enzyme-method_round1_interpretation.json`.

## Orthogonal safeguards and trade-offs
- Parent MolProbity: clashscore 3.34, Rama outliers 0%, rotamer outliers 1.24%. Candidate structures (setA_2/setB_3): clashscore 22.06 / 30.25, Rama outliers 2.04% — quality regression.
- Candidate-specific AlphaFold structures: pLDDT 96.2 / 96.0; TM-score 0.988 / 0.979 vs parent. Structures are candidate-specific, not copied parent coordinates.
- Assembly: parent Prodigy A/B −14.8 kcal/mol; R2_setD_3 dimer model −13.1 kcal/mol (weaker).
- Solubility (NetsolP) and pHPred near parent; no expression-risk discrimination.
- Boltz2 parent dimer + authentic limonene-1,2-epoxide: LIG present in both models; min ligand–Asp101 distance 3.08 Å (descriptive). No explicit catalytic water modeled; catalytic geometry gate remains descriptive, not a pass/fail.
- No disulfides introduced; whole-variant folding ΔΔG (EvoEF1/DDGun/PACKMAN) has no connector job and local heavy compute is disabled — unresolved, not imputed.

## Failures, exclusions and limitations
- 23 submitted attempts: 1 ineligible-output generation, 1 backend failure (corrected), 1 malformed-sequence multimer discarded as invalid input (not used as evidence), plus transient credential-check error where the operation was not started (no job created). No duplicate pending/ambiguous submissions.
- `evaluation_observations.csv` initially contained a duplicate parent row; the independent evaluator caught it (helper exit 2). It was corrected to 24 unique rows; helper then exited 0 with `status: no_selection`.
- Cost records: native billing amounts/units are preserved in `usage.json`; several jobs returned no billing block; costs are unknown, never imputed as zero. Specialist token usage is self-reported; main-agent tokens are not included.
- Predictor deltas are computational, not experimental stability or catalysis. The paper's experimental winners and benchmark values were excluded from design inputs.

## Independent review
`evaluation.json` (enzyme-evaluator): workflow complete = true; qualification = false; empty selection justified. Receipt: `results/specialist_receipts/enzyme-evaluator_final_receipt.json`. Seal `selection_seal.json` sha256 `16d352eb...c489d3` verified unchanged.

## Next experimental questions
Would a different mutation region (e.g. interior packing or designed disulfide with explicit geometry checks) cross the frozen bar? Does the predicted +1 °C translate to measured thermal stability or activity? Requirement for a calibrated whole-variant folding endpoint remains open.
