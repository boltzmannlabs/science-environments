# Task-specific configuration index

Original root-level examples, schemas and frozen gates are retained. Every task folder has an immutable copy of its original example(s). Tried configs are in `<task>/Run-4_2026-11-16/<config_id>/benchmark_config.json`; execution.json links actual results.

| Task | Executed configs | Scope |
|---|---|---|
| [001_general](001_general/README.md) | 4 | EXECUTED_RETROSPECTIVE_ANALYSIS |
| [002_oncology](002_oncology/README.md) | 4 | EXECUTED_RETROSPECTIVE_ANALYSIS |
| [003_genetic-disease-total-lowering](003_genetic-disease-total-lowering/README.md) | 4 | EXECUTED_DESCRIPTIVE_SENSITIVITY |
| [004_genetic-disease-allele-selective](004_genetic-disease-allele-selective/README.md) | 4 | EXECUTED_DESCRIPTIVE_SENSITIVITY |
| [005_metabolic-liver-galnac](005_metabolic-liver-galnac/README.md) | 0 | SKIPPED_NO_MATCHED_BENCHMARK |
| [006_systemic-lnp](006_systemic-lnp/README.md) | 4 | EXECUTED_DESCRIPTIVE_SENSITIVITY |
| [007_neuro-cns](007_neuro-cns/README.md) | 3 | EXECUTED_DESCRIPTIVE_SENSITIVITY |
| [008_inflammation-immune](008_inflammation-immune/README.md) | 0 | SKIPPED_NO_MATCHED_BENCHMARK |
| [009_functional-genomics](009_functional-genomics/README.md) | 4 | EXECUTED_RETROSPECTIVE_ANALYSIS |
| [010_gene-regulation](010_gene-regulation/README.md) | 4 | EXECUTED_DESCRIPTIVE_SENSITIVITY |
| [011_drug-target-validation](011_drug-target-validation/README.md) | 4 | EXECUTED_RETROSPECTIVE_ANALYSIS |

Sweep report: [REPORT](../benchmark/012_Config-sweep/Run-4_2026-11-16/REPORT.md). Config aliases across application frames are not independent fits. Never edit tried configs; add a new config/run.

## Run-5 — published pretrained-model upgrade assessment

[Report](../benchmark/013_Model-upgrade/Run-5_2026-11-16/REPORT.md). Each task has `Run-5_2026-11-16/workflow.json`. Seven task frames have U00 fresh incumbent-control outputs and U01/U02 configurations that stopped at model readiness gates. Four tasks remain skipped for missing/unsuitable benchmark inputs. No new challenger efficacy score or model promotion is claimed; new research-baseline training was explicitly declined. Run-4 configurations and results remain unchanged.

## Run-6 — actual workflow rerun

[Execution and published-reference report](../benchmark/014_Workflow-rerun/Run-6_2026-11-16/REPORT.md). Thirty-five task/config bundles retain actual outputs and execution records. OligoFormer predictions are freshly computed, not historical-score reuse; no new training or full design completion is claimed.
