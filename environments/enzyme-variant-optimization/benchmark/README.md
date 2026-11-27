# Benchmark comparisons

These six comparison reports use historical agent-alone runs only. Specialist-assisted runs have separate result records; they are not pooled into the benchmark tables. Each task report contains published predictions, method-labeled comparisons and embedded figures. Open-source recalculations score reported reference variants and our retained candidates under a shared protocol within each panel. Parent identity and calculation details are in the corresponding results folder.

| Task | Report |
|---|---|
| RML stability | [Comparison and figures](evaluation/task_001_rml_stability/comparisons/benchmark_report.md) |
| LEH stability | [Comparison and figures](evaluation/task_002_leh_stability/comparisons/benchmark_report.md) |
| BLA high-temperature performance | [Comparison and figures](evaluation/task_003_bla_high_temperature/comparisons/benchmark_report.md) |
| AtHOL1 substrate expansion | [Comparison and figures](evaluation/task_004_athol1_substrate/comparisons/benchmark_report.md) |
| Sun LEH / Pythia reproduction | [Comparison and figures](evaluation/task_005_sun_leh_pythia/comparisons/benchmark_report.md) |
| Zhang cellulase and β-glucanase reproduction | [Comparison and figures](evaluation/task_006_zhang_hydrolases/comparisons/benchmark_report.md) |

[Benchmark definitions](definitions/README.md) · [Reference data](reference_data/README.md) · [Evaluation records](evaluation/README.md) · [All approaches and run results](../results/README.md)

Rebuild from saved data with `python scripts/build_reports.py`. Requires `matplotlib`. Report generation does not run predictors.
