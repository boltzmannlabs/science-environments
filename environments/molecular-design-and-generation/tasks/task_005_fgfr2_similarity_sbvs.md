# Task 005 — Similarity-guided structure-based screening of FGFR2 inhibitor-like compounds

## Description

Retrieve FGFR2-inhibitor analogs from PubChem by Tanimoto similarity to clinical FGFR2 inhibitors (erdafitinib, infigratinib, zoligratinib, AZD4547), screen them by molecular docking, and prioritize a drug-like lead with ADMET profiling and MD validation.

## Target

**Name:** Fibroblast growth factor receptor 2 (FGFR2)
**Protein:** FGFR2 (UniProt P21802, derived)
**Disease:** Cancer (FGFR2-dysregulated tumors)
**Objective:** Similarity-guided discovery of FGFR2 inhibitors docking at −11.7 kcal/mol or better with a full ADMET/PAINS pass (derived)
**Binding Region:** FGFR2 kinase pocket defined by the EVC co-crystal of 6LVK
**Data:** All compounds via PubChem CIDs; hits and scores in article + Supplementary
**PDB:** 6LVK (2.29 Å, wild-type, co-crystal ligand EVC)
**Structure and Context:** 6LVK wild-type kinase domain (2.29 Å) with EVC co-crystal
**Reference Inputs:** EVC co-crystal ligand from 6LVK (similarity seed); PubChem CIDs for the paper's candidate set (given in-doc)

## Design Constraints

- **Workflow:** Seed inhibitors (erdafitinib/infigratinib/zoligratinib/AZD4547) → PubChem analogs (Tanimoto ≥80%) → Lipinski/RO5 filter → 2336 compounds (574+231+807+724) → InstaDock/Vina docking (EVC redocking-validated) → top 10 hits → SwissADME + pkCSM ADMET + PAINS/carcinogenicity screen → 200 ns MD of FGFR2–CID507883 with apo-FGFR2 and FGFR2–Zoligratinib references + PCA/FEL
- **Similarity retrieval is the hit-generation engine** (analogs of known inhibitors)
- **Lead selection is ADMET-driven**, not score-driven: CID 507883 (−11.7 kcal/mol, rank 6) is the only compound passing the ADMET/PAINS screen (CarcinoPred-EL is listed among the paper's tools but no carcinogenicity result is reported in the text; likewise PASS appears only in the introduction with no results reported)
- **MD as secondary validation of the lead vs references**
- **No QSAR, no DFT, no ML, no wet lab** (CarcinoPred-EL used only as a pre-trained carcinogenicity web tool)

## Computational Tool Capabilities

Workflow stages and the capabilities each requires, with the evidence every stage must produce. Record unavailable capabilities and leave their required evidence unresolved.

| Stage | Capability | Expected Evidence |
|---|---|---|
| 1. Validate inputs and baseline | Retrieve/prepare the PDB structure(s) and public libraries; reproduce the paper's redock or reference baseline where stated. | Prepared structure and library files with provenance; redock RMSD or reference score. |
| 2. Hit generation | Similarity retrieval from public libraries (`Similarity_Screening`) | Hypothesis/features, ranked hit lists, filter counts. |
| 3. Docking | `Vina_basic_docking` at the paper-verbatim grid/box; `Diffdock` second-engine on finalists. | Score tables with grid parameters; second-engine poses. |
| 4. ADMET / drug-likeness | `Property_Prediction` (SwissADME-class). | ADMET rows covering every pass-bar filter. |
| 5. MD validation (secondary) | `MDS_openMM`; `Binding_affinity_Prediction` corroboration. | Trajectory summaries; affinity ranking vs reference. |
| 6. Select and report | Apply the pass bar, rank hits, write the Expected Output files. | All expected files incl. `metrics.json`; exclusions and limitations noted. |

**Boltzmann platform tools:**
| Tool | Role | Key Arguments |
|------|------|---------------|
| `Similarity_Screening` | PubChem Tanimoto retrieval | query + library |
| `Vina_basic_docking` | Dock into FGFR2 (derived pocket centered on co-crystal ligand EVC; the paper used a structurally blind whole-protein search) | `pdb_file`, `center_x/y/z`, `exhaustivness`, `smiles` |
| `Diffdock` | Second-engine | `processed_pdb`, `input_csv` |
| `Property_Prediction` | SwissADME/pkCSM equivalent | `smiles`, `global_models` |
| `MDS_openMM` | 200 ns MD of top hit | topology, `duration_ns` |
| `Binding_affinity_Prediction` | FGFR2 (UniProt P21802, derived) | `smiles`, `tar_seq`, `mode` |

**Other standard tools:** InstaDock, AutoDock Vina + MGL Tools, SwissADME, pkCSM, GROMACS.

**Paper tools (verbatim):** PubChem, RCSB PDB, MGL AutoDock Tools, InstaDock v1.2, AutoDock Vina, Swiss-PDB Viewer, Discovery Studio Visualizer, PyMOL, VMD, LigPlot+, SwissADME, pkCSM, CarcinoPred-EL, PAINS filter, GROMACS 2020β (GROMOS96 54A7, SPC), gmx covar/anaeig (PCA/FEL).

## Evaluation Metrics

| Metric | Published value |
|---|---|
| Top-10 docking scores | −12.4 to −11.6 kcal/mol (best: CID 137049257 −12.4) |
| Reference scores | Zoligratinib −9.7, AZD4547 −9.0, Erdafitinib −8.5, Infigratinib −8.4 kcal/mol |
| Lead | CID 507883: −11.7 kcal/mol, >80% similarity to Zoligratinib, sole compound passing ADMET/PAINS |
| MD | 200 ns; RMSD 0.42 nm (complex) vs 0.33 (apo) / 0.35 (Zoligratinib); PCA + FEL stable |

## Expected Output

**Format:** `small_molecule_vs_bundle`
**Directory:** `results/task_005/<run>/`

| File | Content |
|---|---|
| `analog_library.csv` | Tanimoto-retrieved PubChem analogs |
| `docking_scores.csv` | Ranked top hits vs references |
| `admet_panel.csv` | SwissADME/pkCSM profiles |
| `metrics.json` | Best docking score |

**Pass bar:** ≥1 candidate docking at −11.7 kcal/mol or better with full ADMET/PAINS pass.

## Constraints

- **Time Limit:** 240 minutes of agent working time (long-running platform jobs may complete asynchronously beyond it)
- **Reference Policy:** use the tools and workflow above; do NOT look up the source publication to copy its hit lists or scores
- **Knowledge Cutoff:** not applicable — retrospective paper-anchored task; every required parameter is stated in this document
- **Evaluation Integrity:** freeze candidate selection, scores, and rankings before comparing them against the paper's published reference values

## Important Instructions

- Solve this task using the provided tools and your own reasoning.
- Do NOT search for, reference, or reproduce the source paper's specific hits, scores, or tables — the run is evaluated on completing the workflow and meeting the pass bar, not on matching published values.

## Publication

[Sci Rep (2024)](https://doi.org/10.1038/s41598-024-69850-1). [PMC11339395](https://pmc.ncbi.nlm.nih.gov/articles/PMC11339395/)
