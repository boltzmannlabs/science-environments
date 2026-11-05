# Task 001 — Fragment-based virtual screening of carbonic anhydrase II inhibitors

## Description

Screen fragment-like sulfonamide and non-sulfonamide ZINC libraries against human carbonic anhydrase II (CAII) using pharmacophore models, DOCK 6 + Glide docking, MM-GBSA rescoring, and 100 ns MD validation.

## Target

**Name:** Human carbonic anhydrase II (CAII/CA2)
**Protein:** Carbonic anhydrase 2 (UniProt P00918, derived)
**Disease:** Glaucoma, tubular kidney acidosis, osteoporosis
**Objective:** Screen fragment-like ZINC libraries for CAII inhibitors that dock ≤ −8.0 kcal/mol (engine-relative) and rank top-3 by MM-GBSA (derived)
**Binding Region:** Zn²⁺ active site (His94/His96/His119/Thr199); docking box centered on the catalytic Zn²⁺
**Data:** Library criteria, pharmacophore models, and hit tables in article + Supplementary Material (paper: "The original contributions presented in the study are included in the article/Supplementary Material, further inquiries can be directed to the corresponding author")
**PDB:** 3IGP (1.65 Å)
**Structure and Context:** Human CAII crystal structure used for docking and pharmacophore training
**Reference Inputs:** 3IGP (CAII crystal structure); ZINC fragment-like subset — MW ≤200 Da, xlogP 0.5, 1–3 rotatable bonds, ≤3 HBA/HBD, net charge −2..+2 → 15,596 compounds

## Design Constraints

