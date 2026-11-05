# Task 002 — Pharmacophore-aided virtual screening for TrkB agonists against CDKL5-deficiency disorders

## Description

Identify agonist candidates of the TrkB (tropomyosin receptor kinase B) ligand-binding domain for CDKL5-deficiency disorder (CDD) by Pharmit pharmacophore screening around the reference agonist 7,8-dihydroxyflavone (7,8-DHF), AutoDock Vina docking, SwissADME ADMET profiling, and MD validation of the top two hits.

## Target

**Name:** TrkB (gene NTRK2, derived), ligand-binding domain (LBD)
**Protein:** NTRK2/TrkB (UniProt Q16640, derived)
**Disease:** CDKL5-deficiency disorder (rare neurodevelopmental disorder; early epilepsy)
**Objective:** Agonist-biased TrkB pharmacophore VS for hits beating 7,8-DHF (−7.1 kcal/mol) with high GI absorption (derived)
**Binding Region:** TrkB ligand-binding domain captured in 1WWB; reference agonist 7,8-DHF
**Data:** All pharmacophore features, hit/score tables, ADMET table, and interaction details within the article (no supplementary material; no "on request" language)
**PDB:** 1WWB (TrkB LBD, Ultsch et al.; resolution not stated in the paper)
**Structure and Context:** 1WWB TrkB LBD crystal (Ultsch et al.); resolution not stated in the paper
**Reference Inputs:** 7,8-DHF reference agonist (PubChem CID 1880) built into 1WWB (Discovery Studio 2021 + Chimera); Pharmit-screenable library behind the resulting pharmacophore

## Design Constraints

- **Workflow:** Blind-dock reference agonist 7,8-DHF (PubChem 1880) into 1WWB (Discovery Studio 2021 + Chimera) → Pharmit pharmacophore from the 7,8-DHF–TrkB interaction (text: 2 H-bond donors + 2 H-bond receptors [sic] + 3 aromatic features; Table 1 lists 1 donor + 3 acceptors — paper-internal conflict) → multi-database screening (10 databases configured: PubChem, MCULE, ZINC, MolPort, CHEMBL30, ChemDiv, ChemSpace, MCULE-ULTIMATE, NCI Open Chemical Repository, LabNetwork; results cite 5 databases — paper-internal conflict) + drug-likeness filters (Lipinski/Veber/Ghose/Egan/Muegge: MW ≤500, rotatable bonds ≤10, logP ≤5, TPSA ≤140 Å, HBA ≤10, HBD ≤5, aromatics ≤2) → 691 unique ligands → PyRx (OpenBabel) 3D conversion → AutoDock Vina 1.2 docking → 6 hits (−9.6 to −8.8 kcal/mol, all beating 7,8-DHF at −7.1) → SwissADME ADMET → 1 ns MD (NAMD/VMD, CHARMM36 via CHARMM-GUI, 310 K, 1 atm, PBC) of the top 2 hits (91637738, 91641310)
- **Agonist-discovery constraint:** hits must out-dock the reference agonist 7,8-DHF
- **MD as secondary validation of the top 2 hits** (published runs are 1 ns; platform MD may extend)
- **No MM-GBSA stage in the paper** — ranking anchors are Vina docking scores only; platform `Binding_affinity_Prediction` may be run as an extension with no published values to compare
- **No QSAR, no DFT, no ML, no wet lab**

## Computational Tool Capabilities

Workflow stages and the capabilities each requires, with the evidence every stage must produce. Record unavailable capabilities and leave their required evidence unresolved.

| Stage | Capability | Expected Evidence |
|---|---|---|
| 1. Validate inputs and baseline | Retrieve/prepare the PDB structure(s) and public libraries; reproduce the paper's redock or reference baseline where stated. | Prepared structure and library files with provenance; redock RMSD or reference score. |
| 2. Hit generation | Agonist pharmacophore build + screen (`pharmacophoreHypothesis`, `Pharmacophore_Screening`) | Hypothesis/features, ranked hit lists, filter counts. |
| 3. Docking | `Vina_basic_docking` at the paper-verbatim grid/box; `Diffdock` second-engine on finalists. | Score tables with grid parameters; second-engine poses. |
| 4. ADMET / drug-likeness | `Property_Prediction` (SwissADME-class). | ADMET rows covering every pass-bar filter. |
| 5. MD validation (secondary) | `MDS_openMM`; `Binding_affinity_Prediction` corroboration. | Trajectory summaries; affinity ranking vs reference. |
| 6. Select and report | Apply the pass bar, rank hits, write the Expected Output files. | All expected files incl. `metrics.json`; exclusions and limitations noted. |

