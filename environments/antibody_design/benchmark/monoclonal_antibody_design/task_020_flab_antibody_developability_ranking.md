# Benchmark: FLAb: Antibody Developability and Fitness Ranking

**Task ID:** `task_020_flab_antibody_developability_ranking`

**Task:** [FLAb: Antibody Developability and Fitness Ranking](../../tasks/monoclonal_antibody_design/task_020_flab_antibody_developability_ranking.md)

## Published Computational Metrics

**Sources:** [FLAb preprint, 2024](https://doi.org/10.1101/2024.01.13.575504), Supplement A.5/A.15 and Tables 1–6; [FLAb2 preprint, 2025](https://doi.org/10.64898/2025.12.27.696706); repository snapshot [Graylab/FLAb @ `e05e3f013578`](https://github.com/Graylab/FLAb/tree/e05e3f0135783ffb7de412df6a1467e7a0031911).

| Computational endpoint | Source evidence | Comparison scope |
| --- | --- | --- |
| Pearson r | FLAb Supplement Tables 1–2 | Individual model–assay pairs |
| Spearman ρ | FLAb Supplement Tables 3–4 | Individual model–assay pairs |
| Kendall τ | FLAb Supplement Tables 5–6 | Preserve the source tie/implementation convention |

| Published illustrative comparison | Pearson r | Spearman ρ | Kendall τ | Exact scope |
| --- | --- | --- | --- | --- |
| ProGen2-Small perplexity versus clinical anti-drug-antibody response | 0.48 | 0.32 | 0.23 | Original FLAb Figure 1b; raw perplexity versus measured %ADA |

The illustrative values are original FLAb Figure 1b correlations of ProGen2-Small raw perplexity with measured %ADA. Retain this exact model, panel and score orientation for the comparison.

## Evaluation Protocol

- Calculate Pearson r, Spearman ρ and Kendall τ independently for each source assay and model.
- Match the source score sign, tie handling and selected measurement population.
- Report properties and assay contexts separately, with signed correlations and evaluated sample counts.
- Freeze train/validation/test partitions by parent or study for supervised comparisons; score zero-shot tracks under their declared exposure policy.
