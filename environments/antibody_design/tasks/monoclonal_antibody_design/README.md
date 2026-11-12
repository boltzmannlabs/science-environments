# Monoclonal Antibody Tasks

The task collection covers **23 tasks grouped into seven scientific scenarios**. Classification follows the information supplied at the start and the scientific outcome required. Each task appears once under its primary scenario; molecular format, target and additional constraints remain defined in the task file.

## Tasks by Scientific Scenario

| Scenario | Starting information | Required work | Tasks |
| --- | --- | --- | --- |
| Reference-guided interaction and interface optimization | A supplied antibody sequence or complex and its target. | Generate reference-derived variants and compare sequence/structure compatibility and interface evidence under matched conditions. | [001 — HER2 / trastuzumab](task_001_her2_trastuzumab_interaction_optimization.md); [008 — EGFR scFv](task_008_egfr_scfv_design.md); [009 — TREM2 scFv](task_009_trem2_scfv_design.md) |
| Glycan-aware interface refinement | A supplied scaffold complex, mapped epitope and target glycosylation context. | Refine the modeled interface while evaluating glycan accessibility and interface stability. | [005 — Gal-3BP](task_005_gal3bp_glycan_aware_interface_refinement.md) |
| Framework- and epitope-conditioned candidate generation | A supplied framework or scaffold, target construct and designated binding region. | Generate CDR variants within the protected framework and assess task-specific target engagement, specificity or properties. | [002 — PD-L1 scFv](task_002_pdl1_epitope_targeted_scfv_design.md); [003 — PD-1 paired framework](task_003_pd1_framework_guided_cdr_design.md); [006 — HA / RSV VHH](task_006_vhh_ha_rsv_fixed_framework_design.md) |
| CDR sequence/structure design and reconstruction | Paired framework and antigen context, with the designated CDRs editable or masked. | Generate CDR sequences and conformations; evaluate recovery where a held-out reference exists, plus structural and interface agreement. | [004 — LCAT CDR-H3 reconstruction](task_004_lcat_reference_fab_cdrh3_reconstruction.md); [010 — Epitope-conditioned CDR-H3 design](task_010_chimera_epitope_conditioned_cdr_design.md); [018 — Paired six-CDR co-design](task_018_iggm_paired_cdr_sequence_structure_codesign.md) |
| Reference-backbone-conditioned heavy-chain CDR redesign | A supplied parent antibody–antigen backbone with verified paired chains. | Redesign HCDR3 or HCDR1–3 while preserving protected framework and light-chain identities; assess recovery and structural consistency. | [011 — IL-17A](task_011_il17a_igdesign_cdr_redesign.md); [012 — ACVR2B](task_012_acvr2b_igdesign_cdr_redesign.md); [013 — Complement C5](task_013_c5_igdesign_cdr_redesign.md); [014 — Factor XI](task_014_fxi_igdesign_cdr_redesign.md); [015 — IL-36R](task_015_il36r_igdesign_cdr_redesign.md); [016 — TSLP](task_016_tslp_igdesign_cdr_redesign.md); [017 — TNFRSF9 / 4-1BB](task_017_tnfrsf9_igdesign_cdr_redesign.md) |
| Fixed-backbone, property-focused variant design | A supplied parent sequence, canonical backbone and permitted edit masks. | Generate constrained variants and calculate matched parent/candidate residue-volume, hydrophilicity and charge descriptors. | [007 — huJ3 / gp120 VHH](task_007_huj3_gp120_fixed_framework_design.md) |
| Supplied-panel prediction and ranking | Existing antibody variants, verified parents and the relevant assay or property context. | Score and rank the supplied panel; evaluate against independently held labels after predictions are frozen. | [019 — Affinity ranking](task_019_abbibench_antibody_affinity_ranking.md); [020 — Developability / fitness ranking](task_020_flab_antibody_developability_ranking.md); [021 — Binding-retention prediction](task_021_abdesign_antibody_binding_retention.md); [022 — Binding ΔΔG prediction](task_022_abbind_antibody_binding_ddg_prediction.md); [023 — Interface mutation-effect scoring](task_023_abagym_antibody_interface_mutation_scoring.md) |

Each task has a [matching computational benchmark](../../benchmark/monoclonal_antibody_design/README.md) with the same task identifier.

## Interpreting the Scenarios

- **Reference-guided optimization** starts from the declared parent or complex. Reference-derived candidates require matched comparisons with that starting point.
- **Framework-conditioned generation** uses a scaffold as the design context. A published final design used for evaluation is a separate comparator; for example, H5 and H965 are not substitutes for the stated starting frameworks.
- **Glycan-aware refinement** requires the specified target construct, glycan context and epitope mapping. A modeled scaffold interface does not establish experimentally validated target binding.
- **Reconstruction and co-design** may use native sequences or structures as held-out evaluation references. Preserve each task's conditioning and input-isolation rules.
- **Reference-backbone redesign** preserves the declared framework and paired light chain while changing only the permitted heavy-chain CDR regions.
- **Property-focused design** generates new variants for the explicitly requested descriptors. Favorable descriptor changes alone do not demonstrate improved binding.
- **Panel assessment** evaluates supplied candidates rather than requiring new antibody generation. Affinity, developability, binding retention, binding ΔΔG and mutation-effect endpoints retain separate definitions and label handling.

## Using a Task

Select the scenario that matches the available inputs and intended outcome, then follow the linked task's target identity, editable/protected regions, evaluation requirements and output contract. The grouping does not prescribe a workflow count, tool sequence or universal ranking rule.

The [environment specification](../../ENVIRONMENT_SPEC.md), [source guide](../../src/readme.md) and [results guide](../../results/README.md) describe execution records and scientific outputs. Task availability records a specification, not evidence that its scientific execution is complete.
