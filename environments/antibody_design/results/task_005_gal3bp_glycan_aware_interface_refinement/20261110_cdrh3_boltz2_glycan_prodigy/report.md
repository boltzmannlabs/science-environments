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

**Open-source cross-check (Prodigy 2.4.0):** All four Prodigy ΔG and intermolecular-contact values **reproduce exactly** when re-run with the genuine Prodigy 2.4.0 CLI (`/home/boltzmann10/anaconda3/bin/prodigy`, selection `A,B` vs `C`). cand17 has the strongest independent binding estimate (ΔG -14.5 kcal/mol, Kd 2.3e-11 M, 102 intermolecular contacts), consistent with its high Boltz2 ipTM and large interface. cand11 has the highest Boltz2 ipTM but a Prodigy ΔG near the reference. Prodigy scores are model estimates, not measurements. Reproducibility check: `evidence/raw/prodigy_reproducibility_check.json`.

## Glycan-aware analysis — honest assessment

**SASA algorithm discrepancy (newly identified):** The original custom probe-based SASA implementation (`06_glycan_aware.py`) overestimates absolute SASA by ~10× relative to **BiOTITE 1.4.0** (genuine open-source rolling-ball SASA, probe 1.4 Å, ProtOr radii). BiOTITE gives the unglycosylated antigen SASA = **26,962.7 Å²**, consistent with a 585-residue protein (80.6% of atoms have SASA < 10 Å²). The custom implementation gives 285,172 Å² for the same atoms (~10× too high). Note: the textbook rolling-ball occlusion test (`d < r_probe + r_j`) gives ~0.4× BiOTITE on the same subset, so the discrepancy is not solely the occlusion radius — the custom implementation's probe sampling/radii convention differs from BiOTITE's. BiOTITE is the authoritative cross-check. The previously reported BACK-domain ΔSASA (34.2 Å²) and the global glycan ΔSASA (1,629.5 Å²) were computed with this non-matching implementation and are **not reliable**.

**Global glycan ΔSASA: not reproducible.** Attempting to compute the global glycan-associated SASA reduction with BiOTITE and a simplified N-glycan model (7 sites, attached to Asn side chain) gives **dSASA = 0.0 Å²**: the glycan atoms (5–17 Å from the Asn side-chain attachment) are farther from the antigen than the rolling-probe centers (3.1 Å from the atom), so no probe points are occluded. A realistic multi-conformation N-glycan ensemble (as used in the paper) is required for a meaningful global glycan ΔSASA. The published ~1,299 Å² is **not reproducible** with the available data and tools.

**BACK-domain ΔSASA: uncertain.** The previously reported 34.2 Å² was computed with the buggy custom SASA. A BiOTITE-based recomputation with the simplified glycan model gives dSASA ≈ 0 (same reason as above). The true value requires a realistic glycan ensemble. The 34.2 Å² should be treated as **uncertain / not independently verifiable**.

## Benchmark comparison (honesty)
Published anchors: 161 (ref) / 165 (Mut1) unique interactions; ~67% H-bond share; 5 Å interface-RMSD selection boundary (3 heated MD replicas); E1 glycan ΔSASA 2.9 Å²; global glycan SASA reduction ~1,299 Å². These require the study's mature construct, glycan model, E1 mapping, Mut1 sequence, and heated-MD replicas — all unavailable (paper inaccessible). Our matched-conditions numbers use a different construct (full-length unglycosylated) and contact definition, so they are **not directly comparable**. We do not claim our counts match or beat the paper's.

**Per-metric status:**
| Metric | Status | Tool | Note |
|---|---|---|---|
| Prodigy ΔG / Kd / IC | **Reproducible** | Prodigy 2.4.0 | All 4 values reproduce exactly. |
| Absolute antigen SASA | **Reproducible** | BiOTITE 1.4.0 | 26,962.7 Å² (unglycosylated). |
| Global glycan ΔSASA | **Not reproducible** | BiOTITE 1.4.0 | Simplified glycan model gives dSASA=0; requires multi-conformation ensemble. |
| BACK-domain glycan ΔSASA | **Uncertain** | (buggy custom SASA) | 34.2 Å² computed with a buggy algorithm; not independently verifiable. |
| Interface residue/vdW/H-bond counts | Matched-conditions | Custom (heavy-atom) | Different construct/definition; not like-for-like with the paper. |
| H-bond share | Matched-conditions (proxy) | Custom (N/O <3.5 Å) | No explicit H in Boltz2 PDBs; angle-based criterion not possible. |
| Interface RMSD (5 Å) | **Not reproducible** | (requires heated-MD) | No MD infrastructure, no Mut1, no paper protocol. |
| Mut1 interactions / stability | **Not reproducible** | (Mut1 unavailable) | Mut1 is a paper-only point-mutation variant. |
| E1/E2 specific ΔSASA | **Not reproducible** | (paper's mapping unavailable) | Paper's exact E1/E2 residue mapping is inaccessible. |

## Limitations
- BDBV-43 is not an established Gal-3BP binder; all interfaces are low-confidence predictions (ipTM 0.31-0.55).
- Full-length unglycosylated LGALS3BP used, not the study's mature construct.
- **SASA algorithm bug:** the original custom probe-based SASA overestimates absolute SASA ~5–10× (occlusion test missing `+ r_probe`). BiOTITE 1.4.0 is the authoritative cross-check.
- **Glycan ΔSASA not reproducible:** the simplified glycan model does not occlude the rolling probe (dSASA=0 with BiOTITE). A realistic multi-conformation N-glycan ensemble is required.
- No heated-MD replicas (interface-RMSD 5 Å boundary not reproduced).
- E1 approximated as the whole BACK domain, not the paper's specific E1 residues.
- No explicit H in Boltz2 PDBs; H-bond share is a distance-only proxy.
- Computational stability, target binding, and functional inhibition are separate conclusions. Experimental validation is ground truth.

## Artifacts
- `candidates.csv`, `designed_sequences.fasta`, `structures/` (Boltz2 complexes)
- `../../../src/task_005_gal3bp_glycan_aware_interface_refinement/workflow.md` (5-workflow design + selection)
- `metrics.json` (consolidated metrics + glycan + Prodigy)
- `benchmark_comparison.csv` (published vs new, comparability flags)
- `evidence/raw/prodigy_reproducibility_check.json` (Prodigy 2.4.0 re-run, all 4 match)
- `evidence/raw/biotite_sasa_crossvalidation.json` (BiOTITE 1.4.0 SASA + glycan dSASA=0)
- `evidence/raw/task005_interface_metrics.json` (Boltz2 + contact metrics)
- `evidence/reference/task005_ref_bdbv43.pdb` (Boltz2 reference complex)

## Source execution record
- [Execution record](../../../src/task_005_gal3bp_glycan_aware_interface_refinement/runs/20261110_cdrh3_boltz2_glycan_prodigy/execution.md)
- [Execution provenance](../../../src/task_005_gal3bp_glycan_aware_interface_refinement/runs/20261110_cdrh3_boltz2_glycan_prodigy/provenance.json)

Task: `task_005_gal3bp_glycan_aware_interface_refinement`. Run: `20261110_cdrh3_boltz2_glycan_prodigy`.
