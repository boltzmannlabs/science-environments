# Task 006 — Pharmacophore-mapped virtual screening of heterocycles against the H1 receptor for allergic rhinitis

## Description

Screen a set of literature heterocycles against the histamine H1 receptor using a ligand-based e-pharmacophore built from six antihistamines, cluster by SwissADME ADMET profile (BBB exclusion), dock the survivors, and validate the top compounds by MD.

## Target

**Name:** Histamine H1 receptor (HRH1)
**Disease:** Allergic rhinitis
**Data:** 184-compound heterocycle library in article + Supplementary (structures shown as 2D depictions; SMILES transcribed from the depictions/Supplementary); public PDB
**PDB:** 7DFL (docking validated by redocking the co-crystallized ligand (histamine), RMSD 1.77 Å; azelastine docked as reference inhibitor)

## Design Constraints

- **Workflow:** 184 organic heterocycles → SwissADME profiling → 3 clusters (BOILED-Egg) → BBB-excluding cluster 1 (74 compounds, I–LXXIV) → e-pharmacophore mapping (3 features: 2 ring + 1 positive ionic; ≥2 features → 62 compounds) → docking vs azelastine reference → DS-ADMET screen → 50 ns MD (Desmond) of XVIII/XX/XXI + apo with MM-GBSA analysis
- **Pharmacophore hypothesis:** built from azelastine, cetirizine, chlorpheniramine, diphenhydramine, fexofenadine, loratadine; ROC 0.83
- **Design goal:** second-generation profile (no BBB penetration, no hepatotoxicity, no CYP2D6 inhibition)
- **MD as secondary validation of final picks**
- **No QSAR, no DFT, no ML, no wet lab**

## Computational Tool Capabilities

**Boltzmann platform tools:**
| Tool | Role | Key Arguments |
|------|------|---------------|
| `lig_phcore` | e-pharmacophore from 6 antihistamines | ligand set |
| `Pharmacophore_Screening` | Map heterocycles to hypothesis | hypothesis + library |
| `Property_Prediction` | SwissADME equivalent (BBB, CYP2D6) | `smiles`, `global_models` |
| `Butina_Clustering` | ADMET-space clustering | descriptors |
| `Vina_basic_docking` | Dock into 7DFL (redocking-validated; site centered on co-crystallized histamine in the binding-site chain) | `pdb_file`, `center_x/y/z`, `smiles` |
| `Diffdock` | Second-engine | `processed_pdb`, `input_csv` |
| `MDS_openMM` | MD of top hits | topology, `duration_ns` |
| `Binding_affinity_Prediction` | HRH1 (UniProt P35367, derived) | `smiles`, `tar_seq`, `mode` |

**Other standard tools:** SwissADME, Schrödinger e-pharmacophore + MM-GBSA, Desmond, DUD-E, Discovery Studio ADMET.

**Paper tools (verbatim):** SwissADME (online), Schrödinger Maestro (e-pharmacophore + DUD-E validation), docking engine not named in the paper, Discovery Studio 2016 (ADMET), Desmond (50 ns MD), MM-GBSA.

## Evaluation Metrics

| Metric | Published value |
|---|---|
| Reference docking score | Azelastine −6.56 kcal/mol (text) vs −7.33 (text and Table 1 — paper-internal conflict) |
| Final picks | XVIII −9.62, XX −6.26, XXI −6.35 kcal/mol (non-hepatotoxic, CYP2D6-clean) |
| MM-GBSA ΔG | XVIII −64.28; XX −36.76; XXI −37.76 kcal/mol |
| MD | 50 ns; compound XVIII most stable complex |
| Pharmacophore quality | ROC 0.83 / AUAC 0.90 |

## Expected Output

| File | Content |
|---|---|
| `pharmacophore_model.json` | 3-feature hypothesis |
| `admet_clusters.csv` | SwissADME clusters with BBB flags |
| `docking_scores.csv` | Scores vs azelastine reference |
| `metrics.json` | Best docking score |

**Pass bar:** ≥1 compound beating azelastine (−6.56/−7.33 kcal/mol) with second-generation ADMET profile (no BBB, no hepatotoxicity, no CYP2D6 inhibition).

## Constraints

- **Time Limit:** 240 minutes of agent working time (long-running platform jobs may complete asynchronously beyond it)
- **Reference Policy:** use the tools and workflow above; do NOT look up the source publication to copy its hit lists or scores

## Important Instructions

- Solve this task using the provided tools and your own reasoning.
- Do NOT search for, reference, or reproduce the source paper's specific hits, scores, or tables — the run is evaluated on completing the workflow and meeting the pass bar, not on matching published values.

## Publication

[Russ J Bioorg Chem (2022)](https://doi.org/10.1134/S1068162022330019). [PMC9134989](https://pmc.ncbi.nlm.nih.gov/articles/PMC9134989/)
