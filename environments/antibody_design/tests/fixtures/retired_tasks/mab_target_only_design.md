# Task: mab_target_only_design

## Description

Propose and assess paired-chain monoclonal antibody candidates targeting the **extracellular domain of human EGFR (ERBB1)**, without a supplied binding-reference antibody. Define the antibody format, permitted frameworks, accessible EGFR search region, and evaluation criteria before generating or selecting candidates.

The objective is to identify EGFR-binding candidates with supported structural, specificity, and developability evidence. Record whether candidates are generated, retrieved, or selected from a supplied library. Do not treat an existing EGFR-binding antibody as an undisclosed reference or claim improvement over one.

## Target

**Target:** Human EGFR (ERBB1), extracellular domain\
**Reference Antibody:** None supplied; this is target-only discovery\
**Binding Region:** Accessible extracellular EGFR surface defined in the request; no reference-antibody epitope is imposed\
**Structure and Context:** Supplied EGFR construct and coordinates, native cell-surface presentation, chain mapping, and relevant modifications\
**Antibody Format:** Declared paired-chain IgG, Fab, or F(ab')2 context and sequence scope\
**Objective:** Discover and assess EGFR-binding candidates using predefined binding, specificity, and developability criteria

## Design Constraints

- Declare framework selection, numbering convention, humanization requirements, and allowed sequence changes.
- Preserve complete heavy/light pairing, conserved domain features, and valid domain boundaries.
- Record candidate origins and sequence hashes; remove duplicate pairs before ranking.
- Keep the EGFR construct, extracellular search region, and evaluation criteria fixed. Exclude held-out EGFR binders and assay labels from candidate generation and ranking.
- Declare comparison controls or explicitly report their absence. Do not claim improvement over an unspecified reference.
- Return up to the requested candidate count; every shortlisted candidate must satisfy all mandatory criteria.

## Computational Tool Capabilities

Use verified capabilities supplied by the execution environment in the following order. Record unavailable capabilities and leave their required evidence unresolved.

| Stage | Capability | Expected Evidence |
| --- | --- | --- |
| 1. Validate target and design space | Review EGFR extracellular context, accessible search regions, antibody format, framework choices, and controls. | Defined input scope and any missing prerequisites. |
| 2. Generate or select candidates | Generate or select EGFR-directed candidates from declared sources without assuming a binding reference. | Paired candidates, origin records, source provenance, and generation settings. |
| 3. Check identity and diversity | Validate domain boundaries, chain pairing, duplicates, and relatedness. | Valid unique pairs and full-chain/CDR diversity summaries. |
| 4. Assess structures and complexes | Evaluate antibody folds and target poses separately. | Structures, mapped interfaces, local uncertainty, and geometry checks. |
| 5. Evaluate interaction and specificity | Assess binding hypotheses, target-panel coverage, and relevant functional evidence. | Per-candidate predictions and separately labeled supplied observations. |
| 6. Assess developability | Check sequence, physical-property, expression, and nonspecific-interaction risks. | Distinct liability assessments and missing-evidence flags. |
| 7. Refine and reassess | Revise candidates within the declared design space and repeat affected checks. | Traceable revisions and fresh candidate evidence. |
| 8. Select and report | Apply the frozen criteria and report supported diversity and tradeoffs. | Evidence-supported shortlist without a reference-improvement claim. |

## Evaluation Metrics

| Criterion | Measurements and Evidence | Evaluation Rule |
| --- | --- | --- |
| Candidate identity and origin | Valid heavy/light pairs, domain boundaries, source artifacts, and unique sequence hashes. | Distinguish generated, retrieved, and library-derived candidates; do not invent binding-reference lineage. |
| Diversity and novelty | Unique-pair count, full-chain/CDR similarity, comparison corpus, and similarity definition. | State the comparison scope and corpus date; diversity is not proof of binding or universal novelty. |
| Antibody structure | Chain/CDR confidence, interdomain orientation uncertainty, clashes, and structural completeness. | Evaluate local weaknesses separately from whole-antibody confidence. |
| Target compatibility | EGFR epitope mapping, interface contacts and area, cell-surface accessibility, pose consistency, and confidence. | Assess the relevant construct and presentation; a predicted fold does not establish a correct binding pose. |
| Binding and controls | Interaction predictions and any supplied affinity/kinetic measurements, with control identity and conditions. | Report absent controls; no comparison to an unspecified binder or conversion of predicted scores into measured affinity. |
| Specificity and function | EGFR recognition, declared receptor-family/off-target panel coverage, and any required mechanism-specific evidence. | Flag missing panel members or functional evidence; binding and biological activity are separate outcomes. |
| Developability | Stability, aggregation, solubility, expression risks, self-interaction, chemical liabilities, polyreactivity, and immunogenicity indicators. | Apply each required criterion independently and preserve its applicability limits. |
| Selection confidence | Uncertainty, method revisions, source evidence, exclusions, and performance of supplied comparison controls. | Use predefined ranking; do not tune selection on held-out outcomes or fill the shortlist with unresolved candidates. |

The supplied protocol defines thresholds, comparison controls, and ranking. Report experimental endpoints as `NOT_MEASURED` when measurements are absent; report missing required computational evidence as unresolved.

## Expected Output

**Format:** `antibody_design_bundle`\
**Directory:** `08_results/`

- `designed_sequences.fasta`: eligible paired sequences with candidate and heavy/light-chain identifiers.
- `metrics.json`: target identity, candidate origins, sequence hashes, measurements, rule decisions, exclusions, and provenance.
- `shortlist.csv`: ordered candidate IDs, paired-sequence hashes, and eligibility status.
- `report.md`: EGFR design-space definition, candidate diversity, ranking rationale, limitations, and unresolved evidence.
- Supporting structures, scoring outputs, and any supplied assay records with relative paths and SHA-256 hashes.

If target identity, construct, format, or evaluation requirements are missing, return `NEEDS_INPUT` or `PROTOCOL_REQUIRED` without candidate outputs.

## Important Instructions

- Do not invent a binding reference, target annotations, assay outcomes, or thresholds.
- Report candidate sequences as computational proposals and retain their actual origin and method provenance.
- Follow the request's knowledge cutoff and keep predicted binding distinct from measured affinity and function.
- A plausible structure does not establish binding, specificity, or therapeutic suitability.
