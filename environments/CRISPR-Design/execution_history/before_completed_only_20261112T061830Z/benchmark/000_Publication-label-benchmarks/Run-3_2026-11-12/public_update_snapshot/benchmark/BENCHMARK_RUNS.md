# BENCHMARK_RUNS — published references vs Run-N iteration registry

## Current registry — Run-2_2026-11-12

The completed model-specific evaluations, author-score replays, component tests and blockers are tabulated below. [Full report](000_Protocol-reproduction/Run-2_2026-11-12/REPORT.md) · [Protocols and validation](000_Protocol-reproduction/Run-2_2026-11-12/WORKFLOWS_AND_VALIDATION.md). No full task, safety or experimental validation is inferred. All 1000 corrected RFcombined fits have independently verified disjoint partitions and numerical metrics.

| Task | Evidence status | Result | Benchmark |
| --- | --- | --- | --- |
| 001 general | SHARED_COMPONENT_BENCHMARKS | [Report](../results/001_general/Run-2_2026-11-12/REPORT.md) | [Evidence](../benchmark/001_general-routing/Run-2_2026-11-12/README.md) |
| 002 knockout_gene_disruption | FRESH_CAS9_COMPONENT_EVALUATION | [Report](../results/002_knockout_gene_disruption/Run-2_2026-11-12/REPORT.md) | [Evidence](../benchmark/002_knockout/Run-2_2026-11-12/README.md) |
| 003 therapeutic_in_vivo_editing | SPECIFICITY_COMPONENT_ONLY | [Report](../results/003_therapeutic_in_vivo_editing/Run-2_2026-11-12/REPORT.md) | [Evidence](../benchmark/003_therapeutic-in-vivo/Run-2_2026-11-12/README.md) |
| 004 variant_correction_precision_repair | MATCHED_MODEL_COMPONENT_EVALUATIONS | [Report](../results/004_variant_correction_precision_repair/Run-2_2026-11-12/REPORT.md) | [Evidence](../benchmark/004_variant-correction/Run-2_2026-11-12/README.md) |
| 005 base_editing | FRESH_BE4_EFFICIENCY_EXTERNAL_TEST | [Report](../results/005_base_editing/Run-2_2026-11-12/REPORT.md) | [Evidence](../benchmark/005_base-editing/Run-2_2026-11-12/README.md) |
| 006 prime_editing | FRESH_MATCHED_HELDOUT_OUTCOME_EVALUATIONS | [Report](../results/006_prime_editing/Run-2_2026-11-12/REPORT.md) | [Evidence](../benchmark/006_prime-editing/Run-2_2026-11-12/README.md) |
| 007 crispr_regulation | CRISPRI_WINDOW_COMPONENT_TEST_ONLY | [Report](../results/007_crispr_regulation/Run-2_2026-11-12/REPORT.md) | [Evidence](../benchmark/007_regulation/Run-2_2026-11-12/README.md) |
| 008 epigenome_editing | BLOCKED_MATCHED_EPIGENETIC_ENDPOINT | [Report](../results/008_epigenome_editing/Run-2_2026-11-12/REPORT.md) | [Evidence](../benchmark/008_epigenome-editing/Run-2_2026-11-12/README.md) |
| 009 rna_targeting_cas13 | COMPLETED_QUALIFIED_RFCOMBINED_REIMPLEMENTATION | [Report](../results/009_rna_targeting_cas13/Run-2_2026-11-12/REPORT.md) | [Evidence](../benchmark/009_rna-targeting-cas13/Run-2_2026-11-12/README.md) |
| 010 diagnostics_pathogen | REVIEW_ONLY_INCOMPLETE_METRIC_REPLAY | [Report](../results/010_diagnostics_pathogen/Run-2_2026-11-12/REPORT.md) | [Evidence](../benchmark/010_diagnostics/Run-2_2026-11-12/README.md) |
| 011 library_screen_design | SHARED_GUIDE_METRICS_NOT_SCREEN_VALIDATION | [Report](../results/011_library_screen_design/Run-2_2026-11-12/REPORT.md) | [Evidence](../benchmark/011_library-screen-design/Run-2_2026-11-12/README.md) |
| 012 plant_genome_editing | PLANT_ASSAY_MATCHED_AUTHOR_SCORE_REPLAY | [Report](../results/012_plant_genome_editing/Run-2_2026-11-12/REPORT.md) | [Evidence](../benchmark/012_plant-editing/Run-2_2026-11-12/README.md) |
| 013 microbial_crispr_design | BACTERIAL_PHENOTYPE_AUTHOR_SCORE_REPLAY | [Report](../results/013_microbial_crispr_design/Run-2_2026-11-12/REPORT.md) | [Evidence](../benchmark/013_microbial/Run-2_2026-11-12/README.md) |

## Historical Run-1 and future-plan record

The older registry below is retained as history; its blanket NOT_EXECUTED statements do not describe the current registry above. Corrections: the Xiang treated cohort was not fully training-exclusion audited; D8/D10 correlation is not a predictor ceiling. The 2023 0.85 intended/0.78 unintended anchor is PRIDICT1, not PRIDICT2.0 or purity. Current DeepPrime/PRIDICT2/BE4 tests have their own matched endpoints and cannot be conflated with these older plans.


