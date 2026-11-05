# Task: denv_antibody_001

**Task variant:** `tool_specific`

## Description

Perform monoclonal-antibody design and computational assessment using DV87.1 as the reference and DENV-2 envelope Domain III as the target. Produce a shortlist of unique, reference-derived antibody pairs that pass every mandatory rule in the frozen evaluation protocol. Compare candidates with the reference under the same conditions.

## Target

**Name:** Dengue virus serotype 2, DENV-2\
**Protein:** Envelope protein\
**Target Region:** Domain III, EDIII\
**Reference Antibody:** DV87.1\
**Antigen Sequence and Structure:** Exact supplied construct and coordinate file\
**Reference Sequences:** Complete, correctly paired reference heavy and light chains\
**Chains and Numbering:** Antigen/heavy/light assignments and sequence-to-structure mapping\
**Binding Region:** The supplied, verified EDIII annotation; do not guess residue numbering

## Design Constraints

- Preserve the reference framework, chain pairing, and declared construct format.
- Derive permitted sequence changes from the supplied framework/CDR annotations.
- Assign unique candidate IDs and record each candidate's reference parent and sequence hash. Reject malformed or duplicate pairs.
- Freeze acceptance criteria, method versions, and ranking before evaluation; assess the reference and candidates consistently.
- Return up to the requested candidate count; never fill the shortlist with unresolved or failed candidates.

## Computational Tool Capabilities

Use verified capabilities supplied by the execution environment in the following order. Record unavailable capabilities and leave their required evidence unresolved.

| Stage | Capability | Expected Evidence |
| --- | --- | --- |
| 1. Validate inputs and baseline | Check target/reference identity, chain mapping, annotations, and comparable baseline evidence. | Verified input records, reference measurements, and missing-input list. |
| 2. Generate or register candidates | Produce constrained reference-derived sequences or register supplied pairs. | Paired candidates, parent identity, edit trace, and unique sequence hashes. |
| 3. Assess antibody structure | Predict or assess antibody folds, chain pairing, and CDR conformations. | Structures, local confidence, uncertain regions, and geometry checks. |
| 4. Assess target complexes | Model or evaluate antibody–target poses in the declared target context. | Mapped interfaces, clashes, epitope compatibility, and pose uncertainty. |
| 5. Evaluate binding and specificity | Assess antigen-interface confidence, interaction energetics, and declared specificity/function evidence. | Chain selection, interface confidence inputs, energy units and conditions, metric definitions, and native outputs. |
| 6. Assess developability | Assess mutation-associated stability and other required property risks separately. | Reference/candidate mutation mapping, verified energy-change sign convention, native outputs, and property-specific limitations. |
| 7. Refine when justified | Revise permitted positions and repeat affected evaluations. | Revision history and fresh evidence for the updated sequence. |
| 8. Select and report | Apply all mandatory criteria, compare with the reference, and rank eligible pairs. | Shortlist, exclusions, unresolved evidence, and traceable results. |

## Evaluation Metrics

| Criterion | Measurements and Evidence | Evaluation Rule |
| --- | --- | --- |
| Identity and pairing | Reference-parent identity, paired-sequence hashes, permitted changes, and duplicate checks. | Preserve framework, chain pairing, and construct identity. |
| Structure | Assess predicted fold/complex confidence, local uncertainty, and coordinate integrity. | Keep local structural confidence separate from interface confidence. |
| Target interface | Epitope contacts, interface area, clashes, chain scope, and positional uncertainty. | Antigen–antibody interface evidence must not be replaced by heavy/light-chain interface evidence. |
| Binding and reference comparison | Predicted interaction evidence under matched target, method, and conditions; supplied assay data reported separately. | Computational predictions do not establish measured affinity; an absolute score does not demonstrate reference improvement. |
| Developability | Evaluate stability, aggregation, solubility, expression-related liabilities, polyreactivity, and immunogenicity indicators separately. | Record metric direction, units, applicability, and per-property uncertainty. |
| Specificity and functional evidence | Declared target-panel results and separately supplied binding, neutralization, or enhancement-risk evidence. | Do not infer neutralization or absence of antibody-dependent enhancement from a binding prediction. |
| Dynamics, when required | Report numerical structural deviations, residue fluctuations, and interface persistence. | State sampling limits; a stable trajectory does not establish biological activity. |
| Selection and evidence integrity | Reference comparison, uncertainty, source artifacts, and candidate-specific rule outcomes. | Missing or failed mandatory evidence cannot be compensated by an unrelated favorable score. |

The supplied protocol defines thresholds and ranking. Missing numeric values are `null` with `UNRESOLVED` status and a reason. Keep the reference baseline, all evaluated candidates, and explanations of exclusions.

## Expected Output

**Format:** `antibody_design_bundle`\
**Directory:** `08_results/`

- `designed_sequences.fasta`: shortlisted pairs with `>candidate_id|H` and `>candidate_id|L` headers.
- `metrics.json`: reference/candidate records, measurements, rule decisions, exclusions, provenance, and stop reason.
- `shortlist.csv`: ordered `rank,candidate_id,sequence_sha256` rows matching the FASTA and metrics.
- `report.md`: reference comparison, selection rationale, limitations, and requested-versus-returned counts.

Include supporting artifacts with relative paths and SHA-256 hashes. Reference results belong in `metrics.json`; the reference cannot appear as a designed candidate. A completed negative result has an empty FASTA and a header-only shortlist. Missing inputs or protocol requirements return `NEEDS_INPUT` or `PROTOCOL_REQUIRED` without candidate results.

## Constraints

- **Knowledge Cutoff:** `2024-09-01`; verify the eligibility of method, model, and dataset versions against the request.
- **Evaluation Integrity:** keep historical candidate rankings and experimental outcomes hidden until computational conclusions are frozen.

## Important Instructions

- Do not invent target/reference sequences, structures, residue mappings, measurements, or acceptance thresholds.
- Distinguish predicted binding energy, measured Kd, ELISA binding EC50, and neutralization potency.
- Keep both chains paired and invalidate prior evidence after sequence changes.
- Use `PASS`, `FAIL`, and `UNRESOLVED` consistently; qualification requires every mandatory rule to pass.
- Distinguish `NO_QUALIFYING_DESIGNS` from `INCOMPLETE`: unresolved work is not a completed negative result.
- Report the methods and versions actually used. Computational predictions do not establish biological validity, neutralization, or safety.
