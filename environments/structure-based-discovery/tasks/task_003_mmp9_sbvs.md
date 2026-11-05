# Task 003 — Structure-based discovery of MMP-9 inhibitors for cerebral ischemia by pharmacophore screening, docking, ADMET profiling and 200 ns MD

## Description

Identify inhibitors of matrix metalloproteinase-9 (MMP-9) for cerebral ischemia by deriving a structure-based pharmacophore from the 2OVX co-crystal complex, screening a ChEMBL library of 25,083 compounds, docking survivors with Glide SP-style scoring into the catalytic Zn²⁺ site, filtering by SwissADME drug-likeness and ADMETLab toxicity, and validating the top hit by 200 ns MD with MM-GBSA/MM-PBSA against the co-crystal reference.

## Target

**Name:** Matrix metalloproteinase-9 (MMP-9), catalytic domain (S1/S1′ subsites; catalytic Zn²⁺ coordinated by His401/His405/His411 — derived; the paper lists His226, His401, His405, His411 and Glu402 as zinc-coordination/stabilization residues without singling out a triad)
**Protein:** MMP9 (UniProt P14780, derived)
**Disease:** Cerebral ischemia
**Objective:** Discover MMP-9 inhibitors meeting the −9.96 kcal/mol Glide SP-referenced bar with Ames-negative profile and stable 200 ns MD (derived)
**Binding Region:** Catalytic Zn²⁺ site (S1/S1′ subsites); paper grid at X,Y,Z = 24.96, 8.68, 51.16
**Data:** "All data underlying the findings of this study are publicly available in Figshare at: https://doi.org/10.6084/m9.figshare.31425299. The repository includes docking pose coordinates, binding free energy calculation outputs, virtual screening results, raw data used for figure generation, and analysis scripts." — plus Tables 1–5 in-article (no supplementary files)
**PDB:** 2OVX (RCSB metadata — 2.00 Å, co-crystal ligand 4MR, barbiturate inhibitor, active-site-mutant catalytic domain; the paper says only "MMP-9 bound to a selective inhibitor" and names neither ligand nor mutation)
**Structure and Context:** 2OVX active-site-mutant catalytic domain with the 4MR barbiturate co-crystal (RCSB metadata)
**Reference Inputs:** 2OVX with 4MR barbiturate co-crystal; 25,083-compound ChEMBL library (duplicates/salts/inorganics removed, MW 150–600 Da); validation set of known inhibitors + property-matched decoys (ROC AUC 0.70)

## Design Constraints

- **Workflow:** 2OVX preparation (Protein Preparation Wizard; PROPKA pH 7.0) → Phase structure-based pharmacophore (features derived from the crystallographic ligand–protein interactions and proximity to the catalytic Zn²⁺) → validation against known inhibitors + property-matched decoys (ROC AUC 0.70; active/decoy counts not stated) → screen 25,083 ChEMBL compounds (duplicates/salts/inorganics removed, MW 150–600 Da; 20 conformers per compound) → hit = ≥4 features matched AND Phase screen score ≥ 1.5 → 278 hits → Glide SP docking (grid center X=24.96, Y=8.68, Z=51.16; Zn²⁺ retained) → top 10 → SwissADME (Lipinski, PAINS, Brenk) + ADMETLab 3.0 (HIA, VD, BBB, PPB, CYP450, clearance, Ames) → hit CHEMBL3990662 → 200 ns MD (NAMD 3.0, AMBER ff14SB, GAFF/AM1-BCC, TIP3P, 0.15 M NaCl, 310 K) of hit–MMP-9 + co-crystal ligand–MMP-9 reference → MM/GBSA + MM/PBSA (50 snapshots, last 30 ns) + per-residue decomposition
- **Pharmacophore feature count:** the text says seven features (3 aromatic + 3 donor + 1 acceptor) but Table 1 lists six (aromatic R10/R11/R12, donors D7/D8, acceptor A5) — paper-internal conflict; Table 1 coordinates are the ground truth
- **MD duration:** 200 ns in the abstract, results, conclusion and all figure captions, but one Methods sentence says "The production MD run was executed for 100 ns" — paper-internal conflict; 200 ns is used
- **LogP labels:** the text says the compounds "exhibit a balance between hydrophobic (0.82) and hydrophilic (3.90)" but two sentences later calls 3.90 "high lipophilicity" — labels inverted in the first sentence; 0.82 is the hydrophilic end, 3.90 the lipophilic end
- **Cardiotoxicity:** Methods §2.4 lists "risk for cardiotoxicity" among the ADMETLab evaluation criteria, but neither Table 4 nor the Results report any cardiotoxicity prediction (only hepatotoxicity and Ames mutagenicity are discussed) — promised metric never reported
- **Redocking validation:** co-crystal ligand top pose RMSD 0.217 Å vs native pose
- **Engine note:** Glide SP is the paper's docking engine; platform runs use Vina/Diffdock, whose kcal/mol scales differ — treat −9.96 as a Glide-anchored bar and compare engine-relative
- **MD as secondary validation of the top hit vs the co-crystal reference**
- **No QSAR, no DFT, no ML, no wet lab** ("All findings are based on computational modelling"; TCM appears only in affiliations/funding)

