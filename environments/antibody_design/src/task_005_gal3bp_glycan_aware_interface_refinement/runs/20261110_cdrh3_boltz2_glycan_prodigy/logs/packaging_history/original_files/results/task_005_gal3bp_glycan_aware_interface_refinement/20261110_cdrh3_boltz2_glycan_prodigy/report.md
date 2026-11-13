# Task 005 — Gal-3BP: Glycan-Aware Antibody Interface Refinement — Report

Source execution record: `../../../src/task_005_gal3bp_glycan_aware_interface_refinement/runs/20261110_cdrh3_boltz2_glycan_prodigy/execution.md`

## Structural rationale
BDBV-43 is a human Bundibugyo-virus (Ebola) glycan-cap monoclonal antibody (PDB 7KEW; VH IGHV1, CDR-H3 `ARDEIIGADS`; VL IGKV3 kappa). The published Gal-3BP study selected it as a *computational scaffold* for the glycan-free E1 epitope via 3D-Zernike shape similarity — it is NOT an experimentally established Gal-3BP binder. We therefore treat every predicted BDBV-43/LGALS3BP interface as a low-confidence computational model, not a demonstrated binding complex.

The target is human LGALS3BP (Q08380, 585 aa): signal peptide 1-18, mature 19-585, SRCR 24-124, BTB 153-221, **BACK 260-360** (the E1/E2 region), with N-glycosylation sites at 69, 125, 192, 362, 398, 551, 580. Sites 192 and 362 flank the BACK domain and are the key glycan-occlusion context for E1.

## Design
CDR-H3-only redesign (positions 93-102 in the VH) of the BDBV-43 scaffold, framework + VL + CDR-H1/H2 protected. Three candidates carried forward from the prior ProteinMPNN run (the platform AntiBMPNN job is pending explicit partial-validation approval):
- cand11: CDR-H3 `GLYPVPNSQT`
- cand7: CDR-H3 `FLYPRPGSAT`
- cand17: CDR-H3 `GVYPVPLGSS`

## Numerical analysis (matched conditions)
Boltz2-predicted complexes (BDBV-43 Fab + full-length LGALS3BP). Contact definitions: interface residue pair Cα–Cα < 8 Å; vdW atom pair < 4.5 Å; H-bond = N/O heavy-atom pair < 3.5 Å (heavy-atom PDBs, no explicit H).

| Complex | ipTM | pLDDT | Residue pairs | vdW pairs | H-bonds | H-bond share | Antigen res | Prodigy ΔG | Prodigy Kd | Prodigy IC |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| BDBV-43 (ref) | 0.323 | 0.831 | 32 | 281 | 14 | 5.0% | 13 | -11.2 | 6.1e-09 | 69 |
| cand11 | 0.554 | 0.812 | 59 | 383 | 5 | 1.3% | 21 | -11.1 | 7.3e-09 | 80 |
| cand7 | 0.306 | 0.820 | 39 | 367 | 12 | 3.3% | 13 | -10.8 | 1.2e-08 | 75 |
| cand17 | 0.485 | 0.827 | 54 | 499 | 18 | 3.6% | 19 | -14.5 | 2.3e-11 | 102 |

**Open-source cross-check (Prodigy):** cand17 has the strongest independent binding estimate (ΔG -14.5 kcal/mol, Kd 2.3e-11 M, 102 intermolecular contacts), consistent with its high Boltz2 ipTM and large interface. cand11 has the highest Boltz2 ipTM but a Prodigy ΔG near the reference. Prodigy scores are model estimates, not measurements.

**Glycan-aware analysis:** representative N-glycan (simplified 12-sugar model) at Asn362 (C-terminal flank of BACK). BACK-domain SASA: 48,087.8 Å² (unglycosylated) → 48,053.7 Å² (with glycan); **ΔSASA = 34.2 Å²** (dSASA = SASA_unglyc − SASA_glyc; positive = occlusion). Glycan–antibody clashes (<2.5 Å): 0. The flanking N-glycan occludes a modest BACK-domain surface without clashing the antibody — consistent with the paper's "glycan-free E1" premise. NOT directly comparable to the paper's E1 ΔSASA (2.9 Å²), which is for the smaller specific E1 with a multi-glycan model.

## Benchmark comparison (honesty)
Published anchors: 161 (ref) / 165 (Mut1) unique interactions; ~67% H-bond share; 5 Å interface-RMSD selection boundary (3 heated MD replicas); E1 glycan ΔSASA 2.9 Å²; global glycan SASA reduction ~1,299 Å². These require the study's mature construct, glycan model, E1 mapping, Mut1 sequence, and heated-MD replicas — all unavailable (paper inaccessible). Our matched-conditions numbers use a different construct (full-length unglycosylated) and contact definition, so they are **not directly comparable**. We do not claim our counts match or beat the paper's. See `evidence/benchmark_comparison.csv` for the per-metric comparability table.

## Limitations
- BDBV-43 is not an established Gal-3BP binder; all interfaces are low-confidence predictions (ipTM 0.31-0.55).
- Full-length unglycosylated LGALS3BP used, not the study's mature construct.
- Single simplified glycan model, not the study's conformational-diversity N-glycan ensemble.
- No heated-MD replicas (interface-RMSD 5 Å boundary not reproduced).
- E1 approximated as the whole BACK domain, not the paper's specific E1 residues.
- Computational stability, target binding, and functional inhibition are separate conclusions. Experimental validation is ground truth.

## Artifacts
- `candidates.csv`, `sequences.fasta`, `structures/` (Boltz2 complexes)
- `evidence/workflow_design.md` (5-workflow design + selection)
- `evidence/metrics.json` (consolidated metrics + glycan + Prodigy)
- `evidence/benchmark_comparison.csv` (published vs new, comparability flags)
- `evidence/glycan_aware_analysis.json`, `evidence/prodigy_validation.json`
- `evidence/task005_interface_metrics.json` (Boltz2 + contact metrics)
- `evidence/reference/task005_ref_bdbv43.pdb` (Boltz2 reference complex)
