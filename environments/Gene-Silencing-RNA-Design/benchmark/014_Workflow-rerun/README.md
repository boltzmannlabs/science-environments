# Workflow rerun and published-target comparisons

## Published reference

Primary-source snapshots and evidence-backed citations are curated in [the Run-6 report](Run-6_2026-11-16/REPORT.md). SiaRNA's reported Simone AUC and OligoFormer's reported Mixset averages are contextual references, not automatically comparable protocols. Published measured labels and fixed drug-core sites are evaluated separately.

## Run configuration

Run-6_2026-11-16 reruns the approved installed pretrained backends without training, installs, new generation or relaxed gates. Four efficacy configurations, four RNAduplex settings, three degraded-context controls, and an auxiliary unchanged immune-rule check were executed. OligoFormer uses fresh native paired inference, not cached candidate scores. Native training/dropout behavior is explicitly retained and disclosed.

## Benchmark metrics

| Endpoint | Fresh result | Interpretation |
|---|---:|---|
| RN.Ai source-guide Simone AUC, n=322 | 0.7021 | Previously examined measured cohort |
| RN.Ai core19 Simone AUC, n=322 | 0.7056 | Input projection, not a newly trained model |
| RNAiSpline Simone AUC, n=322 | 0.6769 | Separate native efficacy endpoint |
| Fresh OligoFormer Simone AUC, n=322 | 0.6355 | Native paired inference; not published Mixset protocol |
| Highest observed three-target macro AUC | 0.7203 | Retrospective exploratory result |
| Other-target-selected macro AUC | 0.7102 | Does not improve on baseline 0.7115 |

[Run registry](BENCHMARK_RUNS.md). Task-indexed configs/results retain all attempts. No matched published-protocol superiority, production-default change or complete biological application design is claimed. Historical checksum-bound global indexes are intentionally preserved.
