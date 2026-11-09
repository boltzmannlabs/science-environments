
**Task ID:** `task_007_kemp_qmmm`

**Task:** [Kemp elimination reaction-surface assessment](../tasks/task_007_kemp_qmmm.md)

## Published Results

**Source:** [Alexandrova et al., *Catalytic Mechanism and Performance of Computationally Designed Enzymes for Kemp Elimination*, JACS 130, 15907–15915 (2008)](https://doi.org/10.1021/ja804040s), Table 1; [full text](https://pmc.ncbi.nlm.nih.gov/articles/PMC2680199/).

| Modeled system | Calculated activation free energy, ΔG‡ |
| --- | --- |
| KE07 | **8.1 kcal mol⁻¹** |
| KE10(V131N) | **13.5 kcal mol⁻¹** |
| KE15 | **12.3 kcal mol⁻¹** |
| KE16 | **Not determined** |

These barriers use PDDG/PM3 QM/MM with Monte Carlo/FEP sampling. Table 1 gives no individual uncertainty intervals. The KE07 discussion separately estimates uncertainty below ±1 kcal mol⁻¹; do not transfer that estimate to the other systems.

## Evaluation Criteria

| Criterion | Comparison requirement | Acceptance boundary |
| --- | --- | --- |
| System identity | Recover each exact designed complex, sequence, mutation list and substrate pose; preserve KE10(V131N). | Neither the parent scaffold nor a crystal structure automatically replaces the original designed enzyme–substrate model. |
| Barrier definition | Measure transition-state free energy relative to the connected reactant basin on the coupled proton-transfer/ring-opening surface. | Static geometry, a single electronic energy or an experimental rate-derived estimate is not the requested activation free energy. |
| Method comparability | Retain QM/MM Hamiltonian, protein/solvent representation, protonation, boundary conditions and sampling. | Direct numerical reproduction requires matching PDDG/PM3 QM/MM with Monte Carlo/FEP assumptions; altered methods are reported separately. |
| Convergence and uncertainty | Report window connectivity/overlap, convergence, independent sampling and uncertainty for each system. | Table 1 provides no per-system intervals. The separate KE07 uncertainty estimate below ±1 kcal mol⁻¹ is not transferred to other systems. |
| Completeness | Report valid profiles and unavailable outcomes with supporting diagnostics. | KE16 has no determined published barrier; retain it as unavailable rather than zero. Published barriers are references, not universal pass/fail cutoffs. |
