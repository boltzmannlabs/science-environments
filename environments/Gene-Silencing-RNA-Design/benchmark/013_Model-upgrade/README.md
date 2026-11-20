# Published pretrained-model upgrade attempts

[Run-5_2026-11-16 report](Run-5_2026-11-16/REPORT.md)

## Published reference

Published-model citations and protocol caveats are curated in the linked report. Published scores are not substituted for local challenger predictions.

## Run configuration

The run is partial: SiaRNA is blocked by author preprocessing/input issues, ENsiRNA by missing verified structural inputs, and the additional BERT-siRNA search found no released fine-tuned checkpoint in its current author repository tree. Published values are curated context, not fabricated local results.

## Benchmark metrics

| Endpoint | Fresh control | Change vs prior |
|---|---:|---:|
| Full Simone AUC | 0.7021412837 | 0 |
| Three-target macro AUC | 0.7115189089 | 0 |
| New challenger efficacy scores | unavailable | not computed |

A real RN.Ai incumbent control replay covers 322 measured pairs and 598 historical TTR windows. No new challenger efficacy score or model promotion is claimed. The user declined custom training.

[Run registry](BENCHMARK_RUNS.md)

This group uses the same task/config/run organization as 012_Config-sweep. Root benchmark/results indexes are checksum-bound by Run-3 and are intentionally not rewritten; this run-local registry records the new attempt without invalidating historical evidence.
