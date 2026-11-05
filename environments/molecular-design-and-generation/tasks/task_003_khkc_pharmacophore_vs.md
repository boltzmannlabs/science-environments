# Task 003 — Pharmacophore-based virtual screening of the NCI library against ketohexokinase-C

## Description

Screen the NCI 460,000-compound library against ketohexokinase-C (KHK-C) — the fructose-metabolism target for NAFLD/NASH — using Phase pharmacophores, multistage Glide docking, MM-GBSA, ADMET, and MD, benchmarked against phase-II clinical compounds.

## Target

**Name:** Ketohexokinase-C (KHK-C)
**Protein:** Ketohexokinase (UniProt P50053, derived)
**Disease:** Fructose metabolic disorders (NASH/NAFLD, insulin resistance)
**Objective:** Discover KHK-C inhibitors beating the PF-06835919 −7.76 kcal/mol Glide XP reference with acceptable ADMET (derived)
**Binding Region:** Catalytic pocket defined by the PF-06835919 co-crystal in 6W0Z (reference score −7.768 kcal/mol)
**Data:** All hits/scores in article + Supplementary Material
**PDB:** 6W0Z (PF-06835919, 2.30 Å), 8UG3 (LY-3522348), 3NC9 (indazole), 8OME (KHK-A isoform comparison)
**Structure and Context:** 6W0Z (PF-06835919) is the pharmacophore/docking reference; 8UG3/3NC9 comparisons; 8OME the KHK-A isoform comparison
**Reference Inputs:** NCI library (460,000 compounds); reference inhibitors PF-06835919 (6W0Z) and LY-3522348

## Design Constraints

- **Workflow:** NCI library (460,000) → Phase structure-based pharmacophore from PF-06835919 in 6W0Z (5 features: 2× hydrophobic, ring-aromatic, HBA, anionic; library screened at 50 conformers/ligand ranked by PhaseScreenScore) → top 9,000 → Glide VSW multistage docking (HTVS → 700 → SP → 37 → XP → 10; redock validation RMSD 0.245 Å) → MM-GBSA free energies (Prime, VSGB 2.0, OPLS4) → QikProp ADMET → 5 final hits (1, 2, 4–6) → 100 ns MD (Desmond) + AutoDock 4.2 cross-validation
- **Benchmarks:** clinical compounds PF-06835919 (−7.768 kcal/mol; MM-GBSA −56.71 ± 0.30), LY-3522348 (−6.96 ± 0.012; −45.15 ± 0.86), BI-9787 (−6.540; −28.98); the abstract's "LY-3522348 (−6.54)" actually matches BI-9787's Table-1 score (abstract misattribution)
- **MD as secondary validation of top 5 hits**
- **No QSAR, no DFT, no ML, no wet lab**

## Computational Tool Capabilities

Workflow stages and the capabilities each requires, with the evidence every stage must produce. Record unavailable capabilities and leave their required evidence unresolved.

| Stage | Capability | Expected Evidence |
|---|---|---|
| 1. Validate inputs and baseline | Retrieve/prepare the PDB structure(s) and public libraries; reproduce the paper's redock or reference baseline where stated. | Prepared structure and library files with provenance; redock RMSD or reference score. |
| 2. Hit generation | Structure-based pharmacophore screen (`pharmacophoreHypothesis`, `Pharmacophore_Screening`) | Hypothesis/features, ranked hit lists, filter counts. |
| 3. Docking | `Vina_basic_docking` at the paper-verbatim grid/box; `Diffdock` second-engine on finalists. | Score tables with grid parameters; second-engine poses. |
| 4. ADMET / drug-likeness | `Property_Prediction` (SwissADME-class). | ADMET rows covering every pass-bar filter. |
| 5. MD validation (secondary) | `MDS_openMM`; `Binding_affinity_Prediction` corroboration. | Trajectory summaries; affinity ranking vs reference. |
| 6. Select and report | Apply the pass bar, rank hits, write the Expected Output files. | All expected files incl. `metrics.json`; exclusions and limitations noted. |