- **Workflow:** Fragment-like library from ZINC (MW ≤200 Da, xlogP 0.5, 1–3 rotatable bonds, ≤3 HBA/HBD, net charge −2..+2; 15,596 compounds) → DOCK 6 docking + Zn–N 2.5 Å pose filter → ~186 ligands (the paper's SQM rescoring pass between DOCK 6 and selection is out of scope — see note below) → Glide refinement docking → MM-GBSA rescoring → Phase pharmacophore hypotheses (10, sulfonamide set — non-sulfonamides modeled separately; trained on 56, tested on 130 of the docked set) → 3 sulfonamide (S6–S8) + 4 non-sulfonamide (S1, S2, S15, S16) hits → 100 ns MD → QikProp ADME + ProTox-II toxicity
- **Fragment-based drug discovery (FBDD) framing**
- **MD as secondary validation of top hits**
- **Out of scope:** the paper's auxiliary QM steps (SQM rescoring pass; B3LYP/6-31G PES scans of linker flexibility) are excluded — rescore with MM-GBSA only
- **No QSAR, no DFT, no ML, no wet lab**
- **Platform triage:** DOCK 6/Glide/Phase steps denote paper provenance — substitute the Vina/Diffdock equivalents; pre-filter the 15,596-compound library to ≤200–500 candidates via `pharmacophoreHypothesis`/`Similarity_Screening` before docking (per-ligand platform jobs cannot cover the full set within the time limit)

## Computational Tool Capabilities

Workflow stages and the capabilities each requires, with the evidence every stage must produce. Record unavailable capabilities and leave their required evidence unresolved.

| Stage | Capability | Expected Evidence |
|---|---|---|
| 1. Validate inputs and baseline | Retrieve/prepare the PDB structure(s) and public libraries; reproduce the paper's redock or reference baseline where stated. | Prepared structure and library files with provenance; redock RMSD or reference score. |
| 2. Hit generation | Fragment/pharmacophore triage of the ZINC library (`pharmacophoreHypothesis`, `Similarity_Screening`) | Hypothesis/features, ranked hit lists, filter counts. |
| 3. Docking | `Vina_basic_docking` at the paper-verbatim grid/box; `Diffdock` second-engine on finalists. | Score tables with grid parameters; second-engine poses. |
| 4. ADMET / drug-likeness | `Property_Prediction` (SwissADME-class). | ADMET rows covering every pass-bar filter. |
| 5. MD validation (secondary) | `MDS_openMM`; `Binding_affinity_Prediction` corroboration. | Trajectory summaries; affinity ranking vs reference. |
| 6. Select and report | Apply the pass bar, rank hits, write the Expected Output files. | All expected files incl. `metrics.json`; exclusions and limitations noted. |

**Boltzmann platform tools:**
| Tool | Role | Key Arguments |
|------|------|---------------|
| `pharmacophoreHypothesis` | CAII interaction models | ligand/protein features |
| `Similarity_Screening` | Fragment-like ZINC retrieval | query + library |
| `Vina_basic_docking` | Dock into the CAII Zn²⁺ active site of 3IGP (His94/His96/His119/Thr199; box centered on Zn²⁺) | `pdb_file`, `center_x/y/z`, `exhaustivness`, `smiles` |
| `Diffdock` | Second-engine | `processed_pdb`, `input_csv` |
| `Property_Prediction` | ADMET + ProTox-II equivalent | `smiles`, `global_models` |
| `MDS_openMM` | 100 ns MD of top hits | topology, `duration_ns` |
| `Binding_affinity_Prediction` | MM-GBSA-style ranking; CA2 (UniProt P00918, derived) | `smiles`, `tar_seq`, `mode` |

**Other standard tools:** DOCK 6, Glide, Phase, MM-GBSA, Desmond, QikProp, ProTox-II.

**Paper tools (verbatim):** ZINC, Open Babel, UCSF Chimera, DOCK 6, AMBER (H optimization), SQM rescoring, BIOVIA Discovery Studio Viewer 2021, Schrödinger Maestro 2020–23 (LigPrep, Glide), Phase (2023–2024), MM-GBSA, Desmond (TIP3P, OPLS4, NPT 300 K/1.013 bar), QikProp, ProTox-II, B3LYP/6-31G (excluded from task scope).

## Evaluation Metrics

| Metric | Published value |
|---|---|
| Dock + ΔG | e.g., S1 −8.004 kcal/mol; ΔG_bind −46.28 kcal/mol (Table 5) |
| Hit triage | S6–S8 (sulfonamide) + S1, S2, S15, S16 (non-sulfonamide) |
| Toxicity | Table 8 classes: S8 4, S15 4, S16 5 (S1/S2 also class 4); paper text flags "unacceptable toxicities for S2, S3, S6, S7, S11, and S12" and ADME deviations for S1–S3, S7, S11, S14; overall acceptable hits: S8, S15, S16 |
| Validation | 100 ns MD stability (RMSD/RMSF/Rg/SASA/H-bonds) |

## Expected Output

**Format:** `small_molecule_vs_bundle`
**Directory:** `results/task_001/<run>/`

| File | Content |
|---|---|
| `pharmacophore_models.json` | Validated hypotheses |
| `screening_ranking.csv` | Ranked fragment library |
| `docking_scores.csv` | Dock + ΔG_bind values |
| `admet_panel.csv` | Toxicity/ADMET profiles |
| `metrics.json` | Best dock + ΔG |

**Pass bar:** ≥1 hit with docking ≤ −8.0 kcal/mol (engine-relative), a top-3 MM-GBSA ΔG ranking among triaged hits (paper reference: S1 −46.28 kcal/mol), and a non-toxic (ProTox-II class 4–5) profile.

## Constraints

- **Time Limit:** 240 minutes of agent working time (long-running platform jobs may complete asynchronously beyond it)
- **Reference Policy:** use the tools and workflow above; do NOT look up the source publication to copy its hit lists or scores
- **Knowledge Cutoff:** not applicable — retrospective paper-anchored task; every required parameter is stated in this document
- **Evaluation Integrity:** freeze candidate selection, scores, and rankings before comparing them against the paper's published reference values

## Important Instructions

- Solve this task using the provided tools and your own reasoning.
- Do NOT search for, reference, or reproduce the source paper's specific hits, scores, or tables — the run is evaluated on completing the workflow and meeting the pass bar, not on matching published values.

## Publication

[Front Chem (2025)](https://doi.org/10.3389/fchem.2025.1627793). [PMC12528100](https://pmc.ncbi.nlm.nih.gov/articles/PMC12528100/)
