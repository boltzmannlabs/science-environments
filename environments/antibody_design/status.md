# Antibody Design Environment Status

**Maturity:** Specification with retained execution and scientific-result packages; a general scientific executor is not included.

The existing five task/benchmark pairs are unchanged. Their source histories and results are now organized by task/run, with separate scientific-coverage and packaging records.

| Task | Retained evidence | Scientific coverage |
| --- | --- | --- |
| 001 — HER2 / trastuzumab | [Source](src/task_001_her2_trastuzumab_interaction_optimization/README.md) · [Results](results/task_001_her2_trastuzumab_interaction_optimization/20261111_ref15_benchmark_audit/report.md) | Partial. Later audit rejects the old approximate-coordinate improvement claim; exact REF15 remains blocked. |
| 002 — PD-L1 scFv | [Source](src/task_002_pdl1_epitope_targeted_scfv_design/README.md) · [Results](results/task_002_pdl1_epitope_targeted_scfv_design/20261110_rf_antibody_boltz2/report.md) | Partial. Whole-surface fallback; exact sequence/interface novelty comparison remains unresolved. |
| 003 — PD-1 framework CDRs | [Source](src/task_003_pd1_framework_guided_cdr_design/README.md) · [Results](results/task_003_pd1_framework_guided_cdr_design/20261110_local_proteinmpnn_boltz2/report.md) | Partial. Historical CDR-H3 local run; separate platform plan was never submitted; labelled benchmark panels unavailable. |
| 004 — LCAT Fab reconstruction | [Source](src/task_004_lcat_reference_fab_cdrh3_reconstruction/README.md) · [Results](results/task_004_lcat_reference_fab_cdrh3_reconstruction/20261111_lcat_cdrh3_multworkflow/report.md) | Partial. Multiple historical workflow subsets and a retained 60-case baseline; incompatible metric scopes remain separate. |
| 005 — Gal-3BP interface refinement | [Source](src/task_005_gal3bp_glycan_aware_interface_refinement/README.md) · [Results](results/task_005_gal3bp_glycan_aware_interface_refinement/20261110_cdrh3_boltz2_glycan_prodigy/report.md) | Partial. Missing heated MD/developability and study-specific inputs; original glycan SASA unreliable. |

Seven source runs and six result runs are retained. Task 001 includes a separate independent validation; task 003 retains an unsubmitted platform plan without fabricated results. Task 004 retains its historical workflow bundle and additional benchmark evidence without inventing new execution identities.

The existing [task 006](tasks/monoclonal_antibody_design/task_006_vhh_ha_rsv_fixed_framework_design.md), [task 007](tasks/monoclonal_antibody_design/task_007_huj3_gp120_fixed_framework_design.md), their benchmarks and the pre-existing task 006 result report remain unchanged and are outside this transfer.

Packaging validation checks identities, formats, paths, counts and hashes; it does not establish successful task completion or measured binding. No scientific computation, live endpoint discovery or fresh scientific reproduction ran during preparation. External dependency/path requirements and unresolved scientific metrics are documented in the packages.

See the [environment specification](ENVIRONMENT_SPEC.md), [source guide](src/readme.md) and [results guide](results/README.md).
