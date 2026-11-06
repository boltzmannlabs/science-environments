# Task: task_003_pd1_framework_guided_cdr_design

## Description

Design monoclonal antibody candidates against the human PD-1 ligand-binding region using the paired humanized framework in the published tFold example. Compare candidate evidence with the reported anti-PD-1-H965 design and distinguish individual design results from the paper's screening and sequence-recovery benchmarks.

## Target

**Target:** Human PD-1 (PDCD1), extracellular domain\
**Reference Antibody:** Anti-PD-1-H965, a published final-design comparator\
**Starting Framework:** Study-provided humanized IGHV3-23/IGKV1-5 framework, with IGHJ4/IGKJ1 assignments\
**Antibody Format:** Paired heavy/light variable domains in Fab context\
**Objective:** Epitope-directed CDR design compatible with the PD-1 ligand-binding surface

Obtain the actual framework sequences and target construct from the study resources. Germline names alone do not establish the complete input sequences. H965 is not the original parent, and D12 is a sequence comparator rather than a documented design input.

## Design Constraints

- Declare editable CDR regions and allowed loop lengths while protecting the supplied framework and chain pairing.
- Verify the target sequence, structure origin, mature-protein mapping and intended epitope before design.
- Keep H965 and other published designed sequences as comparison controls, separate from newly generated candidates.
- Evaluate candidates in the relevant antigen context. Structural overlap with the ligand-binding region supports a competition hypothesis, not demonstrated functional blockade.
- Freeze candidate selection before inspecting held-out experimental outcomes.

## Evaluation Metrics

| Criterion | Measurements and Evidence | Evaluation Rule |
| --- | --- | --- |
| Sequence validity | CDR boundaries, lengths, framework edits and paired-domain identity | Enforce the declared design constraints. |
| Complex plausibility | Interface confidence, designed-region confidence, epitope contacts and clashes | Report actual scores and uncertain regions for each candidate. |
| Sequence reconstruction | AAR and contact-residue recovery, where native sequences are held out | Use only a declared reconstruction dataset; these are not affinity metrics. |
| Screening quality | AUROC and top-percentile enrichment, if a labelled panel is evaluated | Require the same positive/negative definitions and panel; one candidate cannot yield an AUROC. |
| Novelty and developability | Reference sequence distance and sequence/structure liabilities | Distinguish a new design from a retrieved published antibody. |

Published comparison data: [PD-1: Framework-Guided CDR Design benchmark](../../benchmark/monoclonal_antibody_design/task_003_pd1_framework_guided_cdr_design.md).

## Expected Output

**Format:** Computational antibody design bundle\
**Directory:** `pd1_results/`

- `designed_sequences.fasta`: unique paired heavy/light candidates.
- `metrics.json`: framework identity, permitted changes, candidate scores, provenance and missing evidence.
- `shortlist.csv`: ranked eligible candidates and supporting criteria.
- `benchmark_comparison.csv`: individual, screening-panel and reconstruction results in separate labelled records.
- `report.md`: design rationale, H965 comparison and supported conclusions, with structures and raw outputs.

## Important Instructions

- Choose the design and evaluation methods independently within the user's constraints.
- Do not assign the paper's aggregate scores to H965 or to a new candidate.
- Report `NEEDS_INPUT` if required framework sequences or target annotations cannot be verified.
- Missing candidate-level benchmarks remain unavailable; never infer them from an AUROC or measured affinity.
