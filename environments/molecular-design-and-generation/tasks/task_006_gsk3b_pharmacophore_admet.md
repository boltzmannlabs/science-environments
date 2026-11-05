# Task 006 — Discovery of GSK-3β inhibitors for Alzheimer's disease by dual pharmacophore screening, docking, ADME/BBB filtering and MD validation

## Description

Identify brain-penetrant inhibitors of glycogen synthase kinase-3β (GSK-3β) for Alzheimer's disease by building ligand-based and structure-based pharmacophores, screening the ZINCPharmer library, docking hits with Vina-style scoring into PDB 3GB2, filtering by SwissADME drug-likeness with BBB permeation and ProTox toxicity, and validating the top candidates by 100 ns MD with MM-GBSA/MM-PBSA.

## Target

**Name:** Glycogen synthase kinase-3β (GSK-3β)
**Protein:** GSK3B (UniProt P49841, derived)
**Disease:** Alzheimer's disease
**Objective:** Discover brain-penetrant GSK-3β inhibitors beating the −6.80 kcal/mol same-engine Vina co-crystal benchmark with BBB permeance (derived)
**Binding Region:** ATP-binding site; hinge contact with Lys85 (the paper's wording)
**Data:** "Data generated or analyzed during this study are included in this published article. Other data will be made available on request." — all workflow numbers and Tables 1–5 in-article; no supplementary files exist; hit structures appear only as 2D depictions in Table 2 (SB1, LB1–LB3 are labels, not ZINC IDs — the paper's exact hits cannot be regenerated; the run is evaluated on completing the workflow and meeting the pass bar)
**PDB:** 3GB2 (RCSB metadata — 2.40 Å, co-crystal ligand G3B, an oxadiazole-scaffold inhibitor; the paper names the ligand only as an oxadiazole co-crystal, never by ID)
**Structure and Context:** 3GB2 co-crystal supplies the structure-based pharmacophore, the paper-verbatim Vina grid (33.177/14.194/2.494), and the −6.80 benchmark
**Reference Inputs:** 7 reference GSK-3β inhibitors with potencies (tideglusib 60 nM, AZD1080 31 nM, SB-216763 34.3 nM, laduviglusib 6.7 nM, LY2090314 0.9 nM, bisindolylmaleimide I 170–360 nM, compound VII 3.1 nM); 3GB2 co-crystal; ZINCPharmer searchable set (21,777,093 compounds)

## Design Constraints

- **Workflow:** 7 reference GSK-3β inhibitors (tideglusib 60 nM, AZD1080 31 nM, SB-216763 34.3 nM, laduviglusib 6.7 nM, LY2090314 0.9 nM, bisindolylmaleimide I 170–360 nM, compound VII 3.1 nM — ref. 15 (derived: 3GB2's co-crystal originates from this series)) → MOE flexible alignment → **ligand-based pharmacophore** (3 aromatic/hydrophobic + 2 H-bond acceptor/donor feature pairs) ‖ 3GB2 → Pharmit → **structure-based pharmacophore** (3 HBA + 5 hydrophobic features; hinge contact with Lys85 — the paper's wording) → ZINCPharmer screen (21,777,093 compounds; pharmacophore-mapping RMSD ≤ 1.0 Å) → 1,085 LB hits + 36 SB hits → AutoDock Vina 1.1.2 docking (cut-off: beat the co-crystal's −6.80 kcal/mol) → 957 LB (88.2%) + 22 SB (61.1%) → SwissADME filter (≤1 Lipinski violation, BBB permeant, LB series ≥ "moderately soluble") → 4 finalists (SB1, LB1–LB3) → ProTox-3.0 on top 2 (SB1, LB1) → 100 ns MD (GROMACS 2025.3, CHARMM27, TIP3P; 10 ns NVT + 10 ns NPT equilibration, V-rescale thermostat 300 K, Berendsen barostat 1.0 bar, Parrinello-Rahman production barostat) of co-crystal reference, SB1, LB1 → MM-GBSA/MM-PBSA
- **Retrospective ROC validation of both pharmacophores** (LUDe decoys at 50:1): LB model AUC 0.8233 (3 actives + 150 decoys); SB model AUC 0.8200 (1 active + 50 decoys)
- **Redocking validation:** native 3GB2 ligand top-pose RMSD 1.45 Å
- **Docking protocol (paper-verbatim):** grid center x=33.177, y=14.194, z=2.494; box 55×55×55; spacing 0.375 Å; exhaustiveness 32
- **MD as secondary validation of the top hits** (paper reports three simulated systems — Co, SB1, LB1 — while three figure captions reference five MD trajectories; paper-internal conflict)
- **No QSAR, no DFT, no ML in hit-finding; no wet lab** (ProTox-3.0's internal machine-learning organ-toxicity models are a pre-trained web tool — out of scope; use `Property_Prediction`)
- **ADME/BBB-driven finalist selection** — BBB permeance (BOILED-Egg) is the Alzheimer's-specific filter that cuts 979 docking-passing compounds to 4

## Computational Tool Capabilities

Workflow stages and the capabilities each requires, with the evidence every stage must produce. Record unavailable capabilities and leave their required evidence unresolved.

| Stage | Capability | Expected Evidence |
|---|---|---|
| 1. Validate inputs and baseline | Retrieve/prepare the PDB structure(s) and public libraries; reproduce the paper's redock or reference baseline where stated. | Prepared structure and library files with provenance; redock RMSD or reference score. |
| 2. Hit generation | Dual ligand-based (7-inhibitor set) + structure-based (3GB2) pharmacophore screens (`pharmacophoreHypothesis`, `Pharmacophore_Screening`) | Hypothesis/features, ranked hit lists, filter counts. |
| 3. Docking | `Vina_basic_docking` at the paper-verbatim grid/box; `Diffdock` second-engine on finalists. | Score tables with grid parameters; second-engine poses. |
| 4. ADMET / drug-likeness | `Property_Prediction` (SwissADME-class). | ADMET rows covering every pass-bar filter. |
| 5. MD validation (secondary) | `MDS_openMM`; `Binding_affinity_Prediction` corroboration. | Trajectory summaries; affinity ranking vs reference. |
| 6. Select and report | Apply the pass bar, rank hits, write the Expected Output files. | All expected files incl. `metrics.json`; exclusions and limitations noted. |

**Boltzmann platform tools:**
| Tool | Role | Key Arguments |
|------|------|---------------|
| `pharmacophoreHypothesis` | Dual LB (7-inhibitor set) / SB (3GB2) models | `pdb_file`, features |
| `Pharmacophore_Screening` | ZINCPharmer-equivalent screen (RMSD ≤ 1.0 Å) | hypothesis + library |
| `Vina_basic_docking` | Dock into GSK-3β ATP site (3GB2; paper grid center 33.177/14.194/2.494) | `pdb_file`, `center_x/y/z`, `exhaustivness`, `smiles` |
| `Diffdock` | Second-engine | `processed_pdb`, `input_csv` |
| `Property_Prediction` | SwissADME-equivalent ADME + BBB | `smiles`, `global_models` |
| `MDS_openMM` | 100 ns MD of hit complexes + reference | topology, `duration_ns` |
| `Binding_affinity_Prediction` | MM-GBSA-style ranking; GSK3B (UniProt P49841, derived) | `smiles`, `tar_seq`, `mode` |

**Other standard tools:** MOE, Pharmit, ZINCPharmer, AutoDock Vina, OpenBabel, Discovery Studio Visualizer, SwissADME, ProTox-3.0, GROMACS.

**Paper tools (verbatim):** MOE v2019.0102, Pharmit webserver, ZINCPharmer database, OpenBabel, AutoDock Vina v1.1.2, BIOVIA Discovery Studio Visualizer, SwissADME (BOILED-Egg), ProTox-3.0, GROMACS 2025.3 (CHARMM27, SwissParam, TIP3P, V-rescale thermostat, Berendsen NPT barostat, Parrinello-Rahman production barostat), LUDe decoys, GraphPad Prism 10.1.2 Demo.

## Evaluation Metrics

| Metric | Published value |
|---|---|
| Co-crystal benchmark | −6.80 kcal/mol (3GB2 ligand, Vina 1.1.2) |
| Hit docking range | −7.00 to −7.39 kcal/mol (SB1 −7.16, LB1 −7.28, LB2 −7.00, LB3 −7.39) |
| Redock RMSD | 1.45 Å |
| Screen funnel | 21,777,093 ZINCPharmer → 1,085 LB + 36 SB → 957 + 22 beat −6.80 → 4 ADME/BBB survivors |
| Pharmacophore ROC AUC | 0.8233 (LB) / 0.8200 (SB) |
| ADME/BBB (Table 1) | 4 hits: 0 Lipinski violations, oral-bioavailability score 0.55, BBB permeant, high GI absorption, PAINS 0, SA 2.2–3.7; MW 293.32–353.48, LogP 2.80–3.89, TPSA 65.24–73.06 Å² |
| Toxicity (ProTox-3.0) | SB1 LD50 2500 mg/kg, class 5, respiratory toxicity 0.82; LB1 LD50 521 mg/kg, class 4, respiratory 0.69 + nephrotoxicity 0.59 |
| MD 100 ns | Backbone RMSD ≈0.18–0.23 Å; ligand RMSD (production phase) SB1 ≈1.115 / LB1 ≈0.721 / Co ≈1.081 Å; H-bonds SB1 3–6, LB1 0–3, Co 0–2 |
| MM/GBSA ΔG | SB1 −27.68 ± 7.20, LB1 −25.74 ± 3.41 vs Co −8.75 ± 6.93 kcal/mol; MM/PBSA SB1 −26.85 ± 5.43, LB1 −22.24 ± 3.91 vs Co −7.58 ± 5.32 |
| Hit count note | Results mention "six prioritized hits" but Table 2 scores four (SB1, LB1–LB3) — paper-internal conflict |

## Expected Output

**Format:** `small_molecule_vs_bundle`
**Directory:** `results/task_006/<run>/`

| File | Content |
|---|---|
| `pharmacophore_models.json` | LB + SB hypotheses with feature coordinates |
| `screening_results.csv` | Pharmacophore-screened ranked hits (RMSD ≤ 1.0 Å) |
| `docking_scores.csv` | Vina scores vs −6.80 benchmark |
| `admet_bbb_panel.csv` | SwissADME-equivalent + BBB profiles of finalists |
| `md_analysis.csv` | RMSD/RMSF/H-bond summaries per complex |
| `metrics.json` | Best hit score + MM-GBSA ΔG |

**Pass bar:** ≥1 candidate docking below −6.80 kcal/mol (same-engine Vina anchor — the paper's own co-crystal benchmark) with ≤1 Lipinski violation, BBB permeant, PAINS 0, MM-GBSA below the −8.75 kcal/mol co-crystal reference, and stable 100 ns MD.

## Constraints

- **Time Limit:** 240 minutes of agent working time (long-running platform jobs may complete asynchronously beyond it)
- **Reference Policy:** use the tools and workflow above; do NOT look up the source publication to copy its hit lists or scores
- **Knowledge Cutoff:** not applicable — retrospective paper-anchored task; every required parameter is stated in this document
- **Evaluation Integrity:** freeze candidate selection, scores, and rankings before comparing them against the paper's published reference values

## Important Instructions

- Solve this task using the provided tools and your own reasoning.
- Do NOT search for, reference, or reproduce the source paper's specific hits, scores, or tables — the run is evaluated on completing the workflow and meeting the pass bar, not on matching published values.

## Publication

[Sci Rep (2026)](https://doi.org/10.1038/s41598-026-56505-6). [PMC13396737](https://pmc.ncbi.nlm.nih.gov/articles/PMC13396737/)
