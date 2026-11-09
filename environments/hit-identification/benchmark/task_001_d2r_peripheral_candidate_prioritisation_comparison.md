# Benchmark comparison — reference paper vs agent execution (step by step)

**Task:** `task_001_d2r_peripheral_candidate_prioritisation`
**Reference paper:** Kim S, Jo WH, Cha JO, Kim M-S (2026) *PLOS ONE* 21(8): e0355997, DOI 10.1371/journal.pone.0355997
**Agent run:** Boltzmann-platform execution, result files preserved unchanged in `results/task_001_d2r_peripheral_candidate_prioritisation/`
**Comparison date:** 2026-11-09

**Reading rules.** Vina scores are kcal/mol. The agent's affinity-model scores are unitless model outputs. DiffDock confidence is a pose-quality score. Values from different scales must not be subtracted, averaged or treated as calibrated equivalents. Overlap counts describe selection agreement between two computational workflows, not biological accuracy.

## Step-by-step comparison

| Step | Paper (method → threshold → outcome) | Agent (method → threshold → outcome) | Comparison |
|---|---|---|---|
| 1. Input library | SwissSimilarity (risperidone query) vs ZINC-20 → top-ranked hits → **400 analogs** | Same 400 supplied records (frozen library; similarity search not re-executed per task design) | Identical starting set; all 400 IDs, SMILES and ZINC IDs reconcile |
| 2. Drug-likeness screen | Lipinski RO5 gate: MW<500, HBD≤5, HBA≤10, MlogP≤4.15 | Not applied as a gate | Paper-specific step; agent relied on library pre-selection |
| 3. Brain-access screen | SwissADME BOILED-Egg (WLOGP+TPSA): high GI absorption + outside yolk (BBB-impermeable) → **226 retained** | Platform BBB/HIA labels constant across the library (non-discriminative) → ADMETlab 3.0 `P(BCRP+)` with a domperidone-calibrated bar (0.1237) → **criterion unsupported**: the endpoint is inhibitor probability, not substrate efflux | Both workflows sought a brain-access discriminator; the paper's is operational, the agent's is invalid as interpreted |
| 4. Primary binding screen | AutoDock Vina (docking-primary), cutoff = risperidone's own score **≤ −11.8 kcal/mol** → **8 hits** | Platform binding-affinity model (model-primary), cutoff = domperidone's own score **≤ −0.938** (unitless) → **30 Tier-A** | Different primary scores and different reference anchors (paper: risperidone; agent: domperidone) |
| 5. Docking execution | Vina 1.2.7 into SWISS-MODEL-repaired 6CM4; grid (10, 5.9, −9.5), 30 Å box; exh 16; **226 docked, 225 numerical** (id 380 missing); redocking RMSD 0.458 Å | Boltzmann Vina into chain-filtered 6CM4 crystal; 23 Å box at (9.925, 5.846, −9.582); exh 16; **400 docked, 3,993 poses**; automated interaction extraction failed (70 residues incomplete) | Same engine family, different receptor preparation and coverage; no equivalent redocking validation (exported poses chemically inconsistent with source for 126/400 formulas) |
| 6. Pose / interaction evidence | Discovery Studio Visualizer: Asp80(3.32) salt bridge + Trp373(6.48) + 7-residue hydrophobic pocket (mutagenesis-justified, Ki > 10,000 nM) → **4 of 8 retained** (27, 128, 360, 381) | Closest-atom distances from Vina poses to Asp114/Trp386 (same BW 3.32/6.48 positions): 111 = 3.30/3.72 Å (both in range), 120 = 4.17/5.38 Å (weak) | Paper applied a curated structural criterion; agent produced geometric distances only — interaction types not certified |
| 7. Dynamics (MD) | 100 ns GROMACS/CHARMM36m per complex; ligand + Cα RMSD → **#128 most stable** | Out of task scope; not executed | Paper-only step; excluded from grading |
| 8. Safety / selectivity profiling | pkCSM + ADMETlab 3.0 (BBB, hERG I/II, CYP, HIA/Caco-2) + off-target docking (5-HT2A/H1/α1B) + SA | Caco-2 (platform model) only; BCRP table invalidated (step 3); DiffDock pose check on 20 of 26 Tier-A compounds (confidence direction initially reversed) | Paper profiled more safety axes; agent's safety layer rests on the invalidated BCRP endpoint |
| 9. Final shortlist | **17, 21, 24, 27, 128, 321, 360, 381** (score ≤ −11.8, strictly) | **3, 5, 111, 2, 19, 25, 120, 10** (affinity-ranked Tier-A, controls excluded) | **Overlap 0/8** |
| 10. Final priorities | **#128, #381** (#128 best MD stability; #381 better BBB/hERG profile) | **111, 120** (highest BCRP-inhibitor scores — selection basis invalid as interpreted) | **Overlap 0/2** |

