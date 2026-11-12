# Benchmark and case-study evidence

This folder contains **executed computational benchmarks on public data** (frozen engine `engine-v1.0.0_protocol-v1.0` unless noted), not experimental validation. Original artifacts are copied byte-identical from the source workspace (`~/IMRAN/NOV26/siRNA-Design-Task-Specific`) with hashes in [PROVENANCE.sha256](PROVENANCE.sha256); large artifacts (transcriptome indexes, generator pools, model checkpoints) remain external and referenced.

**Start here:** [BENCHMARK_RUNS.md](BENCHMARK_RUNS.md) — published references vs run results in the iteration structure (published | Run-N config | Δ vs prior runs; future Run slots included) · [WORKFLOWS_AND_VALIDATION.md](WORKFLOWS_AND_VALIDATION.md) — for every benchmark: the workflow executed, exact tools + license tiers, validation steps undergone, and the manual-vs-sub-agent execution-mode comparison. Case folders follow:

- [000_Simone-independent-evaluation](000_Simone-independent-evaluation/README.md) — clean-cohort predictor validation.
- [003_TTR-approved-drugs-cohort](003_TTR-approved-drugs-cohort/README.md) — same-side battery + approved-drug site-rank audit.
- [005_HIF1A-case-study](005_HIF1A-case-study/README.md) — end-to-end DESIGN run vs public measured data; explorer post-hoc.

Status summary:

- Predictor validation (clean, independent): **RN.Ai AUC 0.7021** / Pearson 0.5074 / Spearman 0.3930 on Simone/Sciabola-322 — the independence gate (`BLOCKED_NO_AUDITABLE_INDEPENDENT_DATASET`) is lifted for the efficacy endpoint, with this as the record.
- Generator validation (clean): OligoFormer **AUC 0.760 / Pearson 0.635** on HIF1A measured siRNAs; measured-top-10 at **median 97.5th percentile** of the 3,928-window ranking.
- Approved-drug anchors: vutrisiran target site **#62/598**, patisiran **#107/598** in our TTR ranking; all 7 drugs UGUGU-free; efficacy bands coincide with our generated pool.
- Explorer (blind selection, post-hoc labels): 3/18 gate-re-anchored clean candidates measured **0.92/0.92/0.87** (base rate 0.785).
- Large-pool head-to-head (v2, definitive): ordering tie at ceiling (manual 0.569 [0.476–0.662] vs sub-agent 0.591 [0.488–0.693]); delivery: sub-agent >= manual on every dimension (seed-distinct 24/24, max off-target 0 vs 1, RN.Ai 86.1 vs 84.4) — [001_HeadToHead-LargePool](001_HeadToHead-LargePool/README.md).
- Biological status: **NOT ESTABLISHED** — no wet-lab measurement exists for any generated candidate; all results tier `NEEDS_EXPERIMENTAL_VALIDATION`.

No-tuning attestation: thresholds, weights and rules were frozen before evaluation; no retrospective outcome influenced any parameter. Known target-level gate saturation (HIF1A off-target screen) is documented in the case folder and drives backlog #3.

**Validity ledger:** the source workspace maintains a master index of every benchmark with valid/superseded status (`~/IMRAN/NOV26/siRNA-Design-Task-Specific/BENCHMARKS.md`). Folders here carry only the retained (valid) evidence; superseded originals stay archived in the source workspace.

## Run-3_2026-11-11 — fresh execution and primary-source audit

See the [campaign report](011_Campaign-reproduction/Run-3_2026-11-11/REPORT.md), [endpoint comparisons](011_Campaign-reproduction/Run-3_2026-11-11/benchmark_comparison.csv), and [task ledger](011_Campaign-reproduction/Run-3_2026-11-11/task_execution_status.csv). New case-specific Run-3 folders link to exact results. This run preserves prior data and frozen gates, reproduces RN.Ai Simone predictions exactly, reproduces the TTR drug-core site ranks with fresh generation, and executes paper-defined HTT reporter evaluations. It does not claim matched-protocol superiority or full application completion.

The source audit independently verifies NM_001530.4 as HIF1A (not HIF1AN), corrects the Goodchild paper mapping to PMID 19630977 in a derived table, and uses PCSK9 RefSeq transcript variant 1 for the new liver/GalNAc frame. Historical artifacts remain unchanged; read their claims alongside the new source-verification and comparability caveats rather than inheriting every historical interpretation.

