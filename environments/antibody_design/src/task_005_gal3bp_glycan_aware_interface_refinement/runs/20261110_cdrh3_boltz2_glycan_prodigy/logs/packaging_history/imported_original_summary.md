# Task 005 — Gal-3BP: Glycan-Aware Antibody Interface Refinement — Benchmark Result

## Question
Are we better than the published benchmark (Mut1)?

## What we did (complete pipeline)
- **Reference scaffold:** BDBV-43 Fab, sequences verified from PDB 7KEW (chain G = VH, 112 aa; chain J = VL, 106 aa). CDR-H3 = `ARDEIIGADS` (IGHV1-69, FR3 ends `TAIYYC`).
- **Target:** Human Gal-3BP (LGALS3BP), full-length UniProt Q08380 (585 aa).
- **Design:** ProteinMPNN fixed the entire framework + VL and redesigned **only CDR-H3** → 20 designs (17 unique).
- **Structure:** Boltz2 predicted the BDBV-43 reference + top-3 candidates, each with full-length LGALS3BP (model 0).

## Matched-conditions interface metrics (our computation, same target/definition)

Contact definitions: interface residue pair Cα–Cα < 8 Å; vdW atom pair < 4.5 Å; H-bond = N/O heavy-atom pair < 3.5 Å (no explicit H in Boltz2 PDBs).

| Complex | ipTM | pLDDT | Interface residue pairs | vdW atom pairs | H-bonds | H-bond share | Antigen residues |
|---|---:|---:|---:|---:|---:|---:|---:|
| BDBV-43 (reference) | 0.323 | 0.831 | 32 | 281 | 14 | 5.0% | 13 |
| cand11 (`GLYPVPNSQT`) | **0.554** | 0.812 | **59** | 383 | 5 | 1.3% | **21** |
| cand7 (`FLYPRPGSAT`) | 0.306 | 0.820 | 39 | 367 | 12 | 3.3% | 13 |
| cand17 (`GVYPVPLGSS`) | 0.485 | 0.827 | 54 | 499 | 18 | 3.6% | 19 |

**Matched-conditions observation:** the redesigned CDR-H3 candidates cand11 and cand17 show higher interface confidence (ipTM 0.554 / 0.485 vs 0.323) and larger interface extent (59 / 54 vs 32 residue pairs) than the BDBV-43 reference. cand11 is the best candidate.

## Critical caveat (honesty)
- **BDBV-43 is not an experimentally established Gal-3BP binder** — it is an Ebola-GP binder used here as a computational scaffold (as in the published study). All predicted complexes are **low-confidence** (ipTM 0.31–0.55), reflecting this. None of these interfaces should be interpreted as demonstrated binding.
- We used **full-length LGALS3BP (585 aa)**, not the study's specific mature construct.
- We did **not model glycans** explicitly (Boltz2 does not add glycans to LGALS3BP here).

## Comparison with the published benchmark — NOT DIRECTLY REPRODUCIBLE

| Published metric | Value | Why not directly reproducible |
|---|---:|---|
| Reference-complex interactions | 161 | Paper's mature Gal-3BP construct + glycan model + its own interaction analysis. |
| Mut1-complex interactions | 165 | Same study-specific inputs. |
| H-bond share of contacts | ~67% | Same study-specific contact-counting definition + glycan context. |
| Interface RMSD boundary | 5 Å | Requires 3 heated MD replicas per system (not run here). |
| E1 glycan-associated ΔSASA | 2.9 Å² | Requires the study's E1 epitope mapping + glycan model. |
| Mut1 REF15/pLDDT/ipTM/PAE/pDockQ | *Not verified* | No exact individual values established in the benchmark. |

Our matched-conditions numbers (32–59 interface pairs, 1.3–5.0% H-bond share) are from a **different target construct (full-length, unglycosylated) and a different contact definition**, so they are **not directly comparable** to the paper's 161/165/67%. We do not claim our counts match or beat the paper's.

## Verdict
**Cannot make a like-for-like comparison with the published Mut1 benchmark** — it requires the study's mature construct, glycan model, E1 mapping and heated-MD replicas, which are not available. What we *can* state honestly: under our matched full-length/unglycosylated conditions, the redesigned CDR-H3 candidates (especially cand11) improve interface confidence and extent over the BDBV-43 reference scaffold. All interfaces remain low-confidence predictions because BDBV-43 is not an established Gal-3BP binder.

## Artifacts
- Code: src/task_005_gal3bp_glycan_aware_interface_refinement/ (design_cdrh3.py, prepare_struct.py, interface_metrics.py)
- Designs: results/task005_proteinmpnn/seqs/task005_bdbv43_fab.fa
- Boltz2: results/task005_boltz2/ (ref_bdbv43, cand11, cand7, cand17)
- Metrics: results/task005_interface_metrics.json
