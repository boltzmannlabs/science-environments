# Task: mab_reference_guided_design

## Description

Design and assess monoclonal antibody candidates derived from **cetuximab** against **human EGFR (ERBB1)**. Preserve the reference heavy/light-chain pairing and the declared sequence-edit boundaries. Compare every candidate with cetuximab under the same EGFR target and evaluation conditions.

The objective is reference-guided refinement while retaining EGFR recognition at the cetuximab-associated domain III binding region. Define the property to improve and the binding/developability requirements to retain before evaluation; do not claim improvement without a matched cetuximab comparison.

## Target

**Target:** Human EGFR (ERBB1), extracellular domain\
**Reference Antibody:** Cetuximab\
**Binding Region:** EGFR extracellular domain III; use the supplied reference epitope annotation and residue mapping\
**Structure and Context:** Supplied EGFR construct and coordinates, native cell-surface presentation, chain mapping, and relevant modifications\
**Reference Inputs:** Verified paired cetuximab heavy/light sequences with framework/CDR annotations and numbering\
**Antibody Format:** Declared IgG, Fab, or F(ab')2 context and sequence scope\
**Objective:** Assess reference-derived candidates against cetuximab using matched EGFR-binding and developability criteria

## Design Constraints

- Preserve chain pairing, protected framework positions, and required domain features. Apply the declared edit mask and numbering scheme.
- Keep format, sequence scope, isotype, and Fc policy consistent with the request.
- Assign unique candidate IDs, reference-parent IDs, and sequence hashes; remove duplicate pairs.
- Assess cetuximab alongside candidates using the same EGFR construct and methods. Preserve its declared binding region and reassess changed sequences before reusing their evidence.
- For humanization, document framework selection and binding-retention evidence. For specificity optimization, assess every member of the declared comparison panel.
- For mechanism optimization, require evidence for the stated functional endpoint; missing evidence remains unresolved.
- Return up to the requested count using all mandatory criteria, without filling the shortlist with failed or unresolved candidates.

## Computational Tool Capabilities

Use verified capabilities supplied by the execution environment in the following order. Record unavailable capabilities and leave their required evidence unresolved.

| Stage | Capability | Expected Evidence |
| --- | --- | --- |
| 1. Validate inputs and baseline | Check EGFR and cetuximab identity, chain mapping, annotations, and comparable baseline evidence. | Verified input records, reference measurements, and missing-input list. |
| 2. Generate or register candidates | Produce constrained cetuximab-derived sequences or register supplied reference-derived pairs. | Paired candidates, parent identity, edit trace, and unique sequence hashes. |
| 3. Assess antibody structure | Predict or assess antibody folds, chain pairing, and CDR conformations. | Structures, local confidence, uncertain regions, and geometry checks. |
| 4. Assess target complexes | Model or evaluate antibody–target poses in the declared target context. | Mapped interfaces, clashes, epitope compatibility, and pose uncertainty. |
| 5. Evaluate binding and specificity | Assess interaction predictions and declared specificity/function evidence. | Comparable reference/candidate measurements and panel coverage. |
| 6. Assess developability | Evaluate distinct physical, sequence, and interaction-related liabilities. | Property scores, localized risk flags, applicability, and uncertainty. |
| 7. Refine when justified | Revise permitted positions and repeat affected evaluations. | Revision history and fresh evidence for the updated sequence. |
| 8. Select and report | Apply all mandatory criteria, compare with the reference, and rank eligible pairs. | Shortlist, exclusions, unresolved evidence, and traceable results. |

## Evaluation Metrics

| Criterion | Measurements and Evidence | Evaluation Rule |
| --- | --- | --- |
| Identity and allowed changes | Heavy/light pairing; numbering; framework/CDR edits; duplicate pairs; sequence/artifact hashes. | Every shortlisted pair must retain valid lineage and comply with the declared edit policy. |
| Objective-specific comparison | Candidate-minus-cetuximab differences on the same EGFR construct, endpoint, method, and conditions. | Define favorable direction and required retained properties in advance; an absolute passing score alone does not show improvement. |
| Antibody structure | Local confidence by chain/CDR, interdomain uncertainty, clashes, and missing coordinates. | Inspect weak local regions; a high global average must not conceal an uncertain binding loop. |
| Target interface | Mapped epitope contacts, buried interface area, clash counts, interchain uncertainty, and pose consistency. | Use antigen–antibody scope; structural accuracy requires an independent reference complex when claimed. |
| Binding and function | Interaction predictions; supplied measured affinity and kinetics; mechanism-specific observations and controls. | Do not convert confidence or predicted energy into measured affinity; keep function separate from binding. |
| Specificity and breadth | EGFR-binding results and per-member results for the declared receptor-family, variant, or off-target panel. | Report panel coverage and missing members; absence of tested off-target binding is not universal specificity. |
| Developability and humanization | Stability, aggregation, solubility, expression, self-interaction, chemical liabilities, polyreactivity, and relevant humanization descriptors. | Apply each required endpoint separately; sequence humanness and predicted immunogenicity do not establish clinical immune tolerance. |
| Evidence completeness | Method revisions, units, uncertainty, comparator conditions, native artifacts, and supplied assay provenance. | All mandatory rules must pass; retain failures and unresolved measurements. |

Use the supplied protocol to set thresholds and ranking before evaluation. Report conditional analyses only when supported by the task and inputs. Predictions, supplied measurements, and unresolved endpoints must remain distinguishable.

## Expected Output

**Format:** `antibody_design_bundle`\
**Directory:** `08_results/`

- `designed_sequences.fasta`: eligible heavy/light pairs with candidate and chain identifiers.
- `metrics.json`: reference and candidate records, sequence hashes, measurements, rule decisions, exclusions, provenance, and stop reason.
- `shortlist.csv`: ordered `rank,candidate_id,sequence_sha256` rows.
- `report.md`: comparison with cetuximab, EGFR-binding evidence, ranking rationale, limitations, and unresolved evidence.
- Supporting structures, scoring outputs, and any supplied assay records with relative paths and SHA-256 hashes.

Keep the reference in the evaluation records and out of the designed shortlist. Report missing inputs as `NEEDS_INPUT`, missing evaluation requirements as `PROTOCOL_REQUIRED`, and distinguish incomplete evaluation from a completed result with no qualifying candidates.

## Important Instructions

- Do not invent reference sequences, target annotations, assay outcomes, or acceptance thresholds.
- Keep held-out experimental outcomes and historical rankings hidden until evaluation is frozen.
- Record actual methods, versions, provenance, and the request's knowledge cutoff.
- A computational score does not establish experimental affinity improvement, functional activity, or clinical suitability.