## Computational Tool Capabilities

Workflow stages and the capabilities each requires, with the evidence every stage must produce. Record unavailable capabilities and leave their required evidence unresolved.

| Stage | Capability | Expected Evidence |
|---|---|---|
| 1. Validate inputs and baseline | Retrieve/prepare the PDB structure(s) and public libraries; reproduce the paper's redock or reference baseline where stated. | Prepared structure and library files with provenance; redock RMSD or reference score. |
| 2. Hit generation | Structure-based pharmacophore screen of ChEMBL (`pharmacophoreHypothesis`, `Pharmacophore_Screening`) | Hypothesis/features, ranked hit lists, filter counts. |
| 3. Docking | `Vina_basic_docking` at the paper-verbatim grid/box; `Diffdock` second-engine on finalists. | Score tables with grid parameters; second-engine poses. |
| 4. ADMET / drug-likeness | `Property_Prediction` (SwissADME-class). | ADMET rows covering every pass-bar filter. |
| 5. MD validation (secondary) | `MDS_openMM`; `Binding_affinity_Prediction` corroboration. | Trajectory summaries; affinity ranking vs reference. |
| 6. Select and report | Apply the pass bar, rank hits, write the Expected Output files. | All expected files incl. `metrics.json`; exclusions and limitations noted. |

**Boltzmann platform tools:**
| Tool | Role | Key Arguments |
|------|------|---------------|
| `pharmacophoreHypothesis` | 2OVX-derived interaction model | `pdb_file`, features |
| `Pharmacophore_Screening` | ChEMBL-like screen (≥4 features, score ≥ 1.5) | hypothesis + library |
| `Vina_basic_docking` | Dock into MMP-9 (2OVX; paper grid center 24.96/8.68/51.16) | `pdb_file`, `center_x/y/z`, `exhaustivness`, `smiles` |
| `Diffdock` | Second-engine | `processed_pdb`, `input_csv` |
| `Property_Prediction` | SwissADME/ADMETLab-equivalent ADMET | `smiles`, `global_models` |
| `MDS_openMM` | 200 ns MD of hit + reference complexes (paper uses 0.15 M NaCl; if platform ion types exclude Na⁺, substitute equimolar KCl — derived) | topology, `duration_ns` |
| `Binding_affinity_Prediction` | MM-GBSA-style ranking; MMP9 (UniProt P14780, derived) | `smiles`, `tar_seq`, `mode` |

**Other standard tools:** Schrödinger Maestro (Phase, Protein Preparation Wizard, LigPrep, Epik, Glide), PROPKA, Discovery Studio, SwissADME, ADMETLab 3.0, NAMD, AmberTools, R Bio3D.

**Paper tools (verbatim):** Schrödinger Maestro (Protein Preparation Wizard, Phase, LigPrep, Epik, PROPKA, Glide SP), Discovery Studio, SwissADME, ADMETLab 3.0, NAMD 3.0 (AMBER ff14SB — one Methods passage says FF19SB; paper-internal conflict — TIP3P, PME, Langevin), AmberTools24 (antechamber, AM1-BCC, MMPBSA.py), R Bio3D, ChEMBL.

## Evaluation Metrics