## Selection overlap

| Set | Paper | Agent | Overlap |
|---|---|---|---|
| Shortlist (8) | 17, 21, 24, 27, 128, 321, 360, 381 | 3, 5, 111, 2, 19, 25, 120, 10 | **0/8** |
| Final priorities (2) | 128, 381 | 111, 120 | **0/2** |

Directional disagreement on brain access: both agent priorities (111, 120) are BBB-permeable in the paper's SwissADME table; both paper priorities (128, 381) are BBB-restricted. This is a predictor disagreement between workflows, not an established error on either side.

## Score correspondence (all 16 shortlist members)

| ID | Selected by | Paper Vina (kcal/mol) | Agent Vina (kcal/mol) | Agent affinity model (unitless) |
|---|---|---:|---:|---:|
| 17 | Paper | −12.4 | −12.041 | −0.103 |
| 21 | Paper | −11.9 | −12.579 | −1.130 |
| 24 | Paper | −11.9 | −11.214 | −0.869 |
| 27 | Paper | −11.9 | −11.669 | +0.462 |
| 128 | Paper | −12.3 | −10.943 | +0.558 |
| 321 | Paper | −12.3 | −11.405 | −0.567 |
| 360 | Paper | −11.9 | −11.023 | +0.845 |
| 381 | Paper | −11.9 | −11.224 | +0.813 |
| 3 | Agent | not reported | −11.600 | −2.369 |
| 5 | Agent | not reported | −11.266 | −2.362 |
| 111 | Agent | not reported | −11.043 | −2.214 |
| 2 | Agent | not reported | −12.425 | −2.191 |
| 19 | Agent | not reported | −12.155 | −2.166 |
| 25 | Agent | −11.5 | −11.612 | −2.157 |
| 120 | Agent | not reported | −9.841 | −2.122 |
| 10 | Agent | −11.8 | −11.561 | −2.090 |

## Cross-method agreement

| Paired outputs | n | Pearson r | Spearman ρ |
|---|---:|---:|---:|
| Paper Vina vs agent Vina | 225 | **0.667** | 0.652 |
| Agent Vina vs agent affinity model | 400 | 0.330 | 0.280 |
| Affinity model vs DiffDock (minimum confidence, as submitted) | 20 | 0.196 | 0.322 |
| Affinity model vs DiffDock (maximum confidence, corrected direction) | 20 | 0.144 | 0.017 |

Moderate paper-vs-agent Vina agreement is expected across different receptor preparations (homology-repaired vs chain-filtered crystal; 30 Å vs 23 Å box). Weak model-vs-docking correlations flag genuine method disagreement; neither scale is experimental truth.

## Coverage

| Item | Paper | Agent |
|---|---|---|
| Docked compounds | 226/400 (225 numeric) | 400/400 (3,993 poses) |
| Property predictions | 400 (S1 table) | 398 (ids 195/290 failed) |
| External ADMET predictions | SwissADME/pkCSM/ADMETlab (web) | 180 retained successes; all 30 Tier-A values recoverable |
| MD | 5 × 100 ns | none (out of scope) |
| Second docking engine | — | DiffDock 20 of 26 attempted |
| Reference controls scored | Risperidone docked (−11.8 anchor) | Risperidone −2.597 / domperidone −0.938 (affinity model); domperidone BCRP 0.1237 |

## Confounds limiting interpretation

- Different receptor preparations (paper: SWISS-MODEL-repaired, not deposited, grid in model frame; agent: chain-filtered crystal with 70 incomplete residues) and box sizes; exhaustiveness identical (16).
- Agent Vina export drift: 126/400 first poses differ in molecular formula from source; 129 full InChIKeys differ; 5 of 8 shortlist members affected.
- Paper data-quality flags: S1 payload duplications (ids 51/308/327/354); id 380 lacks a numerical score; 8-hit filter requires strict inequality (ties 10/309 would give 10); Fig 2 caption/drawing conflicts; 0.458 vs 0.48 Å redocking discrepancy.
- The agent's brain-access criterion is invalid as interpreted (BCRP inhibitor probability used as substrate efflux), so its peripheral labels are not evidence-supported; its affinity ranking itself remains reproducible.
- No MD stage was executed by the agent (out of scope), so paper MD-based differentiation (#128) has no run counterpart.

## Verdict

The agent's execution is numerically verified and reproducible from its stated primary model, with materially better docking coverage than the paper (400 vs 226) and multi-method cross-checks. Its final peripheral-restriction conclusion is unsupported because the decisive endpoint was misinterpreted. Selection overlap with the paper is zero at both stages — a consequence of different primary scores, different reference anchors and different (or invalidated) brain-access criteria, not of execution failure. Full finding detail: [`FINAL_REPORT.md`](../FINAL_REPORT.md).
