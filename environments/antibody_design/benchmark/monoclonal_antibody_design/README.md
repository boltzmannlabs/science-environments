# Monoclonal Antibody Benchmarks

Each task has a folder named with its task ID. `reference.md` describes its published reference context, metric definitions and reported values. Folders containing calculated results also provide `comparison.md` with numerical tables, candidate highlights, explanatory text and PNG figures.

## Directory structure

```text
monoclonal_antibody_design/
├── README.md
└── <task_id>/
    ├── reference.md
    ├── comparison.md
    └── figures/
        ├── results_comparison.png
        └── workflow_results.png
```

`comparison.md` groups related run IDs while retaining the comparator, units and sample scope for each endpoint. `results_comparison.png` presents the numerical findings; `workflow_results.png` illustrates how the recorded methods connect to their outputs. Both figures are embedded and explained in the comparison document.

## Reference catalog

| ID | Task | Reference | Calculated comparison |
| --- | --- | --- | --- |
| 001 | [HER2 / trastuzumab interaction optimization](../../tasks/monoclonal_antibody_design/task_001_her2_trastuzumab_interaction_optimization.md) | [reference](task_001_her2_trastuzumab_interaction_optimization/reference.md) | [comparison and figures](task_001_her2_trastuzumab_interaction_optimization/comparison.md) |
| 002 | [PD-L1 epitope-targeted scFv design](../../tasks/monoclonal_antibody_design/task_002_pdl1_epitope_targeted_scfv_design.md) | [reference](task_002_pdl1_epitope_targeted_scfv_design/reference.md) | [comparison and figures](task_002_pdl1_epitope_targeted_scfv_design/comparison.md) |
| 003 | [PD-1 framework-guided CDR design](../../tasks/monoclonal_antibody_design/task_003_pd1_framework_guided_cdr_design.md) | [reference](task_003_pd1_framework_guided_cdr_design/reference.md) | [comparison and figures](task_003_pd1_framework_guided_cdr_design/comparison.md) |
| 004 | [LCAT reference Fab CDR-H3 reconstruction](../../tasks/monoclonal_antibody_design/task_004_lcat_reference_fab_cdrh3_reconstruction.md) | [reference](task_004_lcat_reference_fab_cdrh3_reconstruction/reference.md) | [comparison and figures](task_004_lcat_reference_fab_cdrh3_reconstruction/comparison.md) |
| 005 | [Gal-3BP glycan-aware interface refinement](../../tasks/monoclonal_antibody_design/task_005_gal3bp_glycan_aware_interface_refinement.md) | [reference](task_005_gal3bp_glycan_aware_interface_refinement/reference.md) | [comparison and figures](task_005_gal3bp_glycan_aware_interface_refinement/comparison.md) |
| 006 | [HA / RSV VHH fixed-framework design](../../tasks/monoclonal_antibody_design/task_006_vhh_ha_rsv_fixed_framework_design.md) | [reference](task_006_vhh_ha_rsv_fixed_framework_design/reference.md) |  |
| 007 | [huJ3 / gp120 fixed-framework design](../../tasks/monoclonal_antibody_design/task_007_huj3_gp120_fixed_framework_design.md) | [reference](task_007_huj3_gp120_fixed_framework_design/reference.md) |  |
| 008 | [EGFR scFv design](../../tasks/monoclonal_antibody_design/task_008_egfr_scfv_design.md) | [reference](task_008_egfr_scfv_design/reference.md) |  |
| 009 | [TREM2 scFv design](../../tasks/monoclonal_antibody_design/task_009_trem2_scfv_design.md) | [reference](task_009_trem2_scfv_design/reference.md) |  |
| 010 | [CHIMERA epitope-conditioned CDR design](../../tasks/monoclonal_antibody_design/task_010_chimera_epitope_conditioned_cdr_design.md) | [reference](task_010_chimera_epitope_conditioned_cdr_design/reference.md) |  |
| 011 | [IL-17A IgDesign CDR redesign](../../tasks/monoclonal_antibody_design/task_011_il17a_igdesign_cdr_redesign.md) | [reference](task_011_il17a_igdesign_cdr_redesign/reference.md) |  |
| 012 | [ACVR2B IgDesign CDR redesign](../../tasks/monoclonal_antibody_design/task_012_acvr2b_igdesign_cdr_redesign.md) | [reference](task_012_acvr2b_igdesign_cdr_redesign/reference.md) |  |
| 013 | [Complement C5 IgDesign CDR redesign](../../tasks/monoclonal_antibody_design/task_013_c5_igdesign_cdr_redesign.md) | [reference](task_013_c5_igdesign_cdr_redesign/reference.md) |  |
| 014 | [Factor XI IgDesign CDR redesign](../../tasks/monoclonal_antibody_design/task_014_fxi_igdesign_cdr_redesign.md) | [reference](task_014_fxi_igdesign_cdr_redesign/reference.md) |  |
| 015 | [IL-36R IgDesign CDR redesign](../../tasks/monoclonal_antibody_design/task_015_il36r_igdesign_cdr_redesign.md) | [reference](task_015_il36r_igdesign_cdr_redesign/reference.md) |  |
| 016 | [TSLP IgDesign CDR redesign](../../tasks/monoclonal_antibody_design/task_016_tslp_igdesign_cdr_redesign.md) | [reference](task_016_tslp_igdesign_cdr_redesign/reference.md) |  |
| 017 | [TNFRSF9 / 4-1BB IgDesign CDR redesign](../../tasks/monoclonal_antibody_design/task_017_tnfrsf9_igdesign_cdr_redesign.md) | [reference](task_017_tnfrsf9_igdesign_cdr_redesign/reference.md) |  |
| 018 | [IgGM paired CDR sequence–structure co-design](../../tasks/monoclonal_antibody_design/task_018_iggm_paired_cdr_sequence_structure_codesign.md) | [reference](task_018_iggm_paired_cdr_sequence_structure_codesign/reference.md) |  |
| 019 | [AbBiBench antibody affinity ranking](../../tasks/monoclonal_antibody_design/task_019_abbibench_antibody_affinity_ranking.md) | [reference](task_019_abbibench_antibody_affinity_ranking/reference.md) |  |
| 020 | [FLAb antibody developability ranking](../../tasks/monoclonal_antibody_design/task_020_flab_antibody_developability_ranking.md) | [reference](task_020_flab_antibody_developability_ranking/reference.md) |  |
| 021 | [AbDesign antibody binding-retention prediction](../../tasks/monoclonal_antibody_design/task_021_abdesign_antibody_binding_retention.md) | [reference](task_021_abdesign_antibody_binding_retention/reference.md) |  |
| 022 | [AB-Bind antibody binding ΔΔG prediction](../../tasks/monoclonal_antibody_design/task_022_abbind_antibody_binding_ddg_prediction.md) | [reference](task_022_abbind_antibody_binding_ddg_prediction/reference.md) |  |
| 023 | [AbAgym antibody interface mutation scoring](../../tasks/monoclonal_antibody_design/task_023_abagym_antibody_interface_mutation_scoring.md) | [reference](task_023_abagym_antibody_interface_mutation_scoring/reference.md) |  |

See the [task guide](../../tasks/README.md) for task-definition conventions and the [results guide](../../results/README.md) for per-run reports, metric tables and native scientific outputs.
