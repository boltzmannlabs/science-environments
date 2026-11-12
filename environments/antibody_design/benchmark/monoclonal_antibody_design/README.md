# Monoclonal Antibody Computational Benchmarks

This folder contains computational reference measurements, source provenance and comparison conditions for the monoclonal task collection. Each benchmark uses the same identifier as its task definition. The [task catalog](../../tasks/monoclonal_antibody_design/README.md) groups the collection by scientific starting situation and objective.

## Task and Benchmark Pairs

| ID | Task | Computational reference |
| --- | --- | --- |
| 001 | [HER2 / trastuzumab](../../tasks/monoclonal_antibody_design/task_001_her2_trastuzumab_interaction_optimization.md) | [Benchmark](task_001_her2_trastuzumab_interaction_optimization.md) |
| 002 | [PD-L1 scFv](../../tasks/monoclonal_antibody_design/task_002_pdl1_epitope_targeted_scfv_design.md) | [Benchmark](task_002_pdl1_epitope_targeted_scfv_design.md) |
| 003 | [PD-1 paired framework](../../tasks/monoclonal_antibody_design/task_003_pd1_framework_guided_cdr_design.md) | [Benchmark](task_003_pd1_framework_guided_cdr_design.md) |
| 004 | [LCAT CDR-H3 reconstruction](../../tasks/monoclonal_antibody_design/task_004_lcat_reference_fab_cdrh3_reconstruction.md) | [Benchmark](task_004_lcat_reference_fab_cdrh3_reconstruction.md) |
| 005 | [Gal-3BP](../../tasks/monoclonal_antibody_design/task_005_gal3bp_glycan_aware_interface_refinement.md) | [Benchmark](task_005_gal3bp_glycan_aware_interface_refinement.md) |
| 006 | [HA / RSV VHH](../../tasks/monoclonal_antibody_design/task_006_vhh_ha_rsv_fixed_framework_design.md) | [Benchmark](task_006_vhh_ha_rsv_fixed_framework_design.md) |
| 007 | [huJ3 / gp120 VHH](../../tasks/monoclonal_antibody_design/task_007_huj3_gp120_fixed_framework_design.md) | [Benchmark](task_007_huj3_gp120_fixed_framework_design.md) |
| 008 | [EGFR scFv](../../tasks/monoclonal_antibody_design/task_008_egfr_scfv_design.md) | [Benchmark](task_008_egfr_scfv_design.md) |
| 009 | [TREM2 scFv](../../tasks/monoclonal_antibody_design/task_009_trem2_scfv_design.md) | [Benchmark](task_009_trem2_scfv_design.md) |
| 010 | [Epitope-conditioned CDR-H3 design](../../tasks/monoclonal_antibody_design/task_010_chimera_epitope_conditioned_cdr_design.md) | [Benchmark](task_010_chimera_epitope_conditioned_cdr_design.md) |
| 011 | [IL-17A](../../tasks/monoclonal_antibody_design/task_011_il17a_igdesign_cdr_redesign.md) | [Benchmark](task_011_il17a_igdesign_cdr_redesign.md) |
| 012 | [ACVR2B](../../tasks/monoclonal_antibody_design/task_012_acvr2b_igdesign_cdr_redesign.md) | [Benchmark](task_012_acvr2b_igdesign_cdr_redesign.md) |
| 013 | [Complement C5](../../tasks/monoclonal_antibody_design/task_013_c5_igdesign_cdr_redesign.md) | [Benchmark](task_013_c5_igdesign_cdr_redesign.md) |
| 014 | [Factor XI](../../tasks/monoclonal_antibody_design/task_014_fxi_igdesign_cdr_redesign.md) | [Benchmark](task_014_fxi_igdesign_cdr_redesign.md) |
| 015 | [IL-36R](../../tasks/monoclonal_antibody_design/task_015_il36r_igdesign_cdr_redesign.md) | [Benchmark](task_015_il36r_igdesign_cdr_redesign.md) |
| 016 | [TSLP](../../tasks/monoclonal_antibody_design/task_016_tslp_igdesign_cdr_redesign.md) | [Benchmark](task_016_tslp_igdesign_cdr_redesign.md) |
| 017 | [TNFRSF9 / 4-1BB](../../tasks/monoclonal_antibody_design/task_017_tnfrsf9_igdesign_cdr_redesign.md) | [Benchmark](task_017_tnfrsf9_igdesign_cdr_redesign.md) |
| 018 | [Paired six-CDR co-design](../../tasks/monoclonal_antibody_design/task_018_iggm_paired_cdr_sequence_structure_codesign.md) | [Benchmark](task_018_iggm_paired_cdr_sequence_structure_codesign.md) |
| 019 | [Affinity ranking](../../tasks/monoclonal_antibody_design/task_019_abbibench_antibody_affinity_ranking.md) | [Benchmark](task_019_abbibench_antibody_affinity_ranking.md) |
| 020 | [Developability / fitness ranking](../../tasks/monoclonal_antibody_design/task_020_flab_antibody_developability_ranking.md) | [Benchmark](task_020_flab_antibody_developability_ranking.md) |
| 021 | [Binding-retention prediction](../../tasks/monoclonal_antibody_design/task_021_abdesign_antibody_binding_retention.md) | [Benchmark](task_021_abdesign_antibody_binding_retention.md) |
| 022 | [Binding ΔΔG prediction](../../tasks/monoclonal_antibody_design/task_022_abbind_antibody_binding_ddg_prediction.md) | [Benchmark](task_022_abbind_antibody_binding_ddg_prediction.md) |
| 023 | [Interface mutation-effect scoring](../../tasks/monoclonal_antibody_design/task_023_abagym_antibody_interface_mutation_scoring.md) | [Benchmark](task_023_abagym_antibody_interface_mutation_scoring.md) |

## Reference Use

Use the corresponding source metric, molecular construct, evaluated region, dataset, sampling and aggregation when making a direct comparison. Preserve units, score direction and the distinction between published observations, evaluation thresholds and newly calculated values. Panel-ranking tasks require their declared label and assay context; single-candidate scores do not reproduce dataset-level aggregates.

The [computational metric index](COMPUTATIONAL_BENCHMARKS_INDEX.md) summarizes the source families and pinned releases. The [ProteinBase reference index](PROTEINBASE_SCFV_INDEX.md) identifies the curated EGFR and TREM2 reference cases.

Keep new predictions and comparison outputs under the corresponding `results/` run, with implementation and execution records under `src/`. Published computational references do not establish experimental binding or scientific completion for new candidates.
