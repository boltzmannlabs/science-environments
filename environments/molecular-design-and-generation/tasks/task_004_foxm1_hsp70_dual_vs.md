# Task 004 — Pharmacophore and docking virtual screening for dual FoxM1/Hsp70 inhibitors (cancer)

## Description

Identify dual inhibitors of the FoxM1 transcription factor and Hsp70 chaperone — both overexpressed across cancers — by building a ZINC analog library around the FoxM1 inhibitor FDI-6, screening it through two structure-based pharmacophore models and dual-target AutoDock screening, ADMET profiling, and MD/MM-PBSA validation of the best dual ligand.

## Target

**Name:** Forkhead box protein M1 (FoxM1, DBD) + Heat shock protein 70 (Hsp70) — dual target
**Protein:** FOXM1 (UniProt Q08050, derived) + Hsp70/HSPA1A (UniProt P0DMB8, derived)
**Disease:** Cancer (FoxM1/Hsp70 overexpressing tumors)
**Objective:** Identify dual FoxM1/Hsp70 binders that out-dock FDI-6 and VER-155008 with acceptable ADMET (derived)
**Binding Region:** FoxM1 DNA-binding domain (grid at His287) and Hsp70 nucleotide-binding site (grid at Arg272)
**Data:** Compound ZINC IDs, pharmacophore models, docking energies and MD tables in article (open access; compounds retrievable from ZINC)
**PDB:** FoxM1 3G73 (DNA-binding domain; grid at His287; RCSB metadata: 2.21 Å, protein–DNA complex, no co-crystal ligand), Hsp70 4IO8 (grid at Arg272; co-crystal ligand VER-155008, RCSB ligand code 3FD; docking validated at RMSD <2 Å; RCSB metadata: 2.58 Å)
**Structure and Context:** 3G73 is a protein–DNA complex with no co-crystal ligand (grid anchored at His287); 4IO8 carries VER-155008 (RCSB 3FD)
**Reference Inputs:** FDI-6 (FoxM1 reference, ZINC ID in-doc) and VER-155008 (Hsp70 reference, ZINC ID in-doc); structures 3G73 (protein–DNA) and 4IO8

## Design Constraints

- **Workflow:** ZINC similarity search on FDI-6 (≥80% similarity + Lipinski Ro5) → 850 compounds → two Pharmit structure-based pharmacophore models (FDI-6–FoxM1; VER-155008–Hsp70) → pharmacophore screening (RMSD <2 Å; energy <−7 kcal/mol FoxM1 / <−6 Hsp70) → 520 (FoxM1) + 120 (Hsp70) candidates (the conclusion section states 120/25 — paper-internal conflict) → AutoDock 4.2 dual-target docking (70×70×70 grid, 0.345 Å spacing, 100 runs) → 5 dual hits → QikProp/DataWarrior/Osiris ADMET → 10 ns MD + MM-PBSA triage → 100 ns MD of best ligand on both targets
- **Dual-activity constraint:** ligand must dock into both FoxM1 and Hsp70 sites with energies beating references FDI-6 (−2.7 kcal/mol) and VER-155008 (−1.77 kcal/mol)
- **MD as secondary validation of the best dual hit**
- **No QSAR, no DFT, no ML, no wet lab**

## Computational Tool Capabilities

Workflow stages and the capabilities each requires, with the evidence every stage must produce. Record unavailable capabilities and leave their required evidence unresolved.

| Stage | Capability | Expected Evidence |
|---|---|---|
| 1. Validate inputs and baseline | Retrieve/prepare the PDB structure(s) and public libraries; reproduce the paper's redock or reference baseline where stated. | Prepared structure and library files with provenance; redock RMSD or reference score. |
| 2. Hit generation | Dual-target pharmacophore + similarity screen (`pharmacophoreHypothesis`, `Pharmacophore_Screening`, `Similarity_Screening`) | Hypothesis/features, ranked hit lists, filter counts. |
| 3. Docking | `Vina_basic_docking` at the paper-verbatim grid/box; `Diffdock` second-engine on finalists. | Score tables with grid parameters; second-engine poses. |
| 4. ADMET / drug-likeness | `Property_Prediction` (SwissADME-class). | ADMET rows covering every pass-bar filter. |
| 5. MD validation (secondary) | `MDS_openMM`; `Binding_affinity_Prediction` corroboration. | Trajectory summaries; affinity ranking vs reference. |
| 6. Select and report | Apply the pass bar, rank hits, write the Expected Output files. | All expected files incl. `metrics.json`; exclusions and limitations noted. |

