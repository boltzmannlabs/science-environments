# CRISPR Design Environment Specification

**Version:** 1.0  
**Scope:** Computational CRISPR design, evaluation, benchmarking, and reporting  
**Basis:** Application task specifications created for this environment

## 1. Purpose

This environment supports application-aware CRISPR design through one shared execution contract and task-specific requirements. It must preserve traceability from the confirmed target and reference through candidate generation, evidence collection, gates, ranking, and reporting.

All outputs are computational predictions. They must not be presented as experimentally demonstrated editing, knockout, activation, repression, knockdown, deletion, or phenotype.

## 2. Supported Tasks

| Task ID | Application | Design focus |
|---|---|---|
| `crispr_design_gene_knockout_001` | Gene knockout | Coding-region guides, transcript/exon coverage, predicted coding consequence |
| `crispr_design_base_editing_002` | Base editing | Desired nucleotide change, editor-window compatibility, bystander inventory |
| `crispr_design_crispra_crispri_003` | CRISPRa / CRISPRi | Effector-specific guide placement relative to transcript/TSS and promoter |
| `crispr_design_paired_guide_deletion_004` | Paired-guide deletion | Guide pairs flanking an interval, geometry, predicted boundaries |
| `crispr_design_cas13_rna_targeting_005` | Cas13 RNA targeting | Transcript targeting, isoform coverage, transcriptome matches |
| `crispr_design_guide_optimization_006` | Guide optimization/reranking | Constraint-preserving optimization of a supplied candidate set |
| `crispr_design_prime_editing_007` | Prime editing | Edit encoding and traceable pegRNA spacer/PBS/RTT components |
| `crispr_design_multiplex_editing_008` | Multiplex editing | Guide-set coverage, set-level specificity, diversity and compatibility |

The task selected by the request defines its application-specific evidence and deliverables. Those requirements extend—but do not replace—the shared contract below.

## 3. Shared Design Principles

- Resolve the task, target, mode, reference, and relevant nuclease/editor/effector before design. Do not silently assume missing essentials.
- Verify reference assembly, sequence, annotation/transcript version, coordinates, strand, and allele where applicable.
- Record tool, model, database, and configuration versions.
- Keep evidence dimensions separately visible. Composite scores must be explainable and reproducible.
- Apply frozen hard gates before ranking. Ranking cannot rescue a gate failure.
- Preserve input candidates, generated candidates, candidate identifiers, transformations, and lineage.
- Mark unavailable evidence as unavailable—not as a favorable value.
- Clearly distinguish predictions, published evidence, measured benchmark outcomes, and unsupported claims.

## 4. Shared Run Contract

Every run must create a fresh run directory and follow this lifecycle:

| Stage | Required action | Record/output |
|---|---|---|
| 1. Route and brief | Identify task; confirm objective, target, mode, and required constraints | `confirmed_brief.json` |
| 2. Reference validation | Verify reference identifiers, versions, sequence/coordinates, and relevant annotation | `reference_validation.json` |
| 3. Application preparation | Prepare task-specific windows, transcript/variant/interval/coverage rules | `application_readiness.json` |
| 4. Candidate generation | Run configured generator; preserve provenance and candidate lineage | `candidate_pool.csv` |
| 5. E1 — validity | Validate sequence format, guide length, PAM/system compatibility, and coordinate mapping | `validation_evidence.csv` |
| 6. E2 — activity/fit | Assess task-relevant activity or compatibility | `activity_evidence.csv` |
| 7. E3 — quality/context | Assess applicable sequence quality, composition, context, edit encoding, or coverage | `quality_evidence.csv` |
| 8. E4 — specificity | Assess relevant genomic or transcriptomic near matches and off-target evidence | `specificity_evidence.csv` |
| 9. E5 — application layer | Add application-specific annotations and pair/edit/transcript/set-level evidence | Task-specific tables |
| 10. R1 — gates | Apply frozen shared gates and brief-confirmed vetoes | `gate_log.json` |
| 11. R2/R3 — ranking | Rank eligible candidates with disclosed weights; assess sensitivity and diversity/tradeoffs | `ranked_candidates.csv`, `ranking_stability.json` |
| 12. Delivery | Produce results, evidence, provenance, caveats, and report | `provenance.json`, `report.md` |

Evidence records should contain candidate ID, metric, value/unit, method, version, parameters, source, evidence tier, and status wherever applicable.

## 5. Task-Specific Requirements

### 5.1 Gene knockout

Report coding-exon position, transcript coverage, predicted coding consequence, paralog context, and guide diversity. Do not equate predicted frameshift/disruption with demonstrated knockout.

### 5.2 Base editing

Normalize the requested variant and confirm REF/ALT against the selected reference. Record editor, strand, editing-window position, intended-edit compatibility, bystanders, and predicted consequences. A high guide score alone is insufficient.

### 5.3 CRISPRa / CRISPRi

Treat activation and interference as distinct modes. Record effector, transcript and selected TSS, coordinate convention, promoter-relative placement, isoform coverage, and context-data availability. Do not claim measured expression change.

### 5.4 Paired-guide deletion

Evaluate each guide and the pair. Report orientation, spacing, predicted boundaries, interval size, pair-level risks, and transcript consequences. Do not infer deletion efficiency by multiplying guide scores unless a validated model is specified.

### 5.5 Cas13 RNA targeting

Verify the target transcript and system. Report isoform coverage, transcriptome matches, and supported RNA context/accessibility evidence. Do not apply DNA PAM assumptions indiscriminately or claim measured knockdown.

### 5.6 Guide optimization / reranking

Retain the baseline candidates and scores. Define hard constraints versus soft objectives and the optimization method. Track candidate lineage, report rank changes and Pareto tradeoffs, and do not silently relax gates or substitute the target.

### 5.7 Prime editing

Verify the normalized edit and reference allele. Keep spacer, PBS, and RTT components separately traceable; check that each candidate encodes the requested edit. Report optional nicking-guide scope and byproduct uncertainty. Do not claim successful edit installation.

### 5.8 Multiplex editing

Report individual-guide evidence and set-level evaluation. Include target coverage, uncovered targets, set-level specificity, redundancy/diversity, compatibility assumptions, and set size. Individual guide scores do not establish combined editing outcomes.

## 6. Gates and Ranking

- Define and version each gate, threshold/rule, and evidence source before ranking.
- Record every pass/fail and exclusion reason.
- User-confirmed vetoes may tighten criteria. Changes to shared gates require a documented proposal and approval.
- Disclose ranking dimensions, weights, normalization, and composite-score calculation.
- Perform the task-specified weight sensitivity analysis (including ±25% where required).
- Preserve meaningful alternatives and report tradeoffs; do not hide conflicting objectives inside one score.
- Do not call a candidate "best," "safe," or "validated" without specifying the evidence and scope.

## 7. Benchmarking

Benchmarking must identify the named reference paper or dataset, release, candidate set, assay, and measured versus predicted fields. Compare like with like: application, nuclease/editor, target type, biological context, and metric. Report mismatches and missing measures explicitly.

Environment predictions must remain distinguishable from reference-reported experimental results. Similarity to a reference set alone does not establish general validation.

## 8. Standard Outputs and Provenance

Each run should contain:

```text
runs/<run_id>/
├── confirmed_brief.json
├── reference_validation.json
├── application_readiness.json
├── candidate_pool.csv
├── evidence/
│   ├── validation_evidence.csv
│   ├── activity_evidence.csv
│   ├── quality_evidence.csv
│   └── specificity_evidence.csv
├── gate_log.json
├── ranking_stability.json
├── provenance.json
├── report.md
└── <task-specific output files>
