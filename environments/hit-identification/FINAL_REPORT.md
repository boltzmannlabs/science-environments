# Final Report — task_001_d2r_peripheral_candidate_prioritisation

**Reference paper:** Kim S, Jo WH, Cha JO, Kim M-S (2026) Identification of novel peripherally restricted risperidone-like dopamine D2 receptor antagonists for prolactin-mediated neuroprotection through a multi-stage in silico screening. *PLOS ONE* 21(8): e0355997. https://doi.org/10.1371/journal.pone.0355997
**Task:** `environments/hit-identification/tasks/task_001_d2r_peripheral_candidate_prioritisation.md` (identical to the executed task)
**Agent submission:** `d2r_peripheral_final_deliverables.zip` — ranked_candidates.csv, assessment.json, report.md plus supporting artifacts, preserved unchanged under `results/task_001_d2r_peripheral_candidate_prioritisation/`
**Review date:** 2026-11-09 · **Location:** `environments/hit-identification/` · review validator: PASS

**Headline verdict:** The agent executed substantial, well-covered, honestly-logged scientific work and delivered every required file. Its selection ranking is reproducible from its stated primary model. Its central scientific claim — peripheral restriction of the two priority compounds — rests on a single misinterpreted prediction endpoint and is **unsupported as written**. Shortlist overlap with the paper: 0/8; priority overlap: 0/2 (different workflows, not error).

---

## 1. Reference paper — workflow and evaluation metrics

Five-stage in-silico screen for peripherally restricted, risperidone-like D2R antagonists (prolactin-elevation strategy without CNS exposure). All values below are paper-stated (Methods/Results), verified against the full text.

### Stage 1 — Similarity screening (SwissSimilarity → ZINC-20)

