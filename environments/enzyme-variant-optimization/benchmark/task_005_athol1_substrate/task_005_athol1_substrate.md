# Benchmark: AtHOL1: ethyl iodide activity

**Task ID:** `task_005_athol1_substrate`

**Task:** [AtHOL1: ethyl iodide activity](../../tasks/task_005_athol1_substrate.md)

Operator/evaluator reference. Withhold winner identities and outcome tables from design-agent inputs until selections are sealed.

## Published Results

**Source:** [Shao et al., Chem Catal (2025)](https://doi.org/10.1016/j.checat.2025.101334), [§2e, Figure 8A and Table S2 discussion](https://pmc.ncbi.nlm.nih.gov/articles/PMC12288847/); [released data](https://doi.org/10.5281/zenodo.11188126).

These are **computed** values for AtHOL1 with **ethyl iodide (EtI)**, not measured turnover constants.

| Endpoint | WT | V140T |
| --- | --- | --- |
| Electrostatic transition-state stabilization (kcal/mol), paper convention | −5.6 | −7.8 |
| Projected electric field (MV/cm), reported mean ± spread | −35.2 ± 9.6 | −43.4 ± 5.7 |
| Mean angle between C–I bond and interior electric field | 41.2° | 16.6° |

The paper attributes the stronger projected field to substrate alignment associated with the Thr140–SAH interaction. Figure 8A and the §2e text provide these values; the stabilization comparison is discussed with Table S2.

## Evaluation Criteria

| Endpoint | Requirement |
| --- | --- |
| Electrostatics | Match substrate, SAH state, transition-state definition, field projection/sign, sampling and computational method. Generic docking is a different metric. |
| Activity | Keep electrostatic stabilization separate from experimental catalytic efficiency. Activity increases for n-propyl or other iodides cannot be transferred to EtI. |
| Historical comparison | Rescore WT, reference and selected candidates with a common compatible protocol when original conditions cannot be reproduced. |

Run-version comparisons belong in [comparisions/](comparisions/README.md); original Agent-Scientist outputs belong in [results/](../../results/task_005_athol1_substrate/v1/README.md). Unavailable run measurements remain pending, never zero.
