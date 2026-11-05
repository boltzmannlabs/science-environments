# Task 004 — Discovery of allosteric PI5P4Kγ inhibitors by similarity/bioisostere screening, docking, MD and MM-PBSA

## Description

Identify novel allosteric inhibitors of phosphatidylinositol-5-phosphate 4-kinase type II gamma (PI5P4K2C) by similarity and bioisostere screening around the reference allosteric inhibitor DVF, docking at the allosteric pocket of PDB 7QPN, and 250 ns MD + MM-PBSA validation.

## Target

**Name:** PI5P4Kγ (PI5P4K2C), allosteric pocket
**Protein:** PI5P4K2C (UniProt Q8TBX8, derived)
**Disease:** Cancer (glioblastoma, leukemia, breast, soft-tissue sarcoma) and metabolic disorders
**Objective:** Allosteric-pocket screen for PI5P4Kγ inhibitors beating the same-engine DVF redock with MM-PBSA below −68.44 kJ/mol (derived)
**Binding Region:** DVF-bound allosteric pocket of 7QPN (consensus of chains A and B — derived)
**Data:** All docking scores, interactions, ADME and MM-PBSA tables in article + Supplementary Data (datasets "available from the supplementary data")
**PDB:** 7QPN (DVF-bound allosteric co-crystal; consensus pocket of chains A and B — derived)
**Structure and Context:** 7QPN DVF-bound allosteric co-crystal; consensus pocket of chains A and B (derived)
**Reference Inputs:** DVF reference ligand (7QPN); SwissSimilarity cascade around DVF (ChEMBL actives + ZINC lead-like; 800 retrieved → 0.75 similarity → 143 ChEMBL + 115 ZINC) + 9 STITCH + 2 SwissBioisostere ≈269 → 133 ChEMBL + 84 ZINC after SwissADME

## Design Constraints

