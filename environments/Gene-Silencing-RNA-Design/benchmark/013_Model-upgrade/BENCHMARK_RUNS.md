# R9 — Published pretrained-model upgrades

Run: Run-5_2026-11-16

Config delta versus Run-4: evaluate readiness of SiaRNA and ENsiRNA, inspect the additional BERT-siRNA checkpoint availability, retain the incumbent unless a valid challenger comparison supports promotion. No custom training, synthetic learned features, new generation or changed biological gates.

| Endpoint | Prior run | Run-5 | Difference |
|---|---:|---:|---:|
| Incumbent full Simone AUC (322 pairs) | 0.7021412837 | 0.7021412837 | 0 |
| Incumbent three-target macro AUC | 0.7115189089 | 0.7115189089 | 0 |
| New SiaRNA efficacy metrics | not run | blocked | unavailable, not zero |
| New ENsiRNA efficacy metrics | not run | blocked | unavailable, not zero |

Published references, protocol caveats and exact input/runtime blockers are in [REPORT](Run-5_2026-11-16/REPORT.md). No numerical published-minus-local challenger comparison is permitted without actual comparable predictions.

Earlier registries: [Run-4](../012_Config-sweep/BENCHMARK_RUNS.md) and the checksum-bound [historical root registry](../BENCHMARK_RUNS.md). This is an append-only new group, not an edit of prior run evidence.
