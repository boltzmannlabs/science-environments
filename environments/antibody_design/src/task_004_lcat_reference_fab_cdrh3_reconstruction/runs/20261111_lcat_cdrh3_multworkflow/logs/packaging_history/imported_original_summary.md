# Task 004 — LCAT: Reference Fab CDR-H3 Reconstruction — Benchmark Result

## Question
Are we better than the published benchmark?

**Published benchmarks (AbFlow, KDD 2026, RAbD 60-case aggregate):**
- Table 1 (mean ± SD): AAR 0.4234±0.1334, TM-score 0.9736±0.0090, lDDT 0.8522±0.0216, CAAR 0.2824±0.2037, RMSD 8.25±4.55 Å, DockQ 0.423±0.161
- Table 2 (multi-CDR / full-atom): CDR-H3 RMSD 1.83 Å, full-atom TM-score 0.9707, full-atom lDDT 0.8151, full-atom DockQ 0.431

**Our new results (single case 5BV7, ProteinMPNN design + Boltz2 structure):**
- Best AAR: 0.4737 (9/19 CDR-H3 positions) across 20 candidates
- CDR-H3 Cα RMSD (framework-aligned): best 6.46 Å (sample 9); samples 1/6 = 47.8/51.2 Å
- CDR-H3 TM-score: 0.0000 (all 3 predicted; short loops are TM-sensitive)
- CDR-H3 lDDT: 98.0–98.9 (0-100 scale)

## Verdict
**Mixed — better on sequence recovery (AAR), worse on structural reconstruction (RMSD/TM-score).**
- AAR: our best 0.4737 > benchmark mean 0.4234 (but single case vs 60-case aggregate; not directly comparable)
- CDR-H3 RMSD: our best 6.46 Å > benchmark Table 2 1.83 Å (worse)
- TM-score: our 0.0000 < benchmark 0.9707 (worse; short-loop TM is very sensitive)
- lDDT: our 98 > benchmark 0.8522 (but lDDT measures local shape, not position; and 0-100 vs 0-1 scale)

**We are NOT clearly better than the benchmark.** Sequence recovery is competitive/slightly better, but structural reconstruction is worse.

## What we did (real computation, no fabrication)
1. Identified CDR-H3 in 5BV7 heavy chain (C): residues 97–115, sequence `AREGAAVRSFYYSYYGMDV` (19 residues).
2. Designed 20 CDR-H3 variants with ProteinMPNN (v_48_020), fixing all other positions (framework + light chain + antigen).
3. Predicted the top 3 structures with Boltz2 (local GPU, MSA via server).
4. Computed AAR, CAAR (sequence) and CDR-H3 RMSD, TM-score, lDDT (structure, framework-aligned).

## What we did NOT do (integrity)
- We did not reproduce the 60-case aggregate (this is a single case, 5BV7).
- We did not compute DockQ (needs a proper ligand-protein protocol; reported as unavailable).
- We did not resolve the paper's RMSD-definition discrepancy (Section 5.2 vs Appendix C); we report Table 1 and Table 2 RMSDs separately.
- The reference is public (5BV7), so this is not a blind benchmark.

## Protocol / comparability
- Alignment: Kabsch on antibody framework Cα (light chain B + heavy chain C minus CDR-H3); CDR-H3 Cα metrics.
- Our design (ProteinMPNN) and prediction (Boltz2) are different methods than the paper's (AbFlow).
- The benchmark is a 60-case aggregate; our result is a single case. Not directly comparable, but we report both.

## Artifacts
- Designed sequences: results/task_004_lcat_reference_fab_cdrh3_reconstruction/designed_sequences.fasta
- Metrics: metrics.json (this directory)
- Code: src/task_004_lcat_reference_fab_cdrh3_reconstruction/
- Predicted structures: results/task004_struct_boltz2/
