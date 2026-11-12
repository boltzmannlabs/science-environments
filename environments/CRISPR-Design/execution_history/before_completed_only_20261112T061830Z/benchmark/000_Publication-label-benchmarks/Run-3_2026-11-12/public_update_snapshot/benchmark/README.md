# Benchmark — published anchors + first executed run

**Start here:** [REPORT_2026-11-10_first-runs.md](REPORT_2026-11-10_first-runs.md) —
first-runs report (workflow execution, issues fixed, new-model integration, benchmark
comparison vs published anchors).

**Status:** every anchor number below is **published, source-verified** from the
2026-11-10 curation sweep (primary sources in
[research references](../../../research/CRISPR-Design/references.md); deep tables in the
source workspace `~/IMRAN/NOV26/cirspr-sci-env/02_benchmarks/published_benchmarks.md`).
**Current execution:** measured-label Cas9, Cas13, BE4 efficiency, PRIDICT2.0, DeepPrime and specificity evaluations are recorded in [Run-2_2026-11-12](000_Protocol-reproduction/Run-2_2026-11-12/REPORT.md). Task-specific evidence and missing stages are in the [registry](BENCHMARK_RUNS.md) and [coverage matrix](000_Protocol-reproduction/Run-2_2026-11-12/modality_performance_coverage_matrix.csv). Author-score replays and geometric components remain explicitly distinct from fresh inference and full workflow validation. The earlier [Xiang cohort](001_Xiang2021-clean-evaluation/README.md) is historical; training exposure and treated-label conditions limit its independence. No experimental validation or safety claim follows.

Published anchor ledger:

| Area | Anchor | Dataset / scope | Published headline | Independence |
| --- | --- | --- | --- | --- |
| KO on-target | Kim 2019 (DeepSpCas9) | 12,832 paired sgRNA–target, HEK293T; SRA SRP150719 | CV Spearman up to ~0.77; default transfer-test set | single-lab, paired library |
| KO on-target (variants) | Wang 2019 (DeepHF) | 80,263 pairs WT/eSpCas9(1.1)/SpCas9-HF1; PRJNA522677 | held-out ρ 0.86–0.87 (internal) | single-lab per-variant |
| KO on-target (rules) | DeWeirdt 2022 (RS3) | 46,526 train + 23,629 held-out + 84,609 tiling; PRJNA832308 | RS3 Seq+Target > RS2 (p<0.002) | defined protocol |
| **KO cross-tool** | **Konstantakos 2022** | 6 datasets disjoint from every tool's training | DeepHF/DeepSpCas9 top; DeepCRISPR best on 1/6; ceiling ρ≈0.7 | **independent** |
| KO cross-tool (early) | Haeussler 2016 (CRISPOR) | >19,000 guides, U6 + T7/IVT | all-scores non-training ρ 0.341–0.436; U6 vs T7/IVT split | independent |
| KO screen-level | Lukasiak 2024 (bioRxiv) | 6 public genome-wide libraries | score-based 3-guide libraries match larger ones | independent |
| Off-target datasets | Tsai 2015 (GUIDE-seq); Tsai 2017 (CIRCLE-seq); Cameron 2017 (SITE-seq); Lazzarotto 2020 (CHANGE-seq) | 13 RGNs (cell) · in-vitro · 12/2,047 · **110/201,934** | cell-based vs in-vitro truth layers; SNVs affect ~15.2% of sites | experimental truth |
| **Off-target cross-tool** | **Kaufmann 2026** | 3,827 deep-sequenced sites, 26 combos, 14 tools | recall ≈77% @ top-500; weak score↔indel correlation | **independent** |
| Off-target SOTA | Chuai 2023 (CRISOT) | CHANGE-seq + SITE-seq; Zenodo 8420032 | ROC-AUC >0.984; beats MIT/CFD/CCTop/CROPit/uCRISPR/KinPred (p<0.05) | held-out (license CC BY-NC ⚠) |
| Base editing | Arbab 2020 (BE-Hive) | 38,538 targets, 11 editors | outcome R≈0.9 / efficiency R≈0.7; 3,388 SNVs ≥90% precision | single-platform |
| Base editing (harmonized) | BE-dataHIVE 2024 | 460,000+ combos, 32 editors, 5 studies | fair-comparison substrate | harmonized aggregate |
| Prime editing | Mathis 2023 (PRIDICT1) | 92,423 pegRNAs / 13,349 mutations | ρ 0.85 intended / 0.78 unintended; not a purity metric | multi-context |
| Prime editing | PRIDICT2.0 | Library-Diverse grouped held-out evaluation | intended ρ 0.91 HEK293T / 0.81 K562; reproduced with matching fold assignments | pretraining overlap audit incomplete |
| Prime editing (breadth) | Yu 2023 (DeepPrime) | 338,996 pairs, 8 systems × 7 cell types | breadth standard | multi-system |
| CRISPRi/a | Horlbeck 2016 | K562 tiling + genome-wide γ-scores | compact 5-guide libraries detect >90% essential genes | single-lab |
| Epigenome | Nuñez 2021 (CRISPRoff) | ~116k tiling + 21,378-element screen; GSE168012 | 3 design rules (±500 bp; NDR; CpG density) | single-lab |
| Cas13 | Wessels 2020 (Cas13design); Wessels & Stirn 2023 (TIGER) | 24,460 guides · ~200,000 guides ± mismatches | nt 15–21 intolerance · current reference model | single-lab |
| Diagnostics | Huang 2024 (EasyDesign) | 11,496 validated detections | ρ 0.812; 4 held-out pathogens | single-lab (only large pair) |
| Therapeutic anchors | FDA exa-cel SBRA/BLA; NEJM NTLA-2001/VERVE | strategy-level only | guide "SPY101" redacted (b)(4) — **no public therapeutic guide sequence** | regulatory record |

Validity rules inherited from the siRNA environment (binding for future runs):
pre-registered metrics before label join; gene/cell-line-disjoint splits (the DeepCRISPR
lesson); frozen engines, no post-hoc tuning; blind label joins; bootstrap CIs on every
correlation/AUC; degenerate-n reported as degenerate; weak/negative results published
alongside strong ones; supersession requires a dated note + corrected re-run.