**Boltzmann platform tools:**
| Tool | Role | Key Arguments |
|------|------|---------------|
| `Similarity_Screening` | FDI-6-analog ZINC retrieval | query + library |
| `pharmacophoreHypothesis` | FoxM1 + Hsp70 models | `pdb_file`, features |
| `Pharmacophore_Screening` | Screen analog library | hypothesis + library |
| `Vina_basic_docking` | Dual-target docking (3G73, 4IO8) | `pdb_file`, `center_x/y/z`, `exhaustivness`, `smiles` |
| `Diffdock` | Second-engine | `processed_pdb`, `input_csv` |
| `Property_Prediction` | QikProp-equivalent ADMET | `smiles`, `global_models` |
| `MDS_openMM` | 100 ns MD + MM-PBSA | topology, `duration_ns` |
| `Binding_affinity_Prediction` | FoxM1/Hsp70 affinity ranking | `smiles`, `tar_seq`, `mode` |

**Other standard tools:** Pharmit, AutoDock 4.2 + AutoDock Tools, GROMACS + MM-PBSA, QikProp, DataWarrior, Osiris Property Explorer.

**Paper tools (verbatim):** ZINC database, Pharmit web server, AutoDock 4.2 / AutoDock Tools (Kollman/Gasteiger charges), GROMACS 2019.3 (AMBER force field, TIP3P, PME), ACPYPE, PROPKA 3.1, MM-PBSA, QikProp (methods say v.3.0; Table 1 footnote says v.3.2 — paper-internal conflict), DataWarrior, Osiris, Marvin Sketch v5.7, Discovery Studio Visualizer 4.0.2.

## Evaluation Metrics

| Metric | Published value |
|---|---|
| Reference docking | FDI-6 −2.7 kcal/mol (FoxM1); VER-155008 −1.77 kcal/mol (Hsp70) |
| Final dual hits | ZINC8448537, ZINC1152745, ZINC199847048, ZINC199676474, ZINC6110690 |
| Best dual ligand | ZINC1152745 (−4.27 kcal/mol FoxM1; −3.291 kcal/mol Hsp70; stable on both targets) |
| ADMET | QikProp descriptors + DataWarrior toxicity risks + Osiris drug-likeness |
| MD/MM-PBSA | 100 ns stable on both proteins; ZINC1152745 ΔG_bind −79.406 (FoxM1) / −79.103 (Hsp70) kJ/mol vs FDI-6 −65.805 / VER-155008 −28.331 (units not stated in the paper; kJ/mol inferred from the g_mmpbsa/GROMACS analysis — derived) |

## Expected Output

**Format:** `small_molecule_vs_bundle`
**Directory:** `results/task_004/<run>/`

| File | Content |
|---|---|
| `analog_library.csv` | FDI-6-similar ZINC compounds (≥80%, Ro5-passing) |
| `pharmacophore_models.json` | FoxM1 + Hsp70 hypotheses |
| `docking_scores.csv` | Dual-target energies vs FDI-6/VER-155008 |
| `admet_panel.csv` | QikProp/DataWarrior-equivalent profiles |
| `metrics.json` | Best dual ligand + energies |

**Pass bar:** ≥1 compound docking better than FDI-6 on FoxM1 AND VER-155008 on Hsp70 with acceptable ADMET.

## Constraints

- **Time Limit:** 240 minutes of agent working time (long-running platform jobs may complete asynchronously beyond it)
- **Reference Policy:** use the tools and workflow above; do NOT look up the source publication to copy its hit lists or scores
- **Knowledge Cutoff:** not applicable — retrospective paper-anchored task; every required parameter is stated in this document
- **Evaluation Integrity:** freeze candidate selection, scores, and rankings before comparing them against the paper's published reference values

## Important Instructions

- Solve this task using the provided tools and your own reasoning.
- Do NOT search for, reference, or reproduce the source paper's specific hits, scores, or tables — the run is evaluated on completing the workflow and meeting the pass bar, not on matching published values.

## Publication

[Res Pharm Sci (2023)](https://doi.org/10.4103/1735-5362.359431). [PMC9872178](https://pmc.ncbi.nlm.nih.gov/articles/PMC9872178/)