- **Workflow:** SwissSimilarity around DVF (ChEMBL actives + ZINC lead-like; 800 retrieved) → similarity filter (threshold 0.75) → 143 ChEMBL + 115 ZINC; + 9 STITCH (Tanimoto 0.53–0.57) + 2 SwissBioisostere ≈ 269 (derived total) → SwissADME drug-likeness (133 ChEMBL + 84 ZINC qualify) → PyRx/Vina screening at the allosteric site → AutoDock 4.2 re-docking of best molecules → Hits I–XI → 250 ns MD (GROMACS 5.1.4, AMBER ff99SB, SPC) → MM-PBSA + PCA + FEL
- **Allosteric-site selectivity is the central design constraint** (ATP-site inhibitors are cross-reactive; allosteric pocket spans Asp161, Met162, Ser164, Asn165, Leu166, Tyr169, Leu182, Pro183, Phe185, Phe272, Leu273, Leu276, Ile278, Tyr281, Leu330, Ile331, Asp332, Leu334, Thr335)
- **Redocking validation:** DVF RMSD 0.45 Å (AutoDock 4.2) / 1.07 Å (PyRx)
- **MD as secondary validation of hits**
- **No QSAR, no DFT, no ML in hit-finding; no wet lab** (the paper's CarcinoPred-EL carcinogenicity web tool — ensemble RF/SVM/XGBoost — is out of scope; use `Property_Prediction` for the toxicity panel)
- **Query structure:** DVF is taken from the 7QPN co-crystal ligand

## Computational Tool Capabilities

Workflow stages and the capabilities each requires, with the evidence every stage must produce. Record unavailable capabilities and leave their required evidence unresolved.

| Stage | Capability | Expected Evidence |
|---|---|---|
| 1. Validate inputs and baseline | Retrieve/prepare the PDB structure(s) and public libraries; reproduce the paper's redock or reference baseline where stated. | Prepared structure and library files with provenance; redock RMSD or reference score. |
| 2. Hit generation | Allosteric-pocket detection + pharmacophore screen (`pharmacophoreHypothesis`, `Pharmacophore_Screening`) | Hypothesis/features, ranked hit lists, filter counts. |
| 3. Docking | `Vina_basic_docking` at the paper-verbatim grid/box; `Diffdock` second-engine on finalists. | Score tables with grid parameters; second-engine poses. |
| 4. ADMET / drug-likeness | `Property_Prediction` (SwissADME-class). | ADMET rows covering every pass-bar filter. |
| 5. MD validation (secondary) | `MDS_openMM`; `Binding_affinity_Prediction` corroboration. | Trajectory summaries; affinity ranking vs reference. |
| 6. Select and report | Apply the pass bar, rank hits, write the Expected Output files. | All expected files incl. `metrics.json`; exclusions and limitations noted. |

**Boltzmann platform tools:**
| Tool | Role | Key Arguments |
|------|------|---------------|
| `Similarity_Screening` | DVF-analog retrieval (ChEMBL/ZINC-like) | query + library |
| `pharmacophoreHypothesis` | Optional allosteric-pocket interaction model (the paper builds no pharmacophore) | `pdb_file`, site |
| `Vina_basic_docking` | Dock at allosteric site (7QPN; paper grid centered at X=63.470, Y=53.110, Z=47.470 Å) | `pdb_file`, `center_x/y/z`, `exhaustivness`, `smiles` |
| `Diffdock` | Second-engine re-docking | `processed_pdb`, `input_csv` |
| `Property_Prediction` | SwissADME-equivalent drug-likeness/ADMET | `smiles`, `global_models` |
| `MDS_openMM` | 250 ns MD of hit complexes | topology, `duration_ns` |
| `Binding_affinity_Prediction` | MM-PBSA-style ranking; PI5P4K2C (UniProt Q9HB55, derived) | `smiles`, `tar_seq`, `mode` |

**Other standard tools:** AutoDock 4.2 / PyRx (paper engines), GROMACS + g_mmpbsa, SwissSimilarity / SwissBioisostere / STITCH, SwissADME, I-TASSER.

**Paper tools (verbatim):** SwissSimilarity, SwissBioisostere, STITCH, SwissADME, PyRx 0.8 (UFF, conjugate gradients), AutoDock 4.2, I-TASSER, GROMACS 5.1.4 (AMBER ff99SB, SPC, Antechamber + ACPYPE), g_mmpbsa, Discovery Studio Visualizer, UCSF Chimera, Molinspiration (bioactivity scoring — out of scope).

## Evaluation Metrics

| Metric | Published value |
|---|---|
| Reference docking | DVF −9.26 kcal/mol (AutoDock 4.2) / −10.4 (PyRx) |
| Hit docking range | −7.31 to −11.1 kcal/mol (AutoDock 4.2); −7.06 to −10.0 (PyRx) |
| Redock RMSD | 0.45 Å (AutoDock 4.2) vs co-crystal pose |
| MM-PBSA ΔG | Hits II −103.64, III −163.67, IV −150.65 kJ/mol vs DVF −68.44 ± 1.80 |
| MD | 250 ns; complexed protein RMSD <0.4 nm, ligand RMSD <0.15 nm; PCA/FEL stable |
| Hits | 4 pyrrole-pyrimidine-core hits (Hit I–IV; Table 1 lists IUPAC names only — mapping CHEMBL2418346/47 to specific hits is derived, not stated in the paper) |

## Expected Output

**Format:** `small_molecule_vs_bundle`
**Directory:** `results/task_004/<run>/`

| File | Content |
|---|---|
| `screening_ranking.csv` | Similarity + drug-likeness ranked analogs |
| `docking_scores.csv` | Allosteric-site scores vs DVF reference |
| `admet_panel.csv` | SwissADME-equivalent profiles |
| `md_energies.csv` | MM-PBSA components per hit |
| `metrics.json` | Best hit score, ΔG, redock RMSD |

**Pass bar:** ≥1 hit docking better than the same-engine DVF redock score (paper reference: −9.26 AutoDock 4.2 / −10.4 PyRx kcal/mol) with MM-PBSA ΔG below −68.44 kJ/mol and stable 250 ns MD.

## Constraints

- **Time Limit:** 240 minutes of agent working time (long-running platform jobs may complete asynchronously beyond it)
- **Reference Policy:** use the tools and workflow above; do NOT look up the source publication to copy its hit lists or scores
- **Knowledge Cutoff:** not applicable — retrospective paper-anchored task; every required parameter is stated in this document
- **Evaluation Integrity:** freeze candidate selection, scores, and rankings before comparing them against the paper's published reference values

## Important Instructions

- Solve this task using the provided tools and your own reasoning.
- Do NOT search for, reference, or reproduce the source paper's specific hits, scores, or tables — the run is evaluated on completing the workflow and meeting the pass bar, not on matching published values.

## Publication

[Sci Rep (2025)](https://doi.org/10.1038/s41598-025-07480-x). [PMC12485083](https://pmc.ncbi.nlm.nih.gov/articles/PMC12485083/)
