# Benchmark: AbDesign: Antibody Mutation Binding-Retention Prediction

**Task ID:** `task_021_abdesign_antibody_binding_retention`

**Task:** [AbDesign: Antibody Mutation Binding-Retention Prediction](../../tasks/monoclonal_antibody_design/task_021_abdesign_antibody_binding_retention.md)

## Published Computational Metrics

**Source:** [AbDesign, mAbs 2025](https://doi.org/10.1080/19420862.2025.2567319), Figures 6–8 and 12, Supplement Tables S1–S5; [data provider](https://naturalantibody.com/ab-design/).

| Computational metric | Reported source result | Scope |
| --- | --- | --- |
| Pearson r | Per-parent and pooled correlations in Figures 6–7 and Supplement Tables S1–S2 | Computational mutation-effect scores versus normalized ELISA ratios |
| Spearman ρ | Per-parent and pooled correlations in Figures 6–7 and Supplement Tables S1–S2 | Same source comparison |
| ML generalization correlation | Approximately 0.0–0.1 in the paper discussion | Method- and structural-preparation-dependent summary |

The paper evaluates DSMBind, Binding-DDG-predictor and RDE-PPI. Its FoldX comparison uses the overlapping nine-parent subset shown in Figure 12 and Supplement Table S5.

## Evaluation Protocol

- Preserve the matched parent complex, mutant sequence and normalized source label.
- Freeze computational predictions before joining evaluation labels.
- Orient mutation scores consistently with the binding-retention endpoint.
- Report per-parent and pooled Pearson/Spearman results separately for each structural-preparation method.
- Compare methods on the same parent/mutant intersection, including the source nine-parent population for FoldX comparisons.
