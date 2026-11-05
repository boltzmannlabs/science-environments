# Task 003 — Targeting CDK1 in cancer: docking and dynamics of dinaciclib analogs

## Description

Triage a PubChem library of 100 dinaciclib analogs against CDK1 by drug-likeness and ADMET filters, dock the survivors with AutoDock-style scoring into the single CDK1 crystal structure, and validate the top two hits by 100 ns MD — with target justification from public TCGA-BRCA expression and kmplot survival data.

## Target

**Name:** Cyclin-dependent kinase 1 (CDK1)
**Disease:** Cancer (pan-cancer; TCGA-BRCA focus)
**Data:** PubChem dinaciclib analogs (hits 46916588, 67133456); parent/reference compound: dinaciclib itself (CID 46926350); TCGA-BRCA (gdc.cancer.gov) and kmplot survival (kmplot.com) — both public; Supplementary DOCX verified: Table S1 = all 100 evaluated analogs with PubChem CIDs, SwissADME properties and Lipinski-violation marks (9 violations → the 91 passing), Table S2 = all 73 docked compounds with dock scores (dinaciclib −8.5 at rank 01; hits at ranks 49 and 69)
**PDB:** 6GU7 (the single CDK1 crystal structure used for both docking and MD; RCSB metadata — the paper names 6GU7 but none of the following: 2.75 Å, CDK1/CKS2 complex, co-crystal ligand AZD5438/FB8)

## Design Constraints

- **Workflow:** 100 PubChem dinaciclib analogs → Discovery Studio structure analysis → SwissADME Lipinski filter (100 → 91) → SwissADME ADMET filter (91 → 73) → docking of 73 into 6GU7 → top-2 selection → 100 ns MD (Desmond) of both hit complexes
- **Docking protocol:** grid box 14×14×13 Å at 0.3 Å spacing; Lamarckian Genetic Algorithm; 3 replicates × 50 solutions; population 500; 2.5M energy evaluations
- **Engine note:** the AutoDock 4.2.6 protocol parameters are paper-verbatim; platform runs use Vina/Diffdock, whose kcal/mol scales differ — treat −9.3 as an AutoDock-anchored bar and derive Ki from ΔG (Ki = e^(ΔG/RT))
- **MD as secondary validation of the top 2 hits**
- **Reference standard:** dinaciclib (CID 46926350), −8.5 kcal/mol (Table 1) — the published top hits beat it by 0.7–0.8 kcal/mol
- **No QSAR, no DFT, no Optuna, no ML**

## Computational Tool Capabilities

**Boltzmann platform tools:**
| Tool | Role | Key Arguments |
|------|------|---------------|
| `Similarity_Screening` | Dinaciclib-analog retrieval | query + library |
| `Vina_basic_docking` | Dock into CDK1 (6GU7) | `pdb_file`, `center_x/y/z`, `exhaustivness`, `smiles` |
| `Diffdock` | Second-engine | `processed_pdb`, `input_csv` |
| `Property_Prediction` | SwissADME-equivalent ADMET/Lipinski | `smiles`, `global_models` |
| `MDS_openMM` | 100 ns MD of top hits | topology, `duration_ns` |
| `Binding_affinity_Prediction` | CDK1 (UniProt P06493, derived) | `smiles`, `tar_seq`, `mode` |

**Other standard tools:** AutoDock 4.2.6 (paper engine), SwissADME, Desmond, UCSF Chimera, Discovery Studio.

**Paper tools (verbatim):** PubChem, Discovery Studio v18, SwissADME, AutoDock 4.2.6, UCSF Chimera, Desmond 2020.1 (Schrödinger, OPLS-2005, SPC), ChemSpider; expression/survival context: GEPIA2, TIMER 2.0, UALCAN, KM plotter.

## Evaluation Metrics

| Metric | Published value |
|---|---|
| Best hit | 46916588: −9.3 kcal/mol, Ki 1.07 µM (H-bonds Ile10/Ser84/Asp86; π-σ Leu135) |
| Second hit | 67133456: −9.2 kcal/mol, Ki 2.1 µM (H-bonds Ser84/Asp86/Gln132; π-σ Ile10/Leu135) |
| Comparator | Dinaciclib (CID 46926350): −8.5 kcal/mol |
| Filters | 100 → 91 (Lipinski) → 73 (ADMET) (the Discussion says 72; 73 is used per Methods/Results) |
| MD | 100 ns; CDK1 Cα-backbone RMSD 0.2 Å (46916588) / 0.9 Å (67133456) |
| ADMET | Table 1: solubility, BBB, H-acc, H-don, MW per compound |

## Expected Output

| File | Content |
|---|---|
| `admet_filters.csv` | 100 analogs with Lipinski + ADMET pass/fail |
| `docking_scores.csv` | Docked 73 with scores + Ki vs top hits |
| `admet_panel.csv` | Final-hit pharmacokinetic profile |
| `metrics.json` | Best score + Ki |

**Pass bar:** ≥1 analog docking at −9.3 kcal/mol or better with acceptable ADMET and stable MD.

## Constraints

- **Time Limit:** 240 minutes of agent working time (long-running platform jobs may complete asynchronously beyond it)
- **Reference Policy:** use the tools and workflow above; do NOT look up the source publication to copy its hit lists or scores

## Important Instructions

- Solve this task using the provided tools and your own reasoning.
- Do NOT search for, reference, or reproduce the source paper's specific hits, scores, or tables — the run is evaluated on completing the workflow and meeting the pass bar, not on matching published values.

## Publication

[Med Oncol (2022)](https://doi.org/10.1007/s12032-022-01748-2). [PMC9207877](https://pmc.ncbi.nlm.nih.gov/articles/PMC9207877/)
