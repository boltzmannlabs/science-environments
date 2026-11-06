# Benchmark: LEH: thermal stability

**Task ID:** `task_003_leh_stability`

**Task:** [LEH: thermal stability](../../tasks/task_003_leh_stability.md)

Operator/evaluator reference. Withhold winner identities and outcome tables from design-agent inputs until selections are sealed.

## Published Results

**Source:** [Wijma et al., Protein Engineering, Design and Selection (2014)](https://doi.org/10.1093/protein/gzt061), [Figures 1, 3 and 5 and accompanying text](https://pmc.ncbi.nlm.nih.gov/articles/PMC3893934/).

| Evidence | Reference value | Provenance |
| --- | --- | --- |
| Computed FoldX folding-energy change, T85I | −20 kJ/mol | Figure 1 caption; control-library selection example |
| Computed FoldX folding-energy change, T85V | −14 kJ/mol | Figure 1 caption |
| Experimental T85V apparent melting-temperature increase | +7°C | Figure 3 caption |
| Experimental WT apparent melting temperature | About 50°C | Introduction and Figure 5 |
| Experimental F1 / F2 apparent melting-temperature increases | +34.6 / +35.5°C | Combined-variant results and Figure 5A |

The study screened 64 variants, confirmed 21 stabilizing substitutions/pairs, and combined 10–12 substitutions in final designs. Apparent melting temperatures were assessed by Thermofluor and checked with DSC.

## Evaluation Criteria

| Endpoint | Requirement |
| --- | --- |
| FoldX | Match structural preparation, method/settings, units and mutation mapping. These two single-mutant examples are not global winning energies. |
| Experimental stability | Keep apparent melting temperature separate from predicted folding energy and activity. |
| Design budget | Published F1/F2 exceed this environment's eight-substitution limit; retain as historical context, not directly eligible task solutions. |

Run-version comparisons belong in [comparisions/](comparisions/README.md); original Agent-Scientist outputs belong in [results/](../../results/task_003_leh_stability/v1/README.md). Unavailable run measurements remain pending, never zero.
