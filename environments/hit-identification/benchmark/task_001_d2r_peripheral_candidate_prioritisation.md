**Task ID:** `task_001_d2r_peripheral_candidate_prioritisation`

**Task:** [D2R peripheral candidate prioritisation](../tasks/task_001_d2r_peripheral_candidate_prioritisation.md)

## Published Results

**Source:** [Kim S, Jo WH, Cha JO, Kim M-S, *Identification of novel peripherally restricted risperidone-like dopamine D2 receptor antagonists for prolactin-mediated neuroprotection through a multi-stage in silico screening*, PLOS ONE 21(8): e0355997 (2026)](https://doi.org/10.1371/journal.pone.0355997), Methods and Results; [full text](https://journals.plos.org/plosone/article?id=10.1371/journal.pone.0355997).

| Published metric | Reported value or outcome | Scope and interpretation |
| --- | --- | --- |
| Similarity screening | **400 risperidone analogs** from SwissSimilarity vs ZINC-20, ranked by similarity. | Top-ranked hits; no numeric similarity cutoff is published. |
| ADMET filter | Lipinski RO5 (MW<500, HBD≤5, HBA≤10, MlogP≤4.15) and BOILED-Egg position (WLOGP+TPSA; high GI absorption, outside yolk = BBB-impermeable) → **226 candidates**. | Library-wide gate. pkCSM (logBB, logPS, P-gp) and ADMETlab 3.0 (BBB probability, P-gp) were applied to shortlisted candidates, not to this gate. |
| Docking reference score | Risperidone (co-crystal ligand 8NU) Vina score **−11.8 kcal/mol**. | Reference anchor for hit selection, not a universal cutoff. |
| Docking hits | Strictly better than −11.8 → **8 hits** (17, 21, 24, 27, 128, 321, 360, 381); best #17 at **−12.4**. | Vina 1.2.7 into a SWISS-MODEL-repaired 6CM4 receptor; grid center (10, 5.9, −9.5), 30×30×30 Å; exhaustiveness 16. |
| Redocking validation | Heavy-atom RMSD **0.458 Å** for risperidone. | Text value; the Fig 3 caption states 0.48 Å. Original redocked coordinates are not deposited. |
| Interaction filter | Salt bridge to Asp80(3.32) plus hydrophobic-pocket engagement (Cys84, Thr85, Ser163, Phe164, Phe376, Trp373(6.48), Phe377) → **4 advanced** (27, 128, 360, 381). | Model numbering; Asp114/Trp386 in the full-length construct. Justified by mutagenesis (loss of these contacts → Ki > 10,000 nM). |
| MD stability | 100 ns GROMACS/CHARMM36m; receptor Cα RMSD 0.259 nm (risperidone) vs 0.265–0.382 nm (candidates); **#128 most stable ligand RMSD**. | Five systems, one trajectory each; no replicates. |
| Final priorities | **#128 (ZINC000019333157)** and **#381 (ZINC000019337359)**. | Complementary profiles: #128 best MD stability; #381 better predicted BBB restriction and hERG-10 μM probability. |

Published decision data are fully available (S1: 400 compounds; S2: 226 docking scores; S1 Dataset: RMSD curves); id 380 has no numerical S2 score.

## Evaluation Criteria

| Criterion | Comparison requirement | Acceptance boundary |
| --- | --- | --- |
| Brain-access evidence | Use an endpoint whose meaning and direction are verified; state the predictor for every label. | Peripheral-restriction labels are accepted only from correctly interpreted evidence; an inhibitor probability cannot support a substrate-efflux claim. |
| Affinity evidence | State the primary score, its provider and its units; anchor thresholds to same-run reference controls. | Platform model scores are unitless unless units are documented; Vina scores are kcal/mol; the two scales must not be mixed. |
| Docking comparability | Match engine, receptor preparation and grid definition before comparing scores with the paper. | Paper scores come from a homology-repaired receptor (not deposited) and a 30 Å box; differences in preparation must be reported with any comparison. |
| Pose and interaction evidence | Report geometric observations; verify charge state and ring orientation before naming interaction types. | Closest-atom distances alone do not establish salt bridges or π-stacking. |
| Reference-control use | Compare candidates with risperidone and domperidone within the same predictor and scale. | Cross-provider raw values are not comparable without reconciliation. |

## Agent Results

Executed on the Boltzmann platform; result files preserved unchanged in [`results/task_001_d2r_peripheral_candidate_prioritisation/`](../results/task_001_d2r_peripheral_candidate_prioritisation/report.md).

| Stage | Agent execution | Outcome |
| --- | --- | --- |
| Affinity prediction | Platform binding-affinity model on all 400 compounds + controls (unitless scores) | 400 + 2 control predictions; Tier-A bar = domperidone (−0.938) → **30 compounds** |
| Property prediction | Platform Property_Prediction (Caco-2, MW, TPSA, LogP, HBD/HBA) | 398/400 (ids 195/290 failed) |
| Brain access | Platform BBB/HIA labels constant → ADMETlab 3.0 `P(BCRP+)` with a domperidone-calibrated bar (0.1237) | Criterion unsupported: the endpoint is inhibitor probability, not substrate efflux |
| Docking | Platform Vina on all 400 (23 Å box at 9.925, 5.846, −9.582; exhaustiveness 16) | 3,993 poses; 400 best scores |
| Pose check | Closest-atom distances to Asp114/Trp386; DiffDock on 20 of 26 Tier-A compounds | 111: 3.30/3.72 Å (in range); 120: 4.17/5.38 Å (weak) |
| Shortlist | Affinity-ranked Tier-A, controls excluded | **3, 5, 111, 2, 19, 25, 120, 10** |
| Final priorities | Highest BCRP scores among top-ranked | **111 and 120** — selection basis invalid as interpreted |

**Overlap with the paper: shortlist 0/8, priorities 0/2.** Both agent priorities are BBB-permeable in the paper's SwissADME table; both paper priorities are BBB-restricted — a predictor disagreement between workflows.

**Scores for the paper's 8 shortlisted compounds**

| Compound ID | Paper Vina score (kcal/mol) | Agent Vina score (kcal/mol) | Agent affinity score (unitless) |
| ---: | ---: | ---: | ---: |
| 17 | −12.4 | −12.041 | −0.103 |
| 21 | −11.9 | −12.579 | −1.130 |
| 24 | −11.9 | −11.214 | −0.869 |
| 27 | −11.9 | −11.669 | +0.462 |
| 128 | −12.3 | −10.943 | +0.558 |
| 321 | −12.3 | −11.405 | −0.567 |
| 360 | −11.9 | −11.023 | +0.845 |
| 381 | −11.9 | −11.224 | +0.813 |

**Scores for the agent's 8 shortlisted compounds**

| Compound ID | Paper Vina score (kcal/mol) | Agent Vina score (kcal/mol) | Agent affinity score (unitless) |
| ---: | ---: | ---: | ---: |
| 3 | — | −11.600 | −2.369 |
| 5 | — | −11.266 | −2.362 |
| 111 | — | −11.043 | −2.214 |
| 2 | — | −12.425 | −2.191 |
| 19 | — | −12.155 | −2.166 |
| 25 | −11.5 | −11.612 | −2.157 |
| 120 | — | −9.841 | −2.122 |
| 10 | −11.8 | −11.561 | −2.090 |

"—" = no paper docking score exists: the paper docked only its 226 BBB-impermeable candidates, and these compounds were predicted BBB-permeable in its table, so they never entered its docking stage.

Cross-method agreement: paper Vina vs agent Vina r = 0.667 / ρ = 0.652 (n = 225 common compounds).

Full evaluation: [`FINAL_REPORT.md`](../FINAL_REPORT.md). Agent's own account: [`results/…/report.md`](../results/task_001_d2r_peripheral_candidate_prioritisation/report.md).
