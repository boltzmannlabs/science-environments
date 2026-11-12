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

## Benchmark interpretation

The single-case designs and the 60-case aggregate have different populations and, for several legacy scores, different metric implementations. Their numerical differences do not establish that our design method outperforms or falls below the published method. The later reproduction and candidate evaluations below retain these distinct scopes.

## What we did (real computation, no fabrication)
1. Identified CDR-H3 in 5BV7 heavy chain (C): residues 97–115, sequence `AREGAAVRSFYYSYYGMDV` (19 residues).
2. Designed 20 CDR-H3 variants with ProteinMPNN (v_48_020), fixing all other positions (framework + light chain + antigen).
3. Predicted the top 3 structures with Boltz2 (local GPU, MSA via server).
4. Computed AAR, CAAR (sequence) and CDR-H3 RMSD, TM-score, lDDT (structure, framework-aligned).

## What we did NOT do (integrity)
- The initial design stage evaluated only 5BV7. The later retained benchmark stage reproduced a 60-case baseline, documented below.
- The initial stage did not compute DockQ. Later whole-complex and CDR-H3 evaluations are documented below with separate definitions.
- We did not resolve the paper's RMSD-definition discrepancy (Section 5.2 vs Appendix C); we report Table 1 and Table 2 RMSDs separately.
- The reference is public (5BV7), so this is not a blind benchmark.

## Protocol / comparability
- Alignment: Kabsch on antibody framework Cα (light chain B + heavy chain C minus CDR-H3); CDR-H3 Cα metrics.
- Our design (ProteinMPNN) and prediction (Boltz2) are different methods than the paper's (AbFlow).
- The benchmark is a 60-case aggregate; our result is a single case. Not directly comparable, but we report both.

## Artifacts
- Designed sequences: `results/task_004_lcat_reference_fab_cdrh3_reconstruction/20261111_lcat_cdrh3_multworkflow/designed_sequences.fasta`
- Metrics: metrics.json (this directory)
- Code: src/task_004_lcat_reference_fab_cdrh3_reconstruction/
- Predicted structures: `structures/`


## Canonical package links

- Candidates: `candidates.csv`
- Shortlist: `shortlist.csv`
- Generated inventory: `candidates_all_generated.csv`
- Benchmark table: `benchmark_comparison.csv`
- Source execution: `../../../src/task_004_lcat_reference_fab_cdrh3_reconstruction/runs/20261111_lcat_cdrh3_multworkflow/execution.md`

Packaging did not rerun design, structure prediction or scoring.

## Selection record

The archived selection order is preserved in `shortlist.csv` as `selection_order`. A blank `rank` and `ranking_status=unranked_archived_selection` identify an exported evaluation subset without a newly assigned numerical ranking. Original selection rationale and any prior method-specific priority remain in the source records; no candidates were reranked during packaging.

## Source execution record

- [Execution record](../../../src/task_004_lcat_reference_fab_cdrh3_reconstruction/runs/20261111_lcat_cdrh3_multworkflow/execution.md)
- [Execution provenance](../../../src/task_004_lcat_reference_fab_cdrh3_reconstruction/runs/20261111_lcat_cdrh3_multworkflow/provenance.json)

Task: `task_004_lcat_reference_fab_cdrh3_reconstruction`. Run: `20261111_lcat_cdrh3_multworkflow`.


## Additional reproduced metric: DockQ

The retained AbFlow DockQ implementation was run on the three Boltz2 complexes against deposited 5BV7, using model antibody chains B/C versus antigen chain A, the same chain mapping as the task record. Runtime: Biopython 1.88; DockQ source SHA-256 is recorded in `evidence/dockq_task004.json`.

| Candidate | DockQ | Fnat | iRMS (Å) | LRMS (Å) |
|---|---:|---:|---:|---:|
| task004_sample1 | 0.539 | 0.745 | 1.427 | 11.647 |
| task004_sample6 | 0.506 | 0.800 | 1.473 | 16.516 |
| task004_sample9 | 0.537 | 0.764 | 1.203 | 15.219 |

