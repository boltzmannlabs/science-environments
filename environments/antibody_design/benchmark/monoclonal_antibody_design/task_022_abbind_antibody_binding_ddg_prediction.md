# Benchmark: AB-Bind: Antibody Binding ΔΔG Prediction

**Task ID:** `task_022_abbind_antibody_binding_ddg_prediction`

**Task:** [AB-Bind: Antibody Binding ΔΔG Prediction](../../tasks/monoclonal_antibody_design/task_022_abbind_antibody_binding_ddg_prediction.md)

## Published Computational Metrics

**Source:** [AB-Bind original study](https://pmc.ncbi.nlm.nih.gov/articles/PMC4815335/) / [DOI](https://doi.org/10.1002/pro.2829), online 2015, Protein Science issue 2016; source data snapshot [sarahsirin/AB-Bind-Database @ `f5af13df8000`](https://github.com/sarahsirin/AB-Bind-Database/tree/f5af13df80000ad9e438a6ccf1147bd5f9d55dba).

| Published comparison | Value | Scope |
| --- | --- | --- |
| FoldX Pearson r | 0.34 | Predicted versus observed ΔΔG in the original study |
| STATIUM ROC-AUC | 0.81 | Source high-effect subset, 527 observations with \|ΔΔG\|>1 kcal/mol |
| FoldX ROC-AUC | 0.87 | Same source high-effect subset |
| Discovery Studio ROC-AUC | 0.88 | Same source high-effect subset |

The source high-effect subset contains 527 observations satisfying |ΔΔG| > 1 kcal/mol. The reported AUCs classify improved versus weakened binding under that subset definition.

## Evaluation Protocol

- Use ΔΔG = ΔG_mutant − ΔG_parent, with negative values indicating improved binding.
- Calculate Pearson r between computational and measured ΔΔG for the matched source rows.
- Calculate ROC-AUC using −predicted ΔΔG as the improvement score and measured ΔΔG < 0 as the positive class.
- Report source effect-size subsets separately, including strict |ΔΔG| > 0.5 and >1 kcal/mol cutoffs.
- Match parent complexes, structural preparation and selected observations for numerical comparisons.