Iteration structure: every benchmark row carries **published reference | Run-N
configuration | results**, with future Run slots explicit. **Run-1 of benchmark §1 was
executed 2026-11-10** (Xiang-2021 clean cohort, blind join, bootstrap CIs, no-tuning
attestation); all other slots remain `NOT_EXECUTED` until their phase delivers executed
artifacts.

**Scope note:** `results/002_knockout_gene_disruption/Run1_20261110/` is a **runtime
smoke + regression run** (stack liveness, determinism, anchor regression, off-target
controls) — the executed benchmark against published data is
[001_Xiang2021-clean-evaluation](001_Xiang2021-clean-evaluation/README.md).

## 1. KO on-target clean evaluation (protocol: Konstantakos-2022-style, training-disjoint)

| Stage | Content |
| --- | --- |
| Published reference | CRISPRon internal ρ 0.80 vs Azimuth 0.56 / DeepSpCas9 0.73 / DeepHF 0.74 (Xiang 2021); non-training scores 0.34–0.44 (Haeussler 2016); independent envelope 0.4–0.7 (Konstantakos 2022) |
| **Run-1 (EXECUTED 2026-11-10)** | Xiang-2021 TRAP12K D10+dox (one of Konstantakos's 6 disjoint sets), n=11,461, authoritative paper labels, blind join, bootstrap CIs — [001_Xiang2021-clean-evaluation](001_Xiang2021-clean-evaluation/README.md) |
| **Run-1 results** | **RS3 0.516 [0.500–0.530]** · CRISPRon 0.504 [0.489–0.519] (exposed) · RS1 0.222 · CRISPRater 0.091 — vs **measured assay-noise ceiling 0.615** (D8-vs-D10 replicate); modern endpoints reach 83–84% of ceiling; classical rules degrade on this assay class (consistent with CRISPOR's assay-transfer finding); nDCG@20 degenerate at this n (disclosed) |
| FUTURE slots | Run-2: remaining Konstantakos sets (Labuhn-424 HEL, Shalem, Koike-Yusa, zebrafish) for nDCG@20-appropriate cohorts · Run-3: DeepSpCas9/Azimuth arms after py2.7 envs · Run-4: DeepHF variant arm |

## 2. Off-target pair-scoring (protocol: Kaufmann-2026-style recall@K)

| Stage | Content |
| --- | --- |
| Published reference | Kaufmann 2026: recall ≈77% @ top-500, ≈83% @ top-1,250; weak score↔indel correlation (14 tools) |
| Run-1 configuration | `NOT_EXECUTED` — planned: CFD + Elevation (CRISOT optional, research-internal) on CHANGE-seq 110-guide set; recall@K + PR-AUC; GUIDE-seq as cell-based truth layer |
| Run-1 results | `NOT_EXECUTED` |
| FUTURE slots | Run-2: CRISPRitz bulge-aware arm · Run-3: CRISPRme variant layer |

## 3. Base-editing outcome prediction

| Stage | Content |
| --- | --- |
| Published reference | BE-Hive outcome R≈0.9 / efficiency R≈0.7 (Arbab 2020); BEDICT2.0 R 0.60–0.94 (2025); DeepBE editor-choice gains 2.9–20× (2024) |
| Run-1 configuration | `NOT_EXECUTED` — planned: BEDICT2.0 + DeepBE on BE-dataHIVE held-out editors; intended-fraction + purity metrics |
| Run-1 results | `NOT_EXECUTED` |
| FUTURE slots | Run-2: bystander-model arm (BE-Hive CLI) |

## 4. Prime-editing intended-edit prediction

| Stage | Content |
| --- | --- |
| Published reference | PRIDICT2.0 ρ 0.85 intended / 0.78 purity on 92,423 pegRNAs (Mathis 2023) |
| Run-1 configuration | `NOT_EXECUTED` — planned: self-hosted PRIDICT2.0 CLI on Mathis held-out split; DeepPrime cross-check on shared PE systems (license check first) |
| Run-1 results | `NOT_EXECUTED` |
| FUTURE slots | Run-2: pegRNA design-vs-prediction round trip |

## 5. Application-layer anchors (same-side, later phases)

| Stage | Content |
| --- | --- |
| Published reference | Horlbeck 2016 γ-scores (CRISPRi) · Nuñez 2021 GSE168012 rules (CRISPRoff) · TIGER corpus (Cas13) · EasyDesign ρ 0.812 (diagnostics, contrived targets only) · RS3 tiling 84,609 (libraries) |
| Run-1 configuration | `NOT_EXECUTED` — planned per task after P0/P1 installs |
| Run-1 results | `NOT_EXECUTED` |

## No-tuning attestation (to be recorded at first freeze)

Thresholds, weights and rules will be frozen before evaluation (see
[config/thresholds.v0.1.draft.json](../config/thresholds.v0.1.draft.json)
`no_freeze_without` list); no retrospective outcome may influence any parameter. Until
then, every deliverable carries the DRAFT-gates disclosure.
