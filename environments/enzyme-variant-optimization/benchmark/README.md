# Benchmark comparisons

Each task report contains published predictions, method-labeled comparisons and embedded figures. Open-source recalculations score reported reference variants and our retained candidates under a shared protocol within each panel. Parent identity and calculation details are in the corresponding results folder.

| Task | Report |
|---|---|
| RML stability | [PDF comparison](task_001_rml_stability/comparisions/benchmark_report.pdf) |
| LEH stability | [PDF comparison](task_002_leh_stability/comparisions/benchmark_report.pdf) |
| BLA high-temperature performance | [PDF comparison](task_003_bla_high_temperature/comparisions/benchmark_report.pdf) |
| AtHOL1 substrate expansion | [PDF comparison](task_004_athol1_substrate/comparisions/benchmark_report.pdf) |
| Sun LEH / Pythia reproduction | [PDF comparison](task_005_sun_leh_pythia/comparisions/benchmark_report.pdf) |
| Zhang cellulase and β-glucanase reproduction | [PDF comparison](task_006_zhang_hydrolases/comparisions/benchmark_report.pdf) |

Rebuild from saved data with `python scripts/build_reports.py`. Requires `ReportLab`, `matplotlib` and DejaVu Sans fonts (`fonts-dejavu-core` on Debian/Ubuntu). Report generation does not run predictors.
