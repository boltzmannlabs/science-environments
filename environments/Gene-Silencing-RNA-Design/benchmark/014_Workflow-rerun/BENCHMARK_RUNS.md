# R10 — Executed pretrained workflows and public targets

Run: Run-6_2026-11-16

Config delta versus Run-5: rerun all executable Run-4 efficacy/physical/context workflows; replace cached OligoFormer comparison vectors with actual native paired predictions across all 322 measured pairs and 598 fixed TTR windows. Keep new-model blockers, no-training scope and frozen gates unchanged. No panels reranked or candidates generated.

| Reference | Published value | Run-6 comparison | Classification |
|---|---:|---|---|
| SiaRNA, reported Simone n=322 | AUC 0.7586 | Four executed models/configs evaluated on the public Simone cohort; both >=0.7 and >0.7 rules reported | Different model/input pipeline; exact protocol not reproduced |
| OligoFormer, Mixset inter-dataset average | AUC 0.8163; PCC 0.5879 | Fresh native OligoFormer on Simone | Different cohort/protocol; no superiority delta |
| Sciabola measured target labels | No model-specific AUC target | HIF1A/HPSE/HK2/MYC measured-cohort evaluation | Ground-truth label comparison, not published predictor replay |
| TTR projected drug cores | No per-window potency target | Fresh ranks among 598 windows | Descriptive site recovery only |
| Pfister HTT reporters | IC50 and discrimination ratios | Fresh efficacy/thermodynamic correlations | Reporter evaluation; not allele/CNS design validation |
| Goodchild immune evidence | No validated UGUGU-only sensitivity target | Fresh unchanged rule check on eight retained examples | Descriptive, not immune safety |

Primary citations, exact outputs and cohort/threshold limitations: [REPORT](Run-6_2026-11-16/REPORT.md). All matched-protocol superiority deltas remain unavailable. Earlier registries: [Run-5](../013_Model-upgrade/BENCHMARK_RUNS.md) and [Run-4](../012_Config-sweep/BENCHMARK_RUNS.md). This local registry does not edit historical checksummed indexes.
