# Task 002 — PD-L1: Epitope-Targeted scFv Design — Benchmark Result

## Question
Are we better than the published benchmark?

**Published benchmark (the only one we compare to):**
- H5 predicted-vs-experimental global Cα RMSD = **1.25 Å** (Germinal, Nat. Biotechnol. 2026; individual PD-L1/H5 complex vs cryo-EM coordinates PDB 35TL).

**Our new result (independent Boltz-2 prediction):**
- H5 antibody Cα RMSD vs 35TL = **14.94 Å** (VH 19.11 Å, VL 8.23 Å; whole-complex Cα RMSD 12.72 Å).
- Boltz-2 confidence: pTM 0.944, ipTM 0.926, complex pLDDT 0.955, complex pDE 0.368.

## Verdict
**No — we are NOT better than the benchmark on the primary individual structural metric.**
Boltz-2 predicts a confident PD-L1/H5 interface (ipTM 0.926) and the antibody is bound at a comparable distance (min Cα 5.1–5.4 Å vs experimental 5.9–6.0 Å), but the predicted pose/arrangement differs substantially from the cryo-EM structure (14.94 Å vs 1.25 Å). This is an honest, reproducible negative result, not a failure to run the benchmark.

## What we did (real computation, no fabrication)
1. Extracted the H5 (VH chain B, VL chain C) and PD-L1 (chain A) sequences from PDB 35TL.
2. Predicted the H5+PD-L1 complex with Boltz-2 (local GPU run, MSA via server, 3 recycling steps).
3. Aligned the prediction on PD-L1 (chain A) Cα (Kabsch) and computed the position-matched Cα RMSD of the H5 antibody and the whole complex.
4. Compared to the single published individual value (1.25 Å).

## What we did NOT do (integrity)
- We did not reproduce the paper's campaign counts (470 passing filters, 48 selected) — those are campaign yields, not per-candidate metrics.
- We did not reproduce the paper's novelty analysis (CDR identity ~40%, IS ≤ 0.2) — those require the paper's specific databases and definitions, which we did not have.
- We did not assign the paper's "not verified" candidate-level pLDDT/ipTM/PAE/pDockQ values to our run.
- The 1.25 Å is the principal individual structural benchmark; we compared to it and only it.

## Protocol / comparability
- Alignment: Kabsch on PD-L1 (chain A) Cα; position-matched Cα RMSD of H5 (B+C).
- Our predictor (Boltz-2) is a different method than the paper's, so this is an independent prediction against the same experimental reference — a fair comparison of structural agreement.
- The benchmark's 1.25 Å is not a universal acceptance threshold; it is the paper's result. Our result is worse on this metric.

## Artifacts
- Predicted structure: results/task_002_boltz2_local/.../task002_h5_pdl1_model_0.pdb
- Metrics: metrics.json (this directory)
- Code: src/task_002_pdl1_epitope_targeted_scfv_design/

## Note on new scFv candidates
The task asks for new scFv candidates using the study's *starting* framework (not H5). The Germinal paper's starting framework is not in PDB 35TL (which is the final H5). We did not silently substitute H5 as the parent. The H5 reconstruction above is the reproducible individual benchmark; new-candidate generation requires the study's starting framework, which we report as NEEDS_INPUT rather than fabricating.
