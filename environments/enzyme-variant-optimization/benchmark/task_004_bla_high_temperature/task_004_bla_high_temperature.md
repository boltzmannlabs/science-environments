# Benchmark: BLA: high-temperature performance

**Task ID:** `task_004_bla_high_temperature`

**Task:** [BLA: high-temperature performance](../../tasks/task_004_bla_high_temperature.md)

Operator/evaluator reference. Withhold winner identities and outcome tables from design-agent inputs until selections are sealed.

## Published Results

**Source:** [Fan et al., Computational and Structural Biotechnology Journal (2024)](https://doi.org/10.1016/j.csbj.2024.02.005), [Table 1, §§2.5–2.6 and 3.2–3.4](https://pmc.ncbi.nlm.nih.gov/articles/PMC10883975/).

All Table 1 thermal endpoints are experimental; reported uncertainties are retained.

| Variant | Tm (°C) | Half-life (s) |
| --- | --- | --- |
| WT | 91.40 ± 0.59 | 285 ± 8.26 |
| K251E | 87.73 ± 0.76 | 182 ± 5.79 |
| E271L | 96.19 ± 0.74 | 315 ± 10.36 |
| E271R | 95.15 ± 0.36 | 330 ± 12.45 |
| E271M | 92.68 ± 0.83 | 289 ± 14.32 |
| E271Q | 95.85 ± 1.24 | 257 ± 12.89 |
| E271T | 90.32 ± 1.28 | 231 ± 9.66 |
| E271V | 94.56 ± 0.57 | 228 ± 10.13 |
| E271I | 93.60 ± 0.94 | 315 ± 9.89 |
| T277C | 74.39 ± 1.04 | 92 ± 6.53 |
| T277I | 95.93 ± 0.85 | 267 ± 12.61 |
| T277V | 90.10 ± 0.69 | 161 ± 7.59 |
| N278K | 94.49 ± 0.91 | 301 ± 13.62 |
| K319W | 96.71 ± 1.18 | 323 ± 13.25 |
| E336S | 95.38 ± 1.37 | 407 ± 14.38 |
| E271L/K319W | 95.43 ± 1.25 | 193 ± 9.37 |
| E271L/N278K | 92.86 ± 0.91 | 139 ± 7.81 |
| E271L/K251E | 95.66 ± 1.04 | 210 ± 13.68 |

Computed screening: 399 substitutions; 14 selected using reported FoldX ΔΔG <−0.85 kJ/mol. This cutoff is not an achieved best score; per-variant Supplementary Table S2 energies have not been re-extracted here.

## Evaluation Criteria

| Issue | Requirement |
| --- | --- |
| Endpoint | K319W has the highest Tm; E336S the longest half-life. Do not interchange these objectives. |
| Conditions | Table 1 says pH 6.0/95°C; §2.5 describes pH 6.5/70°C kinetics and 90°C inactivation; results describe 95°C. Reconcile before numerical historical scoring. DSC uses a temperature ramp (§2.6). |
| Conflicting values | K319W half-life is 323 s in Table 1, 313 s in prose. Use the table with this caveat. |
| Computed scores | Verify original energy units/signs and matched protocol; predicted ΔΔG does not establish measured thermal performance. |

Run-version comparisons belong in [comparisions/](comparisions/README.md); original Agent-Scientist outputs belong in [results/](../../results/task_004_bla_high_temperature/v1/README.md). Unavailable run measurements remain pending, never zero.
