# Task 002 — Discovery of ROCK2 inhibitors through pharmacophore-based screening of the ZINC database

## Description

Build a Pharmit pharmacophore from the co-crystal ligand of ROCK2 (7P6N), screen the ZINC database through Lipinski and pose-RMSD filters, dock hits with Glide SP or platform Vina/Diffdock, profile ADMET/toxicity, and validate the two top hits by 150 ns MD with trajectory analyses.

## Target

**Name:** Rho-associated coiled-coil kinase 2 (ROCK2)
**Protein:** ROCK2 (UniProt O75116 human, derived)
**Disease:** Cancer, cardiovascular, neurological
**Objective:** Discover ROCK2 inhibitors meeting the −9.89 kcal/mol Glide SP-referenced bar (≥2 hits) with acceptable ADMET and stable 150 ns MD (derived)
**Binding Region:** ATP site of 7P6N defined by co-crystal ligand 5YS; paper grid at X,Y,Z = 83.45, 40.13, 18.05
**Top hits:** ZINC287819616 (−9.939 kcal/mol), ZINC513417492 (−9.894 kcal/mol)
**Data:** "All data has been incorporated within the manuscript" (all tables/figures in article; no supplement)
**PDB:** 7P6N (co-crystal ligand 5YS; resolution not stated in the paper)
**Structure and Context:** 7P6N co-crystal (5YS) supplies the pharmacophore features and the docking grid
**Reference Inputs:** 7P6N co-crystal ligand 5YS (pharmacophore features + docking grid); ZINC database (13,127,550 compounds, Lipinski pre-filter applied by the authors)

## Design Constraints

- **Workflow:** Pharmit pharmacophore from co-crystal ligand 5YS of 7P6N (6 features) → Lipinski filter (MW<500, HBD<5, HBA<10, logP<5) on ZINC (13,127,550 molecules) → pose RMSD <0.5 Å → 4809 hits → ligand prep (LigPrep, OPLS_2005) → Glide SP docking (grid at X,Y,Z = 83.45, 40.13, 18.05) → top-10 ranked → ADMET (OSIRIS + admetSAR) → 150 ns MD (GROMACS, CHARMM36, TIP3P, 310 K) of both hits → RMSD/RMSF/Rg/SASA/H-bond/PCA analysis
- **MD as secondary validation of the 2 top hits** (paper methods label the simulated pair "C2 compound and C4 compound", but the abstract ("two promising compounds") and all MD figures use the top-2 hits ZINC287819616/ZINC513417492 — paper-internal inconsistency)
- **No QSAR, no DFT, no Optuna, no ML**

## Computational Tool Capabilities

Workflow stages and the capabilities each requires, with the evidence every stage must produce. Record unavailable capabilities and leave their required evidence unresolved.

| Stage | Capability | Expected Evidence |
|---|---|---|
| 1. Validate inputs and baseline | Retrieve/prepare the PDB structure(s) and public libraries; reproduce the paper's redock or reference baseline where stated. | Prepared structure and library files with provenance; redock RMSD or reference score. |
| 2. Hit generation | Pharmit-style pharmacophore build + screen (`pharmacophoreHypothesis`, `Pharmacophore_Screening`) | Hypothesis/features, ranked hit lists, filter counts. |
| 3. Docking | `Vina_basic_docking` at the paper-verbatim grid/box; `Diffdock` second-engine on finalists. | Score tables with grid parameters; second-engine poses. |
| 4. ADMET / drug-likeness | `Property_Prediction` (SwissADME-class). | ADMET rows covering every pass-bar filter. |
| 5. MD validation (secondary) | `MDS_openMM`; `Binding_affinity_Prediction` corroboration. | Trajectory summaries; affinity ranking vs reference. |
| 6. Select and report | Apply the pass bar, rank hits, write the Expected Output files. | All expected files incl. `metrics.json`; exclusions and limitations noted. |

**Boltzmann platform tools:**
| Tool | Role | Key Arguments |
|------|------|---------------|
| `pharmacophoreHypothesis` | 5YS-based model | `pdb_file`, features |
| `Pharmacophore_Screening` | Screen ZINC | hypothesis + library |
| `Vina_basic_docking` | Dock into ROCK2 (7P6N) | `pdb_file`, `center_x/y/z`, `exhaustivness`, `smiles` |
| `Diffdock` | Second-engine | `processed_pdb`, `input_csv` |
| `Property_Prediction` | ADMET | `smiles`, `global_models` |
| `MDS_openMM` | 150 ns MD of both hits | topology, `duration_ns` |
| `Binding_affinity_Prediction` | ROCK2 (UniProt O75116, human, derived) | `smiles`, `tar_seq`, `mode` |

**Other standard tools:** Pharmit, Glide SP, OSIRIS Property Explorer, admetSAR, GROMACS + Bio3D.

**Paper tools (verbatim):** Pharmit server, ZINC database (13,127,550), Schrödinger LigPrep (OPLS_2005), Protein Preparation Wizard, MODELLER, PROPKA (pH 7.0), Glide SP, Discovery Studio client, OSIRIS Property Explorer, admetSAR, GROMACS (CHARMM36, TIP3P, 310 K/1 atm), R Bio3D.

## Evaluation Metrics

| Metric | Published value |
|---|---|
| Top hits | ZINC287819616 −9.939; ZINC513417492 −9.894 kcal/mol |
| Top-10 range | −9.939 to −9.082 kcal/mol (Table 2; abstract quotes −11.55 to −9.91 — use table values) |
| ADMET | Both hits pass all OSIRIS risks; drug-likeness 6.09/7.17, drug score 0.75/0.66; HIA+, BBB+ |
| MD | 150 ns; stable RMSD/RMSF/Rg/SASA/H-bonds; PCA compact |

## Expected Output

**Format:** `small_molecule_vs_bundle`
**Directory:** `results/task_002/<run>/`

| File | Content |
|---|---|
| `pharmacophore_model.json` | Hypothesis + feature coordinates |
| `screening_results.csv` | Ranked ZINC candidates (4809 → top 10) |
| `docking_scores.csv` | Top scores + interactions |
| `admet_panel.csv` | OSIRIS/admetSAR-equivalent profiles |
| `md_analysis.csv` | RMSD/RMSF/Rg/SASA/H-bond summaries |
| `metrics.json` | Best hit score |

**Pass bar:** ≥2 candidates at −9.89 kcal/mol or better (Glide SP-anchored; compare engine-relative — paper top-2: −9.939/−9.894) with acceptable ADMET and stable MD.

## Constraints

- **Time Limit:** 240 minutes of agent working time (long-running platform jobs may complete asynchronously beyond it)
- **Reference Policy:** use the tools and workflow above; do NOT look up the source publication to copy its hit lists or scores
- **Knowledge Cutoff:** not applicable — retrospective paper-anchored task; every required parameter is stated in this document
- **Evaluation Integrity:** freeze candidate selection, scores, and rankings before comparing them against the paper's published reference values

## Important Instructions

- Solve this task using the provided tools and your own reasoning.
- Do NOT search for, reference, or reproduce the source paper's specific hits, scores, or tables — the run is evaluated on completing the workflow and meeting the pass bar, not on matching published values.

## Publication

[Alanzi AR, PLoS ONE (2025)](https://doi.org/10.1371/journal.pone.0323781). [PMC12074392](https://pmc.ncbi.nlm.nih.gov/articles/PMC12074392/)
