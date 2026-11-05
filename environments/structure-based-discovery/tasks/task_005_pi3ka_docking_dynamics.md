# Task 005 — Structure-based virtual screening of a kinase inhibitor library against PI3Kα for non-small cell lung cancer

## Description

Run a redocking-validated docking cascade over a 36,324-compound kinase inhibitor library against PI3Kα, take the top ten hits into MMGBSA, ADMET, induced-fit docking, and MD, benchmarked against the approved drug Copanlisib.

## Target

**Name:** PI3Kα (PIK3CA)
**Protein:** PIK3CA/p110α (UniProt P42336, paper-sourced)
**Disease:** Non-small cell lung cancer
**Objective:** Discover PI3Kα inhibitors meeting the −3.941 kcal/mol Glide XP-referenced bar with MMGBSA ≤ −42.58 and acceptable ADMET (derived)
**Binding Region:** PI3Kα ATP-site region of 4JPS defined by NVP-BYL719 (RCSB ligand 1LT)
**Data:** Compound library + hit tables in article + ESI via the DOI (paper: "Electronic supplementary information (ESI) available. See DOI: 10.1039/d2ra03451d"; RSC supplementary file RA-012-D2RA03451D-s001)
**PDB:** 4JPS (2.20 Å, R-value 0.206; co-crystal ligand NVP-BYL719; RCSB metadata: ligand component 1LT, chain A engineered solubilizing mutations M232K/L233K)
**Structure and Context:** 4JPS is a third-party Novartis deposition, not the paper's own structure; chain A carries engineered solubilizing mutations (RCSB metadata)
**Reference Inputs:** NVP-BYL719 co-crystal reference in 4JPS; ChemDiv kinase-focused set (access date 1 July 2022) is account-gated — public-substitute clause applies (see Design Constraints)

## Design Constraints

- **Workflow:** Protein prep (OPLS3e, PROPKA 7.5) + grid from co-crystal ligand NVP-BYL719 → redocking validation (RMSD 1.1327 Å < 2.0 Å) → docking cascade (HTVS → best 1000 → SP → best 30 → XP → top 10) of 36,324 ChemDiv kinase inhibitors → MMGBSA + QikProp ADMET + IFD (best 2) + 100 ns MD (2 leads + Copanlisib)
- **Reference standard:** Copanlisib (Glide XP −3.941 kcal/mol; MMGBSA −42.58)
- **MD as secondary validation of top hits**
- **No QSAR, no DFT, no ML, no wet lab**
- **Library executability:** the paper's 36,324-compound ChemDiv kinase set (access date 1 July 2022) is account-gated; substitute a public kinase-focused set (e.g., ChEMBL/BindingDB kinase actives) and screen a tractable subset (≥1,000 compounds), scaling cascade cut-offs proportionally (top ~3% → SP tier, top 30 → XP tier)

## Computational Tool Capabilities

Workflow stages and the capabilities each requires, with the evidence every stage must produce. Record unavailable capabilities and leave their required evidence unresolved.

| Stage | Capability | Expected Evidence |
|---|---|---|
| 1. Validate inputs and baseline | Retrieve/prepare the PDB structure(s) and public libraries; reproduce the paper's redock or reference baseline where stated. | Prepared structure and library files with provenance; redock RMSD or reference score. |
| 2. Hit generation | Pharmacophore/similarity hit generation (`pharmacophoreHypothesis`, `Similarity_Screening`) | Hypothesis/features, ranked hit lists, filter counts. |
| 3. Docking | `Vina_basic_docking` at the paper-verbatim grid/box; `Diffdock` second-engine on finalists. | Score tables with grid parameters; second-engine poses. |
| 4. ADMET / drug-likeness | `Property_Prediction` (SwissADME-class). | ADMET rows covering every pass-bar filter. |
| 5. MD validation (secondary) | `MDS_openMM`; `Binding_affinity_Prediction` corroboration. | Trajectory summaries; affinity ranking vs reference. |
| 6. Select and report | Apply the pass bar, rank hits, write the Expected Output files. | All expected files incl. `metrics.json`; exclusions and limitations noted. |

**Boltzmann platform tools:**
| Tool | Role | Key Arguments |
|------|------|---------------|
| `binding_site` / `fpocket` | Grid-site definition (or centroid of co-crystal ligand NVP-BYL719) | `pdb_file` |
| `Vina_basic_docking` | Docking cascade equivalent | `pdb_file`, `center_x/y/z`, `exhaustivness`, `smiles` |
| `Diffdock` | Second-engine / IFD proxy | `processed_pdb`, `input_csv` |
| `Property_Prediction` | ADMET | `smiles`, `global_models` |
| `MDS_openMM` | MD of top hits | topology, `duration_ns` |
| `Binding_affinity_Prediction` | PI3Kα (P42336) + MMGBSA-style ranking | `smiles`, `tar_seq`, `mode` |

**Other standard tools:** Schrödinger Glide HTVS/SP/XP, Prime MMGBSA + IFD, QikProp, Desmond, SwissADME.

**Paper tools (verbatim):** Schrödinger Maestro suite (Protein Preparation Wizard + PROPKA, Epik, LigPrep, Glide, Receptor Grid Generation, Prime MMGBSA VSGB 2.0, QikProp, IFD, Desmond; OPLS3e), ChemDiv kinase library, PubChem, SwissADME (synthetic accessibility), ChemDraw.

## Evaluation Metrics

| Metric | Published value |
|---|---|
| Library | 36,324 ChemDiv kinase inhibitors |
| Cascade | HTVS → 1000 → SP → 30 → XP → top 10; redock RMSD 1.1327 Å |
| Reference | Copanlisib: XP −3.941 kcal/mol, MMGBSA −42.58, IFD −2244.06 |
| Top hits | 6943: −11.973 / MMGBSA −62.97; 34100: −11.312 / −55.18 (leads; IFD −2252.79 / −2245.53) |
| MD | 100 ns; RMSD 6943 1.2–1.6 Å; 34100 2–3 Å; Copanlisib 2–4 Å |

## Expected Output

**Format:** `small_molecule_vs_bundle`
**Directory:** `results/task_005/<run>/`

| File | Content |
|---|---|
| `screening_ranking.csv` | Cascade-ranked library |
| `docking_scores.csv` | Top 10 vs Copanlisib |
| `admet_panel.csv` | ADMET profiles |
| `metrics.json` | Best hit score |

**Pass bar:** ≥1 hit with docking score ≤ −3.941 kcal/mol in the engine used (Vina/Diffdock equivalent of the Glide XP reference) and MMGBSA-style ΔG ≤ −42.58 (Copanlisib reference) with acceptable ADMET.

## Constraints

- **Time Limit:** 240 minutes of agent working time (long-running platform jobs may complete asynchronously beyond it)
- **Reference Policy:** use the tools and workflow above; do NOT look up the source publication to copy its hit lists or scores
- **Knowledge Cutoff:** not applicable — retrospective paper-anchored task; every required parameter is stated in this document
- **Evaluation Integrity:** freeze candidate selection, scores, and rankings before comparing them against the paper's published reference values

## Important Instructions

- Solve this task using the provided tools and your own reasoning.
- Do NOT search for, reference, or reproduce the source paper's specific hits, scores, or tables — the run is evaluated on completing the workflow and meeting the pass bar, not on matching published values.

## Publication

[RSC Adv (2022)](https://doi.org/10.1039/D2RA03451D). [PMC9346375](https://pmc.ncbi.nlm.nih.gov/articles/PMC9346375/)