These scores exceed the AbFlow Table 1 mean DockQ (0.423) and Table 2 full-atom DockQ (0.431) numerically, but the comparison is not like-for-like: the published values are aggregate evaluations, while these are three single-case predicted-complex scores with a deposited reference and a different evaluation scope. They are not evidence of dataset-level improvement.


## Exact AbFlow RAbD benchmark reproduction

The AbFlow H3-specific checkpoint was executed on all 60 RAbD test cases using the downloaded test set, batch size 1, one worker and the RTX 3090. AbFlow's own metric pipeline then calculated AAR, CAAR, RMSD, TM-score, structural lDDT and DockQ sequentially.

| Metric | Published benchmark | Reproduced 60-case result |
|---|---:|---:|
| AAR H3 | 0.4234 ± 0.1334 | 0.4209 ± 0.1306 |
| CAAR H3 | 0.2824 ± 0.2037 | 0.2819 ± 0.1985 |
| TM-score | 0.9736 ± 0.0090 | 0.9736 ± 0.0090 |
| Structural lDDT | 0.8522 ± 0.0216 | 0.8524 ± 0.0218 |
| DockQ | 0.423 ± 0.161 | 0.4240 ± 0.1644 |
| CDR-H3 RMSD | 8.25 ± 4.55 Å / Table 2: 1.83 Å | 8.2629 ± 4.5025 Å |

The reproduced aggregate matches the published AbFlow benchmark closely. This validates the environment, dataset and metric pipeline. It does not mean the current ProteinMPNN+Boltz2 candidates were generated by AbFlow.

## Current 5BV7 candidate comparison under AbFlow metrics

- Structural lDDT: 0.8822–0.8907, above the reproduced aggregate mean.
- Full-antibody TM-score: 0.7759–0.8095, below the reproduced aggregate mean.
- CDR-H3 DockQ: 0.162–0.182, below the reproduced aggregate mean.
- Task-specific AAR/CAAR: 0.4737/0.5714 for all three candidates, above the aggregate means but based on one public 5BV7 case.

The current candidates therefore show higher sequence recovery and structural lDDT but lower full-antibody TM-score and CDR-H3 DockQ than the reproduced 60-case AbFlow baseline. These comparisons are descriptive, not claims of model superiority.

Evidence: `evidence/abflow_rabd_reproduction.json`, `evidence/current_candidates_structural_lddt_tm.json`, `evidence/current_candidates_cdrh3_dockq.json`.


AbFlow's exact CDR-H3 C-alpha RMSD implementation was also applied to the current models: raw (un-Kabsch-aligned) values were 38.241, 39.858 and 33.095 Å for samples 1, 6 and 9; Kabsch-aligned values were 3.336, 3.315 and 3.205 Å. Both scopes are above the reproduced AbFlow 60-case means (8.263 Å raw and 1.647 Å Kabsch-aligned), so the current candidates do not outperform the reproduced structural RMSD baseline.

## Metric-definition correction from retained source

The original 97.81–98.90 values were computed by the custom `lddt()` implementation in `src/shared/metrics.py` over CDR-H3 Cα distances, using thresholds 1.5/5/15 Å and at most eight neighbors. They are **custom local-distance scores**, not standard structural lDDT and not pLDDT. Later raw metadata calls them `task_pLDDT_confidence_0_100`; that inherited label conflicts with the retained implementation. Do not use that label or those values for benchmark comparison. The separately computed AbFlow structural lDDT values (0.8822–0.8907) remain a different endpoint. Original source and raw values are retained for audit.

The archived reference-row text mentions DENV-2, while the task and 5BV7 reference identify LCAT. The source identity reconciliation documents this stale label. All current index descriptions use LCAT; the original row is retained as historical evidence.