| Metric | Value |
|---|---|
| Query | Risperidone |
| Output | Top-ranked hits by similarity score → **400 analogs** (#1–#400); no numeric similarity cutoff published |

### Stage 2 — ADMET filter (SwissADME as the library-wide gate; pkCSM + ADMETlab 3.0 shortlist-level)

| Metric | Cutoff / role |
|---|---|
| MW | < 500 Da |
| H-bond donors | ≤ 5 |
| H-bond acceptors | ≤ 10 |
| MlogP | ≤ 4.15 |
| BOILED-Egg position | High GI absorption + **outside yolk** (low BBB), via WLOGP + TPSA — **the library-wide gate, together with RO5** |
| pkCSM | logBB, logPS, P-gp substrate category — applied to shortlisted candidates (Table 3), not the 400→226 gate |
| ADMETlab 3.0 | BBB penetration probability, P-gp classification — shortlist-level (Table 3), not the 400→226 gate |
| Exclusion rule | Any RO5 violation **or** predicted BBB-permeable → excluded |
| Result | **226 candidates** |

### Stage 3 — Docking (AutoDock Vina 1.2.7 into 6CM4 repaired by SWISS-MODEL)

| Metric | Value |
|---|---|
| Receptor | PDB 6CM4 (D2R–risperidone), missing atoms/loops repaired via a SWISS-MODEL homology model |
| Grid | Center (10, 5.9, −9.5) Å, 30×30×30 Å |
| Search settings | Exhaustiveness 16 / max 9 modes / energy range 3 kcal/mol; flexible side-chain protocol |
| Protocol validation | Reference redocking heavy-atom RMSD **0.458 Å** (Fig 3 caption states 0.48 Å — paper-internal inconsistency) |
| Score cutoff | ≤ **−11.8 kcal/mol** (= risperidone's own Vina score) |
| Result | **8 hits**; best #17 at −12.4 kcal/mol |
| Table 2 extras | TPSA, WLOGP, synthetic accessibility 3.43–5.05, RO5 violations = 0 for all 8 |

### Stage 4 — Interaction filter (Discovery Studio Visualizer)

| Metric | Criterion (paper's "Key interaction analysis") |
|---|---|
| Salt bridge | Tertiary amine···Asp80(3.32) — model numbering; Asp114 in the full-length/6CM4 construct |
| Hydrophobic pocket | Engagement of 7 residues: Cys84(3.36), Thr85(3.37), Ser163(5.46), Phe164(5.47), Phe376(6.44), **Trp373(6.48)**, Phe377(6.52) |
| Justification | Mutagenesis: loss of Asp3.32/Trp6.48 contact → Ki > 10,000 nM (paper refs [22],[39]) |
| Protocol check | Redocked risperidone reproduced 4/7 pocket contacts + the Asp80 contact |
| Result | **4 advanced**: #27, #128, #360, #381 |

### Stage 5 — MD (CHARMM-GUI → GROMACS 2023.3, 100 ns)

| Metric | Values |
|---|---|
| Setup | CHARMM36m + CGenFF, ~256 POPC, TIP3P, 0.15 M NaCl, 2 fs, PME/LINCS, 1.875 ns equilibration |
| Ligand RMSD (100 ns) | Risperidone lowest; **#128 most stable of candidates**; #27 intermediate; #381 mobile; #360 largest displacement |
| Receptor Cα RMSD | #27 0.276, #128 0.298, #360 0.382, #381 0.265 nm; risperidone 0.259 nm |
| RMSF (S2 Fig) | All comparable to risperidone (descriptive) |

### Stage 6 — Safety/selectivity profiling (final-2 selection)

| Metric | Use |
|---|---|
| BBB restriction (pkCSM + ADMETlab 3.0 + SwissADME) | #128/#360/#381 restricted; #27 conflicting across platforms |
| hERG (pkCSM + ADMETlab 3.0) | hERG I: only domperidone positive; hERG II: all four; **hERG-10 μM: #381 lower than risperidone/domperidone** |
| HIA + Caco-2 | #128/#381 above domperidone, ≈/above risperidone |
| CYP panel | Liabilities flagged; predictors disagree |
| Off-target docking | 5-HT2A (6A93) −7.4 to −7.9; H1 (3RZE) #381 ≈ domperidone; α1B (7B6W) #128 = −11.2 |
| SA score | #128 ≈ risperidone; #381 slightly worse |

**Final funnel:** 400 → 226 → 8 → 4 → **#128 (ZINC000019333157)** + **#381 (ZINC000019337359)** — complementary profiles (#128 best MD stability; #381 better BBB/hERG predictions). Decision data fully published (S1: 400 compounds; S2: 226 docking scores; S1 Dataset: RMSD curves).

**Independent audit findings on the paper's data:** S1 prediction-payload duplication for ids 51/308/327/354; id 380 has no numeric S2 score (→ 225 usable score pairs); **S1 conjunction discrepancy — 226 records are BBB-negative but only 225 are BBB-negative AND high-GI, versus the paper's stated 226 for the conjunction**; the paper's 8-hit filter reproduces only under strict inequality (equal-score ids 10/309 would yield 10); Fig 2 caption/drawing identity conflicts; redocking RMSD 0.458 vs 0.48 Å between text and caption; the SWISS-MODEL receptor is not deposited (grid coordinates are in the model frame); Asp80/Trp373 are model-numbering (Asp114/Trp386 in the construct) with inconsistent Phe mappings.

---

## 2. Task design assessment

- **The task was clearly specified.** Objective, inputs, constraints, deliverable format (top 8 + 2 priorities + 3 files) and edge-case protocols (NEEDS_INPUT / PARTIAL / do not pad the shortlist) are unambiguous. The agent followed the format exactly and self-corrected its 2/3 eligibility error — evidence it read and applied the task correctly.
- **"Restricted brain access" is explicitly named** as one of three required scientific criteria: "Support recommendations with evidence relevant to D2R, restricted brain access and intestinal absorption."
- **Numeric evaluation ranges are deliberately absent — by design.** (i) Defining and justifying measures is the tested competency ("Define and justify the measures, selection criteria and trade-offs used to assess these goals"). (ii) Calibration is supplied through reference controls (risperidone = high-affinity CNS reference; domperidone = peripheral reference) instead of fixed numbers — the same philosophy the paper itself used (its bar was risperidone's own docking score, not a universal constant). (iii) Hardcoded thresholds would have embedded this same endpoint misinterpretation (§4.1) into the task definition itself. (iv) No hidden bars exist: evaluation graded execution, deliverables, reproducibility from stated criteria, correct evidence interpretation, and honest failure reporting.
- Evaluator-facing material lives in `benchmark/`, separate from the agent-facing `tasks/` — by design.

---

## 3. Agent execution summary

| Stage | What the agent did | Retained outcome |
|---|---|---|
| Target prediction | Boltzmann `global_binding_affinity` (the platform's binding-affinity model; score units unestablished) on all 400 compounds + controls | 400 + 2 control predictions |
| Properties | Boltzmann `Property_Prediction` (Caco-2, MW, TPSA, LogP, HBD/HBA) | 398/400 (ids 195/290 invalid SMILES) |
| Brain access | Platform BBB/HIA labels constant → ADMETlab 3.0 direct API; retried pending Tier-A compounds; queried controls | 180 library successes retained; all 30 Tier-A BCRP values recoverable |
| Docking | Boltzmann `Vina_basic_docking`, 400 × 10 poses, 23 Å box at (9.925, 5.846, −9.582), exhaustiveness 16 | 3,993 poses; automated interaction extraction failed (70 residues missing heavy atoms) |
| Contact analysis | Closest-atom distances computed directly from poses to Asp114/Trp386 | Distances retained; interaction types not certified |
| Pose cross-check | Boltzmann DiffDock on the 26-compound Tier-A subset | 20 numerical results; 6 failure rows |
| Ranking | Affinity-primary (domperidone −0.938 Tier-A bar); BCRP annotation; Caco-2 | Top 8 = **3, 5, 111, 2, 19, 25, 120, 10**; priorities **111 & 120**; 2/3 pair third-qualified |

Coverage and failure logging were honest (invalid SMILES, rate-limit retries, failed external dataset downloads, receptor-prep incompleteness all documented). The 2/3 eligibility self-correction was sound practice (RDKit-verified distinct methylated analog, enantiomer pair).

**Evidence provenance:** the eleven result files are byte-identical to the original agent submission (hash-verified during review).

---

## 4. Identified deficiencies in the agent submission

### 4.1 Primary deficiency — misinterpretation of the BCRP endpoint

```
Platform BBB/HIA labels → constant → discarded              [correct]
ADMETlab 3.0 queried, BCRP endpoint selected                [legitimate step]
P(BCRP+) = 0.65 read as "65% chance of being pumped
out of the brain → restricted brain access"                 [misinterpretation occurs here]
```

ADMETlab's `P(BCRP+)` is the probability the compound **inhibits** the BCRP transporter — not that it is a BCRP substrate effluxed from the brain. Every downstream element inherited this misinterpretation: all peripheral/CNS labels; the "5.2×/4.7× domperidone efflux" claims; the domperidone-calibrated bar of 0.1237 (calibrated precision on a wrongly interpreted quantity); the selection of **111 and 120 as priorities** (they are simply the two highest BCRP-*inhibitor* scorers); and the "only 3 compounds are peripherally restricted" central finding. The numbers themselves were computed correctly; misinterpreting one endpoint label invalidated every peripheral-restriction conclusion built on it.

### 4.2 Additional material deficiencies

These findings invalidate or contradict specific claims in the submitted deliverables:

1. **DiffDock confidence direction:** minimum confidence selected as "best"; the convention (and the agent's own Rank 0 rows) is maximum. Corrected best poses: cid 111 −1.9753 → **−1.2722**; cid 120 −2.2020 → **−0.8961**. The claim that both priorities are confirmed by DiffDock does not survive the correction; the affinity-vs-DiffDock correlations must be recomputed (min-based r=0.196/ρ=0.322; corrected r=0.144/ρ=0.017).
2. **Caco-2 interpretation:** the direction is reversed in the prose (under log10 Papp, higher = more permeable), and Boltzmann values are compared against an ADMETlab domperidone number (−4.71 vs Boltzmann's own −5.28) — an invalid cross-provider comparison. The absorption comparisons as written do not support the stated conclusions.
3. **Affinity score units:** the "kcal/mol" attribution is unsupported; the scores are unitless model outputs presented with physical units they do not have.
4. **False qualification of cid 2:** even taken at face value, cid 2 (0.1217) is below the domperidone bar (0.1237); the "third fully-qualified candidate" claim contradicts its own stated criterion.
5. **Coverage overstatement:** "ADMETlab 400/400" — retained successes cover 180 library compounds; "7 of 8 top-8 have DiffDock" — the correct count is 5 of 8 (5/19/25/111/120).
6. **Interaction claims unsupported by the evidence:** closest-atom distances are reported as salt bridges and π-stacking without charge-state or ring-orientation verification, and the cid 120 C···Trp386 distance is reported inconsistently (4.95 Å in parts of the report vs 5.38 Å in the retained data).
7. **Material data-integrity caveat omitted:** 274/400 first exported Vina poses retain the source molecular formula (126 differ); 129 full InChIKeys differ; shortlist members 2/3/5/19/25 are affected (risperidone export C23H29FN4O2 vs source C23H27FN4O2). Vina-based conclusions were presented without this caveat, and no redocking-RMSD equivalence can be claimed from the chemically inconsistent export.

Minor consistency findings (residual pre-correction prose, ledger ambiguities) are not itemized here.

### 4.3 Evaluation scorecard

| Question | Finding |
|---|---|
| Executed scientific work? | Yes — predictions, properties, docking, subset poses retained and mapped |
| Required files delivered? | Yes, all three, correct format |
| Order follows stated primary model? | Yes (after excluding the risperidone-identical cid 1); some stale prose remains |
| Peripheral restriction supported as claimed? | **No — BCRP inhibitor probability misused as efflux evidence** |
| Absorption evidence? | Partly — recoverable after direction/provider corrections |
| DiffDock confirms binding? | No — pose-quality metric only; direction error |
| Poses fully qualified? | No — export discrepancies + incomplete preparation provenance |
| Disagreement with paper = failure? | No — independent workflow permitted; paper outcomes are computational references |

**Decision:** retain the shortlist and 111/120 as the agent's reported hypotheses; reject the combined peripheral-selection conclusion as written; no replacement list invented; no experimental-validation prerequisite imposed.

---

## 5. Comparison with the reference paper

### 5.1 Funnel

| Stage | Paper (metric → cutoff) | Agent (metric → cutoff) |
|---|---|---|
| Library | 400 SwissSimilarity hits | Same 400 records |
| Drug-likeness | Lipinski RO5 (MW<500, HBD≤5, HBA≤10, MlogP≤4.15) | not gated |
| Brain access | BOILED-Egg outside yolk + pkCSM/ADMETlab BBB → 226 | P(BCRP+) ≥ 0.1237 — endpoint misinterpreted; criterion unsupported |
| Primary affinity | Vina ≤ −11.8 (risperidone anchor) → 8 | platform affinity ≤ −0.938 (domperidone anchor) → 30 Tier-A |
| Docking | 226 docked (225 numeric) | all 400 docked (3,993 poses); Vina as cross-check |
| Interaction filter | Asp80(3.32) + Trp373(6.48) + 7-residue pocket → 4 | N···Asp114 / C···Trp386 pose distances (111: 3.30/3.72 Å, both in range; 120: 4.17/5.38 Å, weak) |
| MD | 100 ns; #128 most stable | out of scope |
| Safety/selectivity | hERG/CYP/Caco-2/off-target docking/SA | Caco-2 only + DiffDock pose check (direction error) |

### 5.2 Selection outcomes

| | Paper | Agent | Overlap |
|---|---|---|---|
| Top 8 | 17, 21, 24, 27, 128, 321, 360, 381 | 3, 5, 111, 2, 19, 25, 120, 10 | **0/8** |
| Final 2 | **128, 381** | **111, 120** | **0/2** |

Both agent priorities are BBB-permeable in the paper's own SwissADME table; both paper priorities are BBB-restricted — a genuine predictor disagreement, not an error on either side.

### 5.3 Per-compound scores (16 shortlist members)

| ID | Selected by | Paper Vina | Agent Vina | Agent affinity model |
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

Vina scores are kcal/mol; affinity-model scores are unitless and must not be subtracted from or equated to Vina values.

### 5.4 Cross-method agreement

| Paired outputs | n | Pearson r | Spearman ρ |
|---|---:|---:|---:|
| Paper Vina vs agent Vina | 225 | **0.667** | 0.652 |
| Agent Vina vs affinity model | 400 | 0.330 | 0.280 |
| Affinity model vs DiffDock (agent's min, wrong) | 20 | 0.196 | 0.322 |
| Affinity model vs DiffDock (corrected max) | 20 | 0.144 | 0.017 |

*Correlations as recorded in `metrics.json`, computed by the review's audit scripts over `compound_comparison.csv`; companion identity/coverage fields re-verified 2026-11-09.*

### 5.5 Coverage

| Item | Paper | Agent |
|---|---|---|
| Docked compounds | 226/400 (225 numeric) | 400/400 |
| Property predictions | 400 (S1) | 398 (195/290 failed) |
| External ADMET calls | web tools | 180 successes; all Tier-A recoverable |
| MD | 5 × 100 ns | none (scoped out) |
| Second engine | — | DiffDock 20/26 |

---

## 6. Revision requirements communicated to the executing agent

The following correction request was issued; originals are preserved as-is and the revision will be recorded additively:

> Fix these defects in the D2R deliverables (diagnose from the retained artifacts; preserve originals as *_v1):
> 1. The BCRP score is inhibitor probability, not efflux — the peripheral-restriction rationale and priority selection rest on this misinterpretation; redo with correctly interpreted evidence.
> 2. DiffDock best pose is max confidence, not min — redo that summary.
> 3. Caco-2: direction reversed; providers mixed in one comparison.
> 4. Affinity scores are unitless model outputs, not kcal/mol.
> 5. cid 2 fails the literal domperidone bar — fix the "third qualified" claim.
> 6. ADMETlab and DiffDock coverage claims are overstated.
> 7. Stale pre-correction text remains in report/assessment.
> 8. cid 120 pose distance inconsistent; interactions overstated from distances alone.
> 9. Flag the exported-pose formula/InChIKey drift and its impact on Vina conclusions.
> 10. Resolve the ambiguous property submissions and the timed-out P-gp attempt in the ledger.
> Ranking may change only as these corrections require. No invented values.

---

## 7. Review package contents

| Folder | Contents | Entry point |
|---|---|---|
| `tasks/` | Original task document (identical to the executed task) | `task_001_d2r_peripheral_candidate_prioritisation.md` |
| `benchmark/` | Published paper results, evaluation criteria and the agent results, in the repository benchmark format | `task_001_d2r_peripheral_candidate_prioritisation.md` |
| `results/task_001…/` | The agent's submitted result files, unchanged (11 files incl. `ranked_candidates.csv`, `assessment.json`, `report.md`) | `report.md` |
| `inputs/`, `config/`, `scripts/`, `tests/` | Original scientific inputs unchanged; environment configuration and scripts | `scripts/validate_environment.py` |

Package integrity: the task document matches the executed task byte-for-byte, and all eleven result files are hash-verified against the original agent submission.

## 8. Status

- Review complete and validated; agent originals preserved unchanged.
- The agent's revision round against §6 is pending; revised deliverables will be recorded alongside the preserved originals without altering them.
