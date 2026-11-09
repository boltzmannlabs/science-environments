
**Task ID:** `task_006_kemp_eliminases`

**Task:** [Kemp eliminase substrate retention and reaction profiles](../tasks/task_006_kemp_eliminases.md)

## Published Results

**Source:** [Listov et al., *Complete computational design of high-efficiency Kemp elimination enzymes*, Nature 643, 1421–1427 (2025)](https://doi.org/10.1038/s41586-025-09136-2); [Supplementary Data 2](https://static-content.springer.com/esm/art%3A10.1038%2Fs41586-025-09136-2/MediaObjects/41586_2025_9136_MOESM3_ESM.pdf), Supplementary Tables 2–3, printed pages 2–3.

| Published metric | Des27 | Des27.7 | Scope and interpretation |
| --- | --- | --- | --- |
| Substrate-bound occupancy | **37%** | **88%** | Supplementary Table 2; fraction of total simulation time. |
| IN orientation occupancy | **11%** | **24%** | Supplementary Table 2; conditional on the **reactive proportion**, not all bound frames or total time. |
| OUT orientation occupancy | **66%** | **57%** | Supplementary Table 2; the same reactive-proportion denominator. |
| IN activation free energy, ΔG‡ | **16.6 ± 2.1 kcal mol⁻¹** | **13.2 ± 0.6 kcal mol⁻¹** | Supplementary Table 3; computed EVB means ± standard deviations. |
| OUT activation free energy, ΔG‡ | **17.1 ± 2.4 kcal mol⁻¹** | **15.5 ± 1.5 kcal mol⁻¹** | Supplementary Table 3; computed EVB means ± standard deviations. |

For the orientation denominator, Table 2 defines reactive frames as **9% of total time for Des27** and **21% for Des27.7**. Its IN and OUT percentages therefore cannot be read as unconditional occupancies. The remaining reactive-frame category is outside these two orientations; do not renormalize IN and OUT to sum to 100%.

The activation-energy statistics use **30 independent EVB simulations per enzyme and starting conformation**. The ± values are standard deviations, not standard errors or confidence intervals. A barrier summary does not reconstruct the full reaction profile or its sampled-window data.

## Evaluation Criteria

| Criterion | Comparison requirement | Acceptance boundary |
| --- | --- | --- |
| System identity | Use exact Des27/Des27.7 designed constructs and matching substrate, topology, protonation and simulation conditions. | Starting coordinates alone do not establish retention or an activation free energy; complete production inputs are required. |
| Substrate retention | Match the bound-state predicate and total analyzed-time denominator; retain per-replica values and uncertainty. | 37% and 88% are published Des27 and Des27.7 reference occupancies, not automatic pass thresholds. |
| Productive orientations | Report the reactive fraction of total time and IN/OUT fractions conditional on reactive frames separately. | Do not use all bound frames as the denominator or renormalize IN+OUT to 100%; the published reactive proportions are 9% and 21% of total time. |
| Reaction profiles | Match EVB model/calibration, coordinates, reactant reference and independent sampling for both orientations of both enzymes. | Retain profiles, convergence and replicate counts. A static score, single-point energy or reference barrier summary is not a newly calculated profile. |
| Numerical comparison | Match means, units and uncertainty definitions; preserve protocol changes and sampling shortfalls. | Published barrier ± values are SD over 30 independent simulations per enzyme/orientation, not SEM or confidence intervals. No cross-method numerical pass tolerance is established. |
