# Benchmark: AbBiBench: Antibody Variant Affinity Ranking

**Task ID:** `task_019_abbibench_antibody_affinity_ranking`

**Task:** [AbBiBench: Antibody Variant Affinity Ranking](../../tasks/monoclonal_antibody_design/task_019_abbibench_antibody_affinity_ranking.md)

## Published Computational Metrics

**Source:** [AbBiBench manuscript v3, 3 November 2026](https://arxiv.org/html/2506.04235v3), Sections 1.2 and 3.6; [released data](https://huggingface.co/datasets/AbBibench/Antibody_Binding_Benchmark_Dataset); code snapshot [MSBMI-SAFE/AbBiBench @ `85645eaa9441`](https://github.com/MSBMI-SAFE/AbBiBench/tree/85645eaa94418034ee6ef6e21666b683c142fa02).

| Published comparison | Reported value | Scope |
| --- | --- | --- |
| ProteinMPNN equal-assay mean Spearman ρ | 0.292; bootstrap 95% CI 0.154–0.416 | Full 16-assay v3 evaluation |
| ESM-IF1 equal-assay mean Spearman ρ | 0.278; bootstrap 95% CI 0.144–0.399 | Same full evaluation |
| Fivefold Precision@k | k = 10, 20, 50, 100 | Ten eligible direct-Kd assays; 1mhp excluded in the source |

Spearman values are equal-assay means across the full 16-assay v3 evaluation. Fivefold Precision@k is evaluated on ten eligible direct-Kd assays using k = 10, 20, 50 and 100.

## Evaluation Protocol

- Calculate Spearman correlation between frozen computational scores and harmonized source binding labels within each assay.
- Orient scores consistently and average assay correlations equally.
- For fivefold Precision@k, define a hit by measured Kd ≤ matched-parent Kd / 5 and use the source assay-eligibility rule.
- Report Precision@k with Wilson 95% intervals and Spearman means with the specified bootstrap procedure.
- Match the source revision, selected assays and scored-row population when comparing numerical results.
