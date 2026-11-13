# Task 001 — HER2: Trastuzumab Interaction Optimization — Workflow

**Target:** human HER2 (ERBB2) extracellular domain
**Reference:** trastuzumab Fab (PDB 1N8Z; chain A = VL, chain B = VH, chain C = HER2)
**Objective:** reference-guided interaction optimization — improve the predicted
antigen–antibody interaction while retaining the reference binding region, paired
variable domains, framework integrity and acceptable structural quality.

## 1. Candidate workflows compared

| Workflow | Design step | Structure step | Binding step | Strengths | Limitations |
| --- | --- | --- | --- | --- | --- |
| **A (SELECTED)** — AntiBMPNN all-CDR | AntiBMPNN (Boltzmann), structure-conditioned on 1N8Z, all 6 CDRs (H1/H2/H3, L1/L2/L3) | Fixed-pose reconstruction on 1N8Z (backbone preserved, designed CDR side chains) | ProDIGy, Fab(A,B)-vs-HER2(C), matched conditions | Design conditioned on the actual complex (CDRs fit the reference pose); all 6 CDRs = max optimization freedom; fixed pose = cleanest matched-conditions binding comparison; framework/disulfides verified | Side-chain placement is ideal-geometry oriented by the original CA→CB (approximation, not full rotamer optimization); ProDIGy is contact-based (RMSE ~2.6 kcal/mol) |
| **B** — ProteinMPNN CDR-H3 only | ProteinMPNN on 1N8Z, CDR-H3 mask only (historical run) | Boltz2 de novo | Boltz2 VH-HER2 + ProDIGy | Simple, fast | One CDR only (little optimization freedom); Boltz2 de novo VH-HER2 interface is unreliable (reference ipTM 0.245) |
| **C** — De novo random | Random sequence generation | Boltz2 de novo | Boltz2 VH-HER2 + ProDIGy | No starting structure needed | Ignores the reference binding region (violates task constraint); de novo antigen-interface prediction unreliable |

**Selected: Workflow A.** Rationale:
1. The task requires retaining the reference binding region — a structure-conditioned
   design on 1N8Z is the most faithful way to do that.
2. Editing all 6 CDRs (not just H3) gives the optimizer the freedom the benchmark
   (Ab-SELDON, which optimizes the variable domain) uses.
3. Boltz2 de novo prediction of the VH–HER2 interface is unreliable for this system
   (reference ipTM 0.245, ipDE 15.87), so a de novo structure (Workflows B/C) is a
   poor basis for a matched-conditions binding comparison. The fixed-pose
   reconstruction keeps HER2 and the Fab backbone identical to the reference — the
   closest open-source analogue to the benchmark's fixed-pose REF15 protocol.
4. Workflow B (ProteinMPNN CDR-H3) was executed earlier in this repo as a historical
   run (see `code/retained_root_scripts/design_cdrh3.py` and `evidence/historical_proteinmpnn_cdrh3/`); it is
   retained as a comparison control, not the primary result.

## 2. Pipeline (as executed)

| # | Step | Tool | Input | Output | Code |
| --- | --- | --- | --- | --- | --- |
| 0 | Verify chain mapping | Biopython | 1N8Z PDB + candidate sequences | 1:1 position→residue map (VH pos i = chain-B res i; VL pos i = chain-A res i) | `code/00_verify_chain_mapping.py` |
| 1 | Candidate generation | **AntiBMPNN** (Boltzmann NodeAPI) | 1N8Z complex PDB, chains A+B, CDR masks | 20 paired VH/VL designs | Boltzmann job (see SOURCES.md) |
| 2 | Sequence-level filtering | Python | 20 designs + reference sequences | framework + disulfide integrity, CDR-edit counts | `code/01_filter_designs.py` |
| 3 | Shortlist selection | Python | filtered designs + AntiBMPNN scores | 5 diverse candidates (AB_13, AB_05, AB_20, AB_08, AB_04) | `code/02_select_shortlist.py` |
| 4 | Structure prediction | **Boltz2** (Boltzmann NodeAPI) | VH+VL+HER2 payloads (ref + 5) | reference VH-VL (ipTM 0.955) + VH-HER2 (ipTM 0.245); candidate jobs submitted, downloads failed (300 s TTL) | `code/03_boltz2_payloads.py` |
| 5 | Property prediction | **Antibody_Prediction** (Boltzmann NodeAPI) | ref + 5 paired sequences | ThermalStab (ProtBert + ESM) and solubility | Boltzmann job (see SOURCES.md) |
| 6 | Fixed-pose reconstruction | Biopython + ideal side-chain geometry | 1N8Z PDB + candidate CDR edits | 5 fixed-pose complexes (backbone preserved, designed CDR side chains) | `code/04_reconstruct_fixed_pose.py` |
| 7 | Binding metric | **ProDIGy** (open-source) | reconstructed complexes + 1N8Z | ΔG (kcal/mol), KD, intermolecular contacts | `code/06_run_prodigy.sh` |
| 8 | Clash analysis | Biopython (custom) | reconstructed complexes + 1N8Z | same-chain non-adjacent clash counts (vdW − 1.5 Å) | `code/05_compute_clashes.py` |
| 9 | Results assembly | Python | all metrics above | `results/task_001_.../` bundle | `code/07_assemble_results.py` |
| 10 | Task-spec bundle | Python | all metrics above | `her2_results/` bundle (designed_sequences.fasta, metrics.json, shortlist.csv, benchmark_comparison.csv, report.md) | `code/08_make_her2_bundle.py` |