**Boltzmann platform tools:**
| Tool | Role | Key Arguments |
|------|------|---------------|
| `pharmacophoreHypothesis` | Phase-equivalent model from 6W0Z/PF-06835919 | `pdb_file`, features |
| `Pharmacophore_Screening` | Screen NCI 460k | hypothesis + library |
| `Vina_basic_docking` | Multistage docking equivalent | `pdb_file`, `center_x/y/z`, `exhaustivness`, `smiles` |
| `Diffdock` | Second-engine | `processed_pdb`, `input_csv` |
| `Property_Prediction` | QikProp ADMET | `smiles`, `global_models` |
| `MDS_openMM` | MD of top 5 | topology, `duration_ns` |
| `Binding_affinity_Prediction` | KHK (UniProt P50053, derived) + MM-GBSA ranking | `smiles`, `tar_seq`, `mode` |

**Other standard tools:** Schrödinger Phase/Glide/Prime/QikProp/Desmond, AutoDock 4.2.

**Paper tools (verbatim):** Schrödinger Suite 2023-1 (Protein Preparation Wizard, Epik, Prime, Phase, LigPrep, Glide VSW, QikProp, Desmond), NCI open database (cactus.nci.nih.gov), AutoDock 4.2 (cross-validation), RCSB PDB.

## Evaluation Metrics

| Metric | Published value |
|---|---|
| Top-10 docking scores | −7.79 to −9.10 kcal/mol (all beat PF-06835919 at −7.76) |
| MM-GBSA ΔG | −57.06 to −70.69 kcal/mol (PF-06835919 −56.71; LY-3522348 −45.15) |
| Hypothesis validation (30 actives + 15 decoys) | ROC 0.81; AUC 0.62; RIE 1.50; BEDROC 1.000/1.000/0.977 (α = 160.9/20.0/8.0); EF 7.5 (50% of actives); top-50 hit rate 52% |
| VS-workflow enrichment (top-10 hits + 18 inactives) | ROC 1.0; BEDROC 1.0; RIE 4.54; accumulation-curve AUC 0.89; EF 4.6 |
| AutoDock 4.2 cross-check | Hits −7.4 to −8.5 vs reference −7.3 kcal/mol (hit 4 −7.0, below the reference) |
| Final hits | Molecules 1, 2, 4–6 (MD-validated; e.g., hit 1 PubChem 6622312) |

## Expected Output

**Format:** `small_molecule_vs_bundle`
**Directory:** `results/task_003/<run>/`

| File | Content |
|---|---|
| `pharmacophore_model.json` | Hypothesis from co-crystals |
| `screening_ranking.csv` | NCI cascade ranking |
| `docking_scores.csv` | Scores + ΔG vs benchmarks |
| `admet_panel.csv` | QikProp profiles |
| `metrics.json` | Best hit score |

**Pass bar:** ≥1 compound with a primary-engine docking score < −7.76 kcal/mol (Glide XP reference value for PF-06835919) and acceptable ADMET.

## Constraints

- **Time Limit:** 240 minutes of agent working time (long-running platform jobs may complete asynchronously beyond it)
- **Reference Policy:** use the tools and workflow above; do NOT look up the source publication to copy its hit lists or scores
- **Knowledge Cutoff:** not applicable — retrospective paper-anchored task; every required parameter is stated in this document
- **Evaluation Integrity:** freeze candidate selection, scores, and rankings before comparing them against the paper's published reference values

## Important Instructions

- Solve this task using the provided tools and your own reasoning.
- Do NOT search for, reference, or reproduce the source paper's specific hits, scores, or tables — the run is evaluated on completing the workflow and meeting the pass bar, not on matching published values.

## Publication

[Front Pharmacol (2025)](https://doi.org/10.3389/fphar.2025.1531512). [PMC12009819](https://pmc.ncbi.nlm.nih.gov/articles/PMC12009819/)
