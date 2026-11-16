# Monoclonal Antibody Tasks

This directory contains the monoclonal antibody task definitions. Each Markdown file specifies a scientific objective, starting inputs, antibody and target context, design constraints, evaluation endpoints and expected outputs.

## File organization

```text
monoclonal_antibody_design/
├── README.md
└── <task_id>.md
```

Task filenames use a numbered, descriptive identifier. The same identifier names the corresponding folder under `benchmark/monoclonal_antibody_design/` and the related task directories under `configs/`, `src/` and `results/`.

The collection spans reference-guided interaction refinement, framework- and epitope-conditioned generation, CDR reconstruction and co-design, constrained property-focused design and supplied-panel prediction. Each task defines its own molecular format, editable regions, comparison references and metric scope.

## Task catalog

| ID | Task | Benchmark reference |
| --- | --- | --- |
| 001 | [HER2 / trastuzumab interaction optimization](task_001_her2_trastuzumab_interaction_optimization.md) | [reference](../../benchmark/monoclonal_antibody_design/task_001_her2_trastuzumab_interaction_optimization/reference.md) |
| 002 | [PD-L1 epitope-targeted scFv design](task_002_pdl1_epitope_targeted_scfv_design.md) | [reference](../../benchmark/monoclonal_antibody_design/task_002_pdl1_epitope_targeted_scfv_design/reference.md) |
| 003 | [PD-1 framework-guided CDR design](task_003_pd1_framework_guided_cdr_design.md) | [reference](../../benchmark/monoclonal_antibody_design/task_003_pd1_framework_guided_cdr_design/reference.md) |
| 004 | [LCAT reference Fab CDR-H3 reconstruction](task_004_lcat_reference_fab_cdrh3_reconstruction.md) | [reference](../../benchmark/monoclonal_antibody_design/task_004_lcat_reference_fab_cdrh3_reconstruction/reference.md) |
| 005 | [Gal-3BP glycan-aware interface refinement](task_005_gal3bp_glycan_aware_interface_refinement.md) | [reference](../../benchmark/monoclonal_antibody_design/task_005_gal3bp_glycan_aware_interface_refinement/reference.md) |
| 006 | [HA / RSV VHH fixed-framework design](task_006_vhh_ha_rsv_fixed_framework_design.md) | [reference](../../benchmark/monoclonal_antibody_design/task_006_vhh_ha_rsv_fixed_framework_design/reference.md) |
| 007 | [huJ3 / gp120 fixed-framework design](task_007_huj3_gp120_fixed_framework_design.md) | [reference](../../benchmark/monoclonal_antibody_design/task_007_huj3_gp120_fixed_framework_design/reference.md) |
| 008 | [EGFR scFv design](task_008_egfr_scfv_design.md) | [reference](../../benchmark/monoclonal_antibody_design/task_008_egfr_scfv_design/reference.md) |
| 009 | [TREM2 scFv design](task_009_trem2_scfv_design.md) | [reference](../../benchmark/monoclonal_antibody_design/task_009_trem2_scfv_design/reference.md) |
| 010 | [CHIMERA epitope-conditioned CDR design](task_010_chimera_epitope_conditioned_cdr_design.md) | [reference](../../benchmark/monoclonal_antibody_design/task_010_chimera_epitope_conditioned_cdr_design/reference.md) |
| 011 | [IL-17A IgDesign CDR redesign](task_011_il17a_igdesign_cdr_redesign.md) | [reference](../../benchmark/monoclonal_antibody_design/task_011_il17a_igdesign_cdr_redesign/reference.md) |
| 012 | [ACVR2B IgDesign CDR redesign](task_012_acvr2b_igdesign_cdr_redesign.md) | [reference](../../benchmark/monoclonal_antibody_design/task_012_acvr2b_igdesign_cdr_redesign/reference.md) |
| 013 | [Complement C5 IgDesign CDR redesign](task_013_c5_igdesign_cdr_redesign.md) | [reference](../../benchmark/monoclonal_antibody_design/task_013_c5_igdesign_cdr_redesign/reference.md) |
| 014 | [Factor XI IgDesign CDR redesign](task_014_fxi_igdesign_cdr_redesign.md) | [reference](../../benchmark/monoclonal_antibody_design/task_014_fxi_igdesign_cdr_redesign/reference.md) |
| 015 | [IL-36R IgDesign CDR redesign](task_015_il36r_igdesign_cdr_redesign.md) | [reference](../../benchmark/monoclonal_antibody_design/task_015_il36r_igdesign_cdr_redesign/reference.md) |
| 016 | [TSLP IgDesign CDR redesign](task_016_tslp_igdesign_cdr_redesign.md) | [reference](../../benchmark/monoclonal_antibody_design/task_016_tslp_igdesign_cdr_redesign/reference.md) |
| 017 | [TNFRSF9 / 4-1BB IgDesign CDR redesign](task_017_tnfrsf9_igdesign_cdr_redesign.md) | [reference](../../benchmark/monoclonal_antibody_design/task_017_tnfrsf9_igdesign_cdr_redesign/reference.md) |
| 018 | [IgGM paired CDR sequence–structure co-design](task_018_iggm_paired_cdr_sequence_structure_codesign.md) | [reference](../../benchmark/monoclonal_antibody_design/task_018_iggm_paired_cdr_sequence_structure_codesign/reference.md) |
| 019 | [AbBiBench antibody affinity ranking](task_019_abbibench_antibody_affinity_ranking.md) | [reference](../../benchmark/monoclonal_antibody_design/task_019_abbibench_antibody_affinity_ranking/reference.md) |
| 020 | [FLAb antibody developability ranking](task_020_flab_antibody_developability_ranking.md) | [reference](../../benchmark/monoclonal_antibody_design/task_020_flab_antibody_developability_ranking/reference.md) |
| 021 | [AbDesign antibody binding-retention prediction](task_021_abdesign_antibody_binding_retention.md) | [reference](../../benchmark/monoclonal_antibody_design/task_021_abdesign_antibody_binding_retention/reference.md) |
| 022 | [AB-Bind antibody binding ΔΔG prediction](task_022_abbind_antibody_binding_ddg_prediction.md) | [reference](../../benchmark/monoclonal_antibody_design/task_022_abbind_antibody_binding_ddg_prediction/reference.md) |
| 023 | [AbAgym antibody interface mutation scoring](task_023_abagym_antibody_interface_mutation_scoring.md) | [reference](../../benchmark/monoclonal_antibody_design/task_023_abagym_antibody_interface_mutation_scoring/reference.md) |

## Related records

Read the task definition together with its `reference.md` for the scientific requirements and benchmark context. Task-level `comparison.md` documents present calculated results and figures. Per-run methods, prepared inputs and logs are stored under `src/<task_id>/<run_id>/`; scientific configurations and outputs are under `results/<task_id>/<run_id>/`.

The [task guide](../README.md), [source guide](../../src/readme.md) and [results guide](../../results/README.md) explain the shared structure.