Execution order was sequential (single RTX 3090; no GPU contention — ProDIGy/
Biopython are CPU; Boltzmann jobs ran on the platform).

## 3. Evaluation criteria (consistent across reference and candidates)

- **Reference preservation:** paired-chain identity, CDR edit counts, protected-position
  changes → reject changes outside the declared design scope (all 20 passed).
- **Interaction improvement:** reference and candidate ΔG on the identical HER2
  construct and preparation (fixed 1N8Z pose); report candidate − reference.
- **Structural quality:** clashes, interface contacts (ProDIGy IC count); Boltz2
  confidence for the de novo reference prediction.
- **Binding-region retention:** same HER2 chain and pose as 1N8Z (fixed-pose by
  construction); epitope contacts reported via IC count.
- **Candidate quality:** Antibody_Prediction stability/solubility, CDR-edit diversity,
  AntiBMPNN score.

## 4. Results

| candidate | ProDIGy ΔG (kcal/mol) | Δ vs ref | KD (M) | IC | clashes | TS ProtBert |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| REF_1N8Z | −9.9 | — | 5.6e-8 | 61 | 26 | 49.55 |
| **AB_13 (best)** | **−10.9** | **−1.0** | **9.4e-9** | 68 | 27 | **52.41** |
| AB_05 | −9.9 | 0.0 | 5.7e-8 | 65 | 38 | 49.70 |
| AB_20 | −9.9 | 0.0 | 5.9e-8 | 67 | 26 | 50.04 |
| AB_08 | −9.8 | +0.1 | 6.3e-8 | 69 | 26 | 50.04 |
| AB_04 | −9.6 | +0.3 | 9.6e-8 | 60 | 26 | 49.10 |

**Best: AB_13** — 1.0 kcal/mol binding improvement, ~6× lower KD, best thermal
stability, +1 clash. A 1.0 kcal/mol delta is within ProDIGy's ~2.6 kcal/mol RMSE;
treat as directional, not definitive.

## 5. Benchmark comparison (integrity)

The published benchmark metric is **REF15 (Rosetta REU)** from Ab-SELDON (JCIM 2026):
best diversity endpoint −94.8663 REU (run 6), best random −92.6947 REU (run 4).
Rosetta is not available in this environment, so **REF15 was not computed and not
fabricated**. ProDIGy (kcal/mol, contact-based) is a **different scoring protocol →
NON-COMPARABLE** to REF15. Published values are reported as controls only
(`results/.../evidence/benchmark_comparison.csv`).

## 6. Status

- **Completed:** AntiBMPNN design (20), sequence filtering, shortlisting,
  Antibody_Prediction properties, Boltz2 reference prediction, fixed-pose
  reconstruction (5), ProDIGy binding (ref + 5), clash analysis, results/bundle
  assembly.
- **Failed:** Boltz2 candidate structure downloads (300 s signed-URL TTL exceeded
  inter-call latency).
- **Pending:** REF15 (Rosetta unavailable), Boltz2 candidate structures, full rotamer
  optimization of reconstructed CDRs.
