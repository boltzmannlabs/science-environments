# Benchmark and case-study evidence

This folder contains **executed computational benchmarks on public data** (frozen engine `engine-v1.0.0_protocol-v1.0` unless noted), not experimental validation. Original artifacts are copied byte-identical from the source workspace (`~/IMRAN/NOV26/siRNA-Design-Task-Specific`) with hashes in [PROVENANCE.sha256](PROVENANCE.sha256); large artifacts (transcriptome indexes, generator pools, model checkpoints) remain external and referenced.

Start with the case folders:

- [Simone-independent-evaluation](Simone-independent-evaluation/README.md) — clean-cohort predictor validation.
- [TTR-approved-drugs-cohort](TTR-approved-drugs-cohort/README.md) — same-side battery + approved-drug site-rank audit.
- [HIF1AN-case-study](HIF1AN-case-study/README.md) — end-to-end DESIGN run vs public measured data; explorer post-hoc.

Status summary:

- Predictor validation (clean, independent): **RN.Ai AUC 0.7021** / Pearson 0.5074 / Spearman 0.3930 on Simone/Sciabola-322 — the independence gate (`BLOCKED_NO_AUDITABLE_INDEPENDENT_DATASET`) is lifted for the efficacy endpoint, with this as the record.
- Generator validation (clean): OligoFormer **AUC 0.760 / Pearson 0.635** on HIF1AN measured siRNAs; measured-top-10 at **median 97.5th percentile** of the 3,928-window ranking.
- Approved-drug anchors: vutrisiran target site **#62/598**, patisiran **#107/598** in our TTR ranking; all 7 drugs UGUGU-free; efficacy bands coincide with our generated pool.
- Explorer (blind selection, post-hoc labels): 3/18 gate-re-anchored clean candidates measured **0.92/0.92/0.87** (base rate 0.785).
- Biological status: **NOT ESTABLISHED** — no wet-lab measurement exists for any generated candidate; all results tier `NEEDS_EXPERIMENTAL_VALIDATION`.

No-tuning attestation: thresholds, weights and rules were frozen before evaluation; no retrospective outcome influenced any parameter. Known target-level gate saturation (HIF1AN off-target screen) is documented in the case folder and drives backlog #3.
