# Benchmark: HER2 Reference Antibody Optimization

**Task ID:** `mab_her2_reference_optimization`

**Task:** [HER2 Reference Antibody Optimization](../../tasks/monoclonal_antibody_design/mab_her2_reference_optimization.md)

**Reviewed:** 2026-11-05

## Benchmark Scope

Reference-derived HER2 interaction optimization. The numerical anchors below are individual optimization-run endpoints from released study data.

## Published Results

**Source:** [Ab-SELDON, JCIM (2026)](https://doi.org/10.1021/acs.jcim.5c01924), [supporting information](https://doi.org/10.1021/acs.jcim.5c01924.s001), and [released optimization data](https://doi.org/10.5281/zenodo.15803983).

The following are final trastuzumab/HER2 interaction REF15 scores from the released per-run logs, in **Rosetta energy units (REU)**. Lower scores are favorable within this scoring protocol; they are not measured binding free energies.

| Run | Diversity-guided final REF15 (REU) | Random-arm final REF15 (REU) |
| --- | ---: | ---: |
| 1 | -69.5855 | -71.0480 |
| 2 | -88.0523 | -76.8652 |
| 3 | -66.7028 | -74.5953 |
| 4 | -76.6880 | **-92.6947** |
| 5 | -91.2867 | -82.5258 |
| 6 | **-94.8663** | -79.5079 |
| 7 | -85.5514 | -66.8244 |
| 8 | -91.7997 | -69.9826 |

| Best final result by arm | Initial REF15 | Final REF15 | Final minus initial |
| --- | ---: | ---: | ---: |
| Diversity run 6 | -49.6996 | -94.8663 | -45.1667 |
| Random run 4 | -48.9576 | -92.6947 | -43.7370 |

The best diversity endpoint is `FINAL_001_1n8z-frk-reduced_div6_000024.anarci`; the best random endpoint is `FINAL_001_1n8z-frk-reduced_ran4_000015.anarci`. Initial scores refer to each run's starting structure, not one universal trastuzumab baseline.

Provenance: `ab_seldon_trastuzumab_optimization_tests/her2_test_data/analyses/energy/swap_001_diversityN.log` and `swap_001_randomN.log`, using their final records. The archive's `aligned_energies.csv` differs for some entries, including random run 5 (-80.3354); this table consistently uses the per-run logs.

Candidate-level pLDDT, ipTM, PAE and pDockQ values for these final endpoints have not been verified from the released evidence inspected. Report them as unavailable in the published comparison, not as zero or inferred scores. Benchmark-wide confidence-score performance is not a substitute for these candidate values.

## Evaluation Criteria

| Criterion | Comparison requirement | Acceptance boundary |
| --- | --- | --- |
| Interaction score | Score reference and candidates under identical preparation and score definitions; report candidate minus reference in REU. | Lower is favorable within the matched protocol, but the published best endpoint is not a universal pass threshold. |
| Allowed changes and structure | Verify chain pairing, edit mask, geometry and intended epitope contacts. | A favorable score cannot compensate for a violated design constraint. |
| Published endpoint comparison | Match the exact candidate, run and score provenance before comparing with a released endpoint. | Different scoring conditions must be labelled non-comparable. |

## Reference Trajectories

The source provides optimization logs and endpoint artifacts, not an Agent-Scientist execution trajectory. Use the released log paths above to inspect the reported progression; no new optimization was executed for this document.

## Required Evidence and Availability

Retain the task inputs, reference identity, sequence/structure mappings, candidate records, raw outputs and method revisions. Supply `benchmark_comparison.csv` with metric, published value, new value, units, population/atom scope, source and comparability decision. Missing published values stay unavailable; missing new measurements stay unresolved. Freeze acceptance rules before evaluation. This document defines reference comparisons and does not implement an automatic scientific grader.