| Metric | Published value |
|---|---|
| Top hit | CHEMBL3990662: −9.96 kcal/mol Glide SP; H-bonds Arg424 (1.98 Å), Thr426 (2.56), Tyr423 (2.78), Gly186 (2.12); Zn²⁺ π-cation; hydrophobic Leu418, His401, Leu188 |
| Top-10 range | −9.28 to −9.96 kcal/mol (Table 2; CHEMBL1181759 listed 9th at −9.58, out of descending order — paper quirk) |
| Screen funnel | 25,083 ChEMBL → 278 hits (≥4 features, score ≥ 1.5) → top 10 docked |
| Pharmacophore validation | ROC AUC 0.70 |
| Redock RMSD | 0.217 Å (co-crystal ligand) |
| Drug-likeness (Table 3) | all 10 Lipinski-Yes; PAINS 0 except CHEMBL1194647 and CHEMBL547206 (1 alert each); Brenk 0 for all; TPSA 53.7–146 Å², LogP 0.82–3.90, LogS −2.8 to −5.6 |
| ADMETLab (Table 4) | HIA+ and BBB+ for all 10; PPB+ only 4/10 (CHEMBL3990662, CHEMBL1184827, CHEMBL1194647, CHEMBL1181759); Ames-positive (avoid): CHEMBL1181759, CHEMBL547206; Ames "Yellow" (moderate/uncertain): CHEMBL1184827, CHEMBL3990207, CHEMBL3991298; use table values — the text quotes clearance numbers as "PPB" (paper-internal mix-up) |
| MD 200 ns | hit RMSD ~1.4–1.8 Å (rising to ~2.1–2.3 Å after ~170 ns) vs co-crystal ~2.6–2.9 Å; RMSF mostly 0.4–1.0 Å; Rg ~14.7–15.2 Å; PCA PC1 24.76% (hit) vs 51.88% (co-crystal); FEL 4.5–6.7 kcal/mol |
| MM/GBSA | hit −45.17 vs co-crystal −43.78 kcal/mol; MM/PBSA −12.08 vs −6.21 |
| Decomposition note | per-residue MM/GBSA residues (Gly77, His117, Val114, Leu134, Tyr139, Arg140) never match the docking active-site residues (His401/405/411, Arg424, Tyr423, Gly186, Leu188) — unreconciled in the paper |

## Expected Output

**Format:** `small_molecule_vs_bundle`
**Directory:** `results/task_003/<run>/`

| File | Content |
|---|---|
| `pharmacophore_model.json` | Hypothesis + Table-1-style feature coordinates |
| `screening_results.csv` | 25k-library ranked hits (278-equivalent) |
| `docking_scores.csv` | Top-10 scores + interactions vs reference |
| `admet_panel.csv` | SwissADME/ADMETLab-equivalent profiles |
| `md_energies.csv` | MM-GBSA/PBSA components, hit vs reference |
| `metrics.json` | Best score + ΔG + redock RMSD |

**Pass bar:** ≥1 candidate docking at −9.96 kcal/mol or better (Glide SP-anchored; compare engine-relative) with Lipinski pass, PAINS 0, Ames-negative, MM-GBSA below −45.17 kcal/mol (MMPBSA.py-anchored; compare engine-relative), and stable 200 ns MD relative to the co-crystal reference.

## Constraints

- **Time Limit:** 240 minutes of agent working time (long-running platform jobs may complete asynchronously beyond it)
- **Reference Policy:** use the tools and workflow above; do NOT look up the source publication to copy its hit lists or scores (the public Figshare deposit is for workflow verification only)
- **Knowledge Cutoff:** not applicable — retrospective paper-anchored task; every required parameter is stated in this document
- **Evaluation Integrity:** freeze candidate selection, scores, and rankings before comparing them against the paper's published reference values

## Important Instructions

- Solve this task using the provided tools and your own reasoning.
- Do NOT search for, reference, or reproduce the source paper's specific hits, scores, or tables — the run is evaluated on completing the workflow and meeting the pass bar, not on matching published values.

## Publication

[PLoS ONE (2026)](https://doi.org/10.1371/journal.pone.0346627). [PMC13175377](https://pmc.ncbi.nlm.nih.gov/articles/PMC13175377/)
