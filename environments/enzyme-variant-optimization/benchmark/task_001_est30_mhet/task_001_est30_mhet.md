# Benchmark: Est30: MHET hydrolysis

**Task ID:** `task_001_est30_mhet`

**Task:** [Est30: MHET hydrolysis](../../tasks/task_001_est30_mhet.md)

Operator/evaluator reference. Withhold winner identities and outcome tables from design-agent inputs until selections are sealed.

## Published Results

**Source:** [Zhang et al., Communications Biology (2023)](https://doi.org/10.1038/s42003-023-05523-5), [Table 1 and footnotes](https://pmc.ncbi.nlm.nih.gov/articles/PMC10636135/#Tab1).

All six Table 1 endpoints are retained below; “—” is unreported, not zero. Energy columns are computed variant-minus-parent differences; efficiency and melting temperature are experimental.

| Variant | Substitutions | ΔΔGbind (kcal/mol) | ΔΔGfold (kcal/mol) | Distance fraction | kcat/Km (mM⁻¹ s⁻¹) | Tm (°C) |
| --- | --- | --- | --- | --- | --- | --- |
| WT | —— | —— | —— | 11.66% | 0.13 | 74.07 ± 0.14 |
| M1 | G130L | 4.00 | −14.31 | 15.45% | 0.55 | 76.39 ± 0.36 |
| M2 | I171K | −5.55 | 4.85 | 24.87% | 0.67 | 65.08 ± 0.33 |
| M8 | I171K/G130L | −0.08 | −12.01 | 55.01% | 4.70 | 67.58 ± 0.13 |
| M13 | I171K/G130F/M127S | −14.98 | 6.24 | 48.06% | 8.11 | 63.29 ± 0.23 |
| M14 | I171K/G130L/M127S | −8.01 | −3.43 | 34.45% | 12.58 | 63.18 ± 0.20 |

Distance fraction means nucleophilic-attack distance <3.0 Å during 5 ns MD. Kinetics used MHET, 50°C, pH 7.5, 50 mM sodium phosphate, 0.5 μM enzyme, 10 minutes, triplicate. DSC used 0.5–1.0 mg/mL enzyme in that buffer, 30–120°C; two measurements.

## Evaluation Criteria

| Endpoint | Requirement |
| --- | --- |
| Computed energy | Match preparation, scoring method and sign convention. |
| Catalytic occupancy | Match atom definition and trajectory protocol; static docking is insufficient. |
| Activity/stability tradeoff | M14 has higher efficiency than M13; M8 retains higher Tm. Choose the task endpoint before scoring. Predictions cannot establish measured activity. |

Run-version comparisons belong in [comparisions/](comparisions/README.md); original Agent-Scientist outputs belong in [results/](../../results/task_001_est30_mhet/v1/README.md). Unavailable run measurements remain pending, never zero.
