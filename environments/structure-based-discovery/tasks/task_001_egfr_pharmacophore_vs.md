# Task 001 — Integrated pharmacophore and docking screen for EGFR inhibitors across commercial databases

## Description

Generate a pharmacophore from the EGFR co-crystal ligand R85, run ligand-based virtual screening across nine commercial databases, dock the 1271 hits into EGFR, profile ADMET, and validate the top three compounds by 200 ns MD.

## Target

**Name:** Epidermal growth factor receptor (EGFR)
**Protein:** EGFR/ERBB1 (UniProt P00533, derived)
**Disease:** Cancer (EGFR-dysregulated tumors)
**Objective:** Find EGFR binders that out-dock R85 and known EGFR inhibitors with QikProp-range compliance (derived)
**Binding Region:** EGFR ATP-binding kinase domain; the 7AEI R85 co-crystal defines the site and pharmacophore
**Data:** All hits/scores in article ("All relevant data are within the article"); nine databases named (ZINC, Lab Network, PubChem, Moleport, Enamine, MCULE, Chemspace, ChemDiv, CHEMBL); MCULE/CSC compound IDs given
**PDB:** 7AEI (R85 co-crystal); mutant cross-docking 3W2O, 3W2Q, 5D41, 5Y9T
**Structure and Context:** 7AEI reference structure; mutants 3W2O/3W2Q/5D41/5Y9T for cross-docking
**Reference Inputs:** R85 reference ligand (7AEI); nine public databases assembled by the authors into the screening library (listed in-doc)

## Design Constraints

- **Workflow:** Pharmit pharmacophore from R85 (6 features: 2 hydrophobic, 2 HBA, 2 aromatic) → ligand-based VS of 9 databases with Lipinski filters → 1271 hits (MCULE highest yield: 446) → Glide SP docking (grid at X,Y,Z = 8.32, 6.48, 9.1) → top 10 by docking score → ADMET (QikProp) → top 3 compounds by QPPCaco → 200 ns MD + MM/GBSA
- **Benchmarks:** R85 and known ATP-competitive EGFR inhibitors docked for comparison (−7.18 to −5.60 kcal/mol)
- **MD as secondary validation of top 3 hits**
- **No QSAR, no DFT, no ML, no wet lab**

## Computational Tool Capabilities

Workflow stages and the capabilities each requires, with the evidence every stage must produce. Record unavailable capabilities and leave their required evidence unresolved.

| Stage | Capability | Expected Evidence |
|---|---|---|
| 1. Validate inputs and baseline | Retrieve/prepare the PDB structure(s) and public libraries; reproduce the paper's redock or reference baseline where stated. | Prepared structure and library files with provenance; redock RMSD or reference score. |
| 2. Hit generation | Ligand-based pharmacophore VS across public databases (`pharmacophoreHypothesis`, `Pharmacophore_Screening`) | Hypothesis/features, ranked hit lists, filter counts. |
| 3. Docking | `Vina_basic_docking` at the paper-verbatim grid/box; `Diffdock` second-engine on finalists. | Score tables with grid parameters; second-engine poses. |
| 4. ADMET / drug-likeness | `Property_Prediction` (SwissADME-class). | ADMET rows covering every pass-bar filter. |
| 5. MD validation (secondary) | `MDS_openMM`; `Binding_affinity_Prediction` corroboration. | Trajectory summaries; affinity ranking vs reference. |
| 6. Select and report | Apply the pass bar, rank hits, write the Expected Output files. | All expected files incl. `metrics.json`; exclusions and limitations noted. |

**Boltzmann platform tools:**
| Tool | Role | Key Arguments |
|------|------|---------------|
| `pharmacophoreHypothesis` | R85-based model | ligand features |
| `Pharmacophore_Screening` | Screen 9 databases | hypothesis + library |
| `Vina_basic_docking` | Dock into EGFR | `pdb_file`, `center_x/y/z`, `exhaustivness`, `smiles` |
| `Diffdock` | Second-engine | `processed_pdb`, `input_csv` |
| `Property_Prediction` | QikProp ADMET | `smiles`, `global_models` |
| `MDS_openMM` | 200 ns MD of top 3 | topology, `duration_ns` |
| `Binding_affinity_Prediction` | EGFR (UniProt P00533, derived) + MM/GBSA ranking | `smiles`, `tar_seq`, `mode` |

**Other standard tools:** Pharmit, Glide SP, QikProp, Desmond, MM/GBSA (total binding free energy).

**Paper tools (verbatim):** Pharmit server, LigPrep (Maestro, OPLS_2005), Protein Preparation Wizard, PROPKA (pH 7.0), Glide SP, QikProp, Desmond (OPLS_2005, TIP3P, 0.15 M NaCl, NPT 300 K), Discovery Studio client, MM/GBSA (total binding free energy).

## Evaluation Metrics

| Metric | Published value |
|---|---|
| Hit docking range | −7.691 to −7.338 kcal/mol |
| Reference inhibitors | R85 −7.18, osimertinib −6.94, afatinib −6.41, gefitinib −6.25, erlotinib −5.60 kcal/mol |
| Top compounds | MCULE-6473175764, CSC048452634, CSC070083626 (best QPPCaco among hits: 939.9/1255.9/712.3) |
| MM/GBSA ΔG | −47.92 / −36.16 / −48.69 kcal/mol |
| MD | 200 ns; stable RMSD/RMSF for all three |

## Expected Output

**Format:** `small_molecule_vs_bundle`
**Directory:** `results/task_001/<run>/`

| File | Content |
|---|---|
| `pharmacophore_model.json` | R85-based hypothesis |
| `screening_results.csv` | 1271 ranked hits |
| `docking_scores.csv` | Hits vs references |
| `admet_panel.csv` | QikProp profiles |
| `metrics.json` | Best hit score |

**Pass bar:** ≥1 hit out-docking R85/known inhibitors with acceptable ADMET (QikProp ranges: QPlogHERG < −5, QPlogPo/w −2.0 to 6.5, QPlogBB −3.0 to 1.2, QPlogKhsa −1.5 to 1.5; MW < 500).

## Constraints

- **Time Limit:** 240 minutes of agent working time (long-running platform jobs may complete asynchronously beyond it)
- **Reference Policy:** use the tools and workflow above; do NOT look up the source publication to copy its hit lists or scores
- **Knowledge Cutoff:** not applicable — retrospective paper-anchored task; every required parameter is stated in this document
- **Evaluation Integrity:** freeze candidate selection, scores, and rankings before comparing them against the paper's published reference values

## Important Instructions

- Solve this task using the provided tools and your own reasoning.
- Do NOT search for, reference, or reproduce the source paper's specific hits, scores, or tables — the run is evaluated on completing the workflow and meeting the pass bar, not on matching published values.

## Publication

[PLoS ONE (2024)](https://doi.org/10.1371/journal.pone.0311527). [PMC11627428](https://pmc.ncbi.nlm.nih.gov/articles/PMC11627428/)
