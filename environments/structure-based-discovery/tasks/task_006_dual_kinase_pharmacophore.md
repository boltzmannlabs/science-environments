# Task 006 — Pharmacophore screening and dual docking for VEGFR-2/c-Met dual-target inhibitors

## Description

Develop and validate pharmacophore models for VEGFR-2 and c-Met, screen a 1.28M-compound commercial library through drug-likeness filters and dual-target docking cascades, and confirm the two best dual hits by 100 ns MD with MM/PBSA.

## Target

**Name:** VEGFR-2 (KDR) + c-Met (MET) — dual target
**Protein:** KDR/VEGFR-2 (UniProt P35968, derived) + MET/c-Met (UniProt P08581, derived)
**Disease:** Cancer (angiogenesis-driven tumors)
**Objective:** Identify dual VEGFR-2/c-Met inhibitors scoring below −60 kJ/mol on both kinases with acceptable ADMET (derived)
**Binding Region:** VEGFR-2 site centered on co-crystal ligand GIG (2OH4); c-Met site centered on MT4 (3EFK)
**Data:** Validation sets, pharmacophore metrics, and hit tables in article + Supplementary; the ChemDiv catalogue is not bulk-downloadable — substitute a public drug-like library of comparable scale (e.g., ZINC purchasable sample ≥10⁵) if unavailable
**PDB:** VEGFR-2 2OH4 (ligand GIG), c-Met 3EFK (ligand MT4)
**Structure and Context:** 2OH4 (GIG) and 3EFK (MT4) co-crystals anchor both kinase sites and the pharmacophore cascade
**Reference Inputs:** Co-crystal ligands GIG (2OH4, VEGFR-2) and MT4 (3EFK, c-Met); DUD-E validation sets (VEGFR-2: 25 actives/375 decoys; c-Met: 25 actives/400 decoys); ChemDiv 1.28M library (not bulk-downloadable — public-substitute clause applies)

## Design Constraints

- **Workflow:** 1.28M compounds collected from ChemDiv → drug-likeness (Lipinski/Veber + ADMET) → 275,866 compounds → pharmacophore development + validation (VEGFR-2: 25 actives/375 DUD-E decoys; c-Met: 25 actives/400 decoys; EF up to 15.3) → pharmacophore screening of the 275,866 (sequential 2OH4_01 → 3EFK_01 cascade, fit >2.4; 78,402 → 28,338 advancing to docking) → LibDock (VEGFR-2 >142.5; c-Met >142.6) → CDOCKER refinement (83 beat GIG; 369 beat MT4; redock RMSD 0.8199/0.2934 Å) → 18 dual hits → top 2 → 100 ns MD + MM/PBSA
- **Dual-activity constraint:** hits must dock strongly into both targets
- **MD as secondary validation of top 2 hits**
- **No QSAR, no DFT, no ML, no wet lab**

## Computational Tool Capabilities

Workflow stages and the capabilities each requires, with the evidence every stage must produce. Record unavailable capabilities and leave their required evidence unresolved.

| Stage | Capability | Expected Evidence |
|---|---|---|
| 1. Validate inputs and baseline | Retrieve/prepare the PDB structure(s) and public libraries; reproduce the paper's redock or reference baseline where stated. | Prepared structure and library files with provenance; redock RMSD or reference score. |
| 2. Hit generation | Pharmacophore cascade screen of a drug-like library (`pharmacophoreHypothesis`, `Pharmacophore_Screening`) | Hypothesis/features, ranked hit lists, filter counts. |
| 3. Docking | `Vina_basic_docking` at the paper-verbatim grid/box; `Diffdock` second-engine on finalists. | Score tables with grid parameters; second-engine poses. |
| 4. ADMET / drug-likeness | `Property_Prediction` (SwissADME-class). | ADMET rows covering every pass-bar filter. |
| 5. MD validation (secondary) | `MDS_openMM`; `Binding_affinity_Prediction` corroboration. | Trajectory summaries; affinity ranking vs reference. |
| 6. Select and report | Apply the pass bar, rank hits, write the Expected Output files. | All expected files incl. `metrics.json`; exclusions and limitations noted. |

