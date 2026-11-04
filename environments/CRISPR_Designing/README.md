# CRISPR Design Environment

This environment describes a reusable, application-aware workflow for designing, evaluating and prioritizing CRISPR candidates across supported editing and gene-regulation tasks.

## Contents

- `ENVIRONMENT_SPEC.md` — environment purpose, supported scope, shared workflow, evaluation stages and output requirements.
- `tasks/crispr_design_gene_knockout_001.md` — gene knockout gRNA design task.
- `tasks/crispr_design_base_editing_002.md` — base-editing guide design task.
- `tasks/crispr_design_crispra_crispri_003.md` — CRISPRa/i guide design task.
- `tasks/crispr_design_paired_guide_deletion_004.md` — paired-guide deletion design task.
- `tasks/crispr_design_cas13_rna_targeting_005.md` — Cas13 RNA-targeting guide design task.
- `tasks/crispr_design_guide_optimization_006.md` — guide optimization and reranking task.
- `tasks/crispr_design_prime_editing_007.md` — prime-editing design task.
- `tasks/crispr_design_multiplex_editing_008.md` — multiplex editing design task.

## Current scope

The environment supports computational CRISPR design and candidate prioritization for gene knockout, base editing, CRISPRa/i, paired-guide deletion, Cas13 RNA targeting, guide optimization, prime editing and multiplex editing.

Each task defines its application-specific inputs, candidate-generation requirements, evaluation criteria and expected outputs. The shared workflow assesses candidate validity, activity or application fit, quality, specificity and relevant contextual evidence before filtering and ranking candidates.

Tool support and evaluation evidence vary by CRISPR system, target, organism and application. Record the selected reference, tool settings, dataset and evidence sources for each run. Missing evidence should not be treated as favorable evidence, and computational predictions should not be interpreted as experimental validation.
