# Benchmark: RML: thermal stability

**Task ID:** `task_002_rml_stability`

**Task:** [RML: thermal stability](../../tasks/task_002_rml_stability.md)

Operator/evaluator reference. Withhold winner identities and outcome tables from design-agent inputs until selections are sealed.

## Published Results

**Source:** [Teng et al., Foods (2024)](https://doi.org/10.3390/foods13244023), [Table 2 and §3.7](https://pmc.ncbi.nlm.nih.gov/articles/PMC11727178/).

Table 2 reports experimental residual-activity half-lives at **50°C**:

| Variant | Half-life (min) | Reported ratio to WT |
| --- | --- | --- |
| WT | 45 | 1 |
| D39M | 46.21 | 1.03 |
| D44L | 33.65 | 0.75 |
| Q119L | 23.5 | 0.52 |
| N120M | 53.73 | 1.19 |
| E230I | 115.52 | 2.57 |
| N264M | 78.77 | 1.75 |
| N120M/E230I | 173.29 | 3.85 |
| E230I/N264M | 182.41 | 4.05 |
| N120M/E230I/N264M | 462 | 10.27 |

Section 3.7 reports p-nitrophenyl laurate docking scores: WT **−5.5**, N120M/E230I/N264M **−5.6 kcal/mol** (computed). Table 1 contains the following computed stability predictions. Its unit headings print `kca/mol` (`kca/mo` for DUET); preserve this source typo and verify intended units before historical scoring.

| Variant | mCSM | SDM | DUET | Epri |
| --- | --- | --- | --- | --- |
| D39M | 0.343 | 0.29 | 0.456 | −4.82 |
| D44L | 0.201 | 1.23 | 0.469 | −0.85 |
| Q119L | 0.32 | 0.29 | 0.819 | −2.06 |
| N120L | 0.066 | 1.52 | 0.463 | −2.84 |
| N120M | 0.491 | 0.85 | 0.684 | −4.86 |
| E230L | 0.324 | 0.69 | 0.755 | −2.47 |
| E230I | 0.324 | 0.54 | 0.751 | −2.83 |
| N264M | 0.531 | 0.55 | 0.745 | −3.10 |

## Evaluation Criteria

| Endpoint | Requirement |
| --- | --- |
| Thermal stability | Match construct, temperature and residual-activity protocol; computed ΔΔG is a separate endpoint. |
| Docking | Match ligand state and scoring protocol; a 0.1 kcal/mol difference alone does not establish catalytic improvement. |
| Source discrepancy | Use Table 2's WT 45 min; the abstract says 46 min. Preserve this discrepancy rather than silently substituting one value. |
| Multiple predictors | Preserve each method's units and favorable sign; do not average incompatible scores. |

Run-version comparisons belong in [comparisions/](comparisions/README.md); original Agent-Scientist outputs belong in [results/](../../results/task_002_rml_stability/v1/README.md). Unavailable run measurements remain pending, never zero.