**Boltzmann platform tools:**
| Tool | Role | Key Arguments |
|------|------|---------------|
| `pharmacophoreHypothesis` | Pharmit-equivalent 7,8-DHF-interaction model | `pdb_file`, features |
| `Pharmacophore_Screening` | Multi-database screen | hypothesis + library |
| `Vina_basic_docking` | Dock into TrkB LBD (1WWB) | `pdb_file`, `center_x/y/z`, `exhaustivness`, `smiles` |
| `Diffdock` | Second-engine | `processed_pdb`, `input_csv` |
| `Property_Prediction` | SwissADME-equivalent ADMET | `smiles`, `global_models` |
| `MDS_openMM` | MD of top hits | topology, `duration_ns` |
| `Binding_affinity_Prediction` | Ranking extension; NTRK2 (UniProt Q16620, derived) | `smiles`, `tar_seq`, `mode` |

**Other standard tools:** Pharmit, AutoDock Vina, NAMD + VMD, SwissADME, Bio3D.

**Paper tools (verbatim):** Discovery Studio 2021 (incl. 2021 Client), Chimera (version 33.02.1242), Pharmit server (pharmit.csb.pitt.edu), PyRx (OpenBabel module), AutoDock Vina (version 1.2), SWISS ADME web tool (swissadme.ch), NAMD, VMD, CHARMM36 force field via CHARMM-GUI, Bio3D on Galaxy Europe, RCSB PDB.

## Evaluation Metrics

| Metric | Published value |
|---|---|
| Docking (Table 2) | 6 hits −9.6 to −8.8 kcal/mol vs 7,8-DHF −7.1; best: 91637738 −9.6, 91641310 −9.3, 91639858 −9.3, 91639334 −9.2, 91640550 −9.0, 91639725 −8.8 |
| Library | 691 unique ligands after drug-likeness filters |
| ADMET (Table 4) | All 6 hits: High GI absorption, BBB non-permeant, ESOL/Ali soluble (Silicos-IT poorly soluble); consensus LogP 1.95–2.41; TPSA 107.8–127.77 Å; SA 3.88–4.12; 7,8-DHF inhibits CYP1A2/2D6/3A4 vs hits inhibiting ≤1 CYP |
| Interactions (Table 3) | Hits: H-bonds Asp370 (2.86 Å), Leu361 (top-2: 2.25/2.2 Å; hits 3–6: 2.18–2.24 Å); 7,8-DHF: Ala363 (2.68 Å), Thr306 (2.19 Å) |
| MD (1 ns NAMD) | Ligand RMSD comp 1 0.2–0.8 Å / comp 2 0.6–1.8 Å (backbone drifts to ~5.3 Å in both); PCA PC1–3: 69.5% (comp 1) / 79.3% (comp 2); H-bonds 6 (comp 1) / 10 (comp 2) |
| Paper-internal conflicts | P-gp text self-contradicts (calls both compound groups "potential substrates"; Table 4 marks only 1/3/6 as substrates); compound-1 H-bond text cites "Figure 9", which is compound 2's graph; Table 1 also duplicates one acceptor row |

## Expected Output

**Format:** `small_molecule_vs_bundle`
**Directory:** `results/task_002/<run>/`

| File | Content |
|---|---|
| `pharmacophore_model.json` | 7,8-DHF-interaction hypothesis + features |
| `screening_ranking.csv` | Filtered 691-compound library |
| `docking_scores.csv` | Vina scores vs 7,8-DHF reference |
| `admet_panel.csv` | SwissADME-equivalent profiles |
| `md_report.md` | RMSD/PCA/H-bond summary of the top-2 complexes |
| `metrics.json` | Best hit score + ADMET summary |

**Pass bar:** ≥1 candidate docking better than 7,8-DHF (−7.1 kcal/mol; published hits reach −9.6) with High GI absorption and an acceptable ADMET profile.

## Constraints

- **Time Limit:** 240 minutes of agent working time (long-running platform jobs may complete asynchronously beyond it)
- **Reference Policy:** use the tools and workflow above; do NOT look up the source publication to copy its hit lists or scores
- **Knowledge Cutoff:** not applicable — retrospective paper-anchored task; every required parameter is stated in this document
- **Evaluation Integrity:** freeze candidate selection, scores, and rankings before comparing them against the paper's published reference values

## Important Instructions

- Solve this task using the provided tools and your own reasoning.
- Do NOT search for, reference, or reproduce the source paper's specific hits, scores, or tables — the run is evaluated on completing the workflow and meeting the pass bar, not on matching published values.

## Publication

[Bioinformatics and Biology Insights (2023)](https://doi.org/10.1177/11779322231158254). [PMC9989394](https://pmc.ncbi.nlm.nih.gov/articles/PMC9989394/)