**Boltzmann platform tools:**
| Tool | Role | Key Arguments |
|------|------|---------------|
| `pharmacophoreHypothesis` | VEGFR-2 + c-Met models | ligand sets |
| `Pharmacophore_Screening` | Screen drug-likeness-filtered library (275,866) | hypothesis + library |
| `Vina_basic_docking` | Dual docking (sites centered on co-crystal ligands GIG/MT4) | `pdb_file`, `center_x/y/z`, `exhaustivness`, `smiles` |
| `Diffdock` | Second-engine | `processed_pdb`, `input_csv` |
| `Property_Prediction` | ADMET descriptors | `smiles`, `global_models` |
| `MDS_openMM` | 100 ns MD | topology, `duration_ns` |
| `Binding_affinity_Prediction` | VEGFR-2 (UniProt P35968, derived), c-Met (UniProt P08581, derived) | `smiles`, `tar_seq`, `mode` |

**Other standard tools:** DS Discovery Studio (LibDock, CDOCKER, pharmacophore), GROMACS + gmx_MM/PBSA, DUD-E.

**Paper tools (verbatim):** Discovery Studio 2019 (CHARMM protein prep, Receptor Ligand Pharmacophore Generation, Prepare Ligands, Lipinski/Veber filters, ADMET, Ligand Pharmacophore Mapping fit >2.4, LibDock, CDOCKER), DUD-E, ChemDiv (Topscience) 1.28M, GROMACS 2018.8 (CHARMM36, TIP3P, cubic 4.0 nm box), CgenFF, pdb2gmx, gmx_MM/PBSA.

## Evaluation Metrics

| Metric | Published value |
|---|---|
| LibDock cutoffs | VEGFR-2 >142.5 (1,667 hits), c-Met >142.6 (3,529 hits) |
| Docking quality | All 18 dual hits with docking scores below −60 kJ/mol; redock RMSD 0.8199 Å (GIG) / 0.2934 Å (MT4) |
| Pharmacophores | 2OH4_01 EF 15.3, AUC 0.940; 3EFK_01 EF 15.3, AUC 0.960 |
| Final dual hits | compound17924, compound4312 |
| MM/PBSA ΔG | VEGFR-2: 17924 −134.072 vs GIG −88.638; c-Met: 17924 −118.564 vs MT4 −23.696 kJ/mol; 4312 −94.904 (VEGFR-2) / −81.097 (c-Met) |
| MD | 100 ns; c-Met RMSD 17924 0.2834 / 4312 0.2498 vs MT4 0.3568 nm |

## Expected Output

**Format:** `small_molecule_vs_bundle`
**Directory:** `results/task_006/<run>/`

| File | Content |
|---|---|
| `pharmacophore_models.json` | Both hypotheses + validation |
| `screening_ranking.csv` | Cascade-ranked library |
| `docking_scores.csv` | Dual-target scores |
| `admet_panel.csv` | ADMET profiles |
| `metrics.json` | Best dual hit |

**Pass bar:** ≥1 candidate with docking scores below −60 kJ/mol against both kinases and acceptable ADMET.

## Constraints

- **Time Limit:** 240 minutes of agent working time (long-running platform jobs may complete asynchronously beyond it); screening stages may be batched and submitted asynchronously — the pass bar requires only ≥1 dual-active candidate, not full-cascade throughput
- **Reference Policy:** use the tools and workflow above; do NOT look up the source publication to copy its hit lists or scores (validation-set ligand lists for pharmacophore validation may be assembled from DUD-E/public actives; hit identities, scores, and tables are off-limits)
- **Knowledge Cutoff:** not applicable — retrospective paper-anchored task; every required parameter is stated in this document
- **Evaluation Integrity:** freeze candidate selection, scores, and rankings before comparing them against the paper's published reference values

## Important Instructions

- Solve this task using the provided tools and your own reasoning.
- Do NOT search for, reference, or reproduce the source paper's specific hits, scores, or tables — the run is evaluated on completing the workflow and meeting the pass bar, not on matching published values.

## Publication

[Front Pharmacol (2025)](https://doi.org/10.3389/fphar.2025.1534707). [PMC11926154](https://pmc.ncbi.nlm.nih.gov/articles/PMC11926154/)
