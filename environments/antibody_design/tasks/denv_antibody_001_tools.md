# Task: denv_antibody_001

**Task variant:** `tool_specific`  
**Task family:** monoclonal-antibody design and computational assessment  
**Status:** specification; scientific execution requires qualified external capabilities.

## Description

Develop a computationally supported shortlist of DV87.1-derived monoclonal-antibody candidates targeting Domain III of the DENV-2 envelope protein. Assess candidate quality across target recognition, structural confidence, predicted binding, stability, and developability while preserving the reference framework and heavy/light-chain pairing.

The scientific intuition is that a plausible antibody candidate must satisfy several requirements together. Strong predicted binding cannot compensate for an unreliable fold, an uncertain target interface, or a major developability liability. Return up to the requested number of candidates that pass every mandatory rule in the frozen evaluation protocol.

## Target

**Name:** Dengue virus serotype 2, DENV-2  
**Protein:** Envelope protein  
**Target Region:** Domain III, EDIII  
**Reference Monoclonal Antibody:** DV87.1  
**Antigen Sequence and Structure:** Exact supplied construct and coordinate file; unresolved until provided  
**Antibody Sequences:** Complete, correctly paired reference heavy and light chains; unresolved until provided  
**Chains and Numbering:** Explicit antigen/heavy/light-chain assignments and sequence-to-structure mapping  
**Binding Region:** The supplied, verified EDIII annotation; do not guess residue numbering

## Design Constraints

- Preserve the reference framework, chain pairing, and declared construct format.
- Determine sequence lengths and permitted variation from verified reference annotations.
- Use unique candidate IDs and retain the reference identity for every candidate.
- Register supplied candidate pairs or outputs of a separately qualified design capability. Candidate generation is not implemented by this specification package.
- Reject malformed or duplicate pairs and record framework-constraint violations.
- Apply the same assessment definitions to the reference and candidates.
- Freeze acceptance criteria, implementation versions, ranking, and budgets before evaluation.
- Return fewer candidates when fewer satisfy the required criteria; never fill the shortlist with unresolved or failed candidates.

## Available Computational Methods

Use the following documented methods for their stated capabilities after the evaluator has qualified their exact versions and input/output contracts. Their inclusion here does not establish installation, availability before the cutoff, or working service access.

| Documented Method | Required Role | Evidence to Retain |
| --- | --- | --- |
| Stability-Binding DDG (`stability-binding-ddg`) | Assess per-mutation DDG values for candidate stability screening using the registered protein-optimization service. | Candidate/reference identity, input sequence and chain, declared mutations, DDG values, unresolved scientific sign convention, service revision, and native CSV output. |
| PRODIGY | Estimate binding energetics for the declared antibody–antigen interface. | Predicted energy, units, conditions, chain selection, and native output. |
| ipSAE | Assess confidence in the antigen–antibody interface. | Score definition, direction and chain scope, input-confidence companions, and version. |

The documents do not provide a qualified implementation for antibody–antigen complex prediction, docking, developability endpoints, or molecular dynamics. Resolve these through qualified capability contracts. Do not introduce an invented tool name, API signature, or parameter set. Stability-Binding DDG does not generate antibody sequences or replace antibody–antigen complex prediction. Its DDG sign convention must remain unresolved until confirmed by the returned product artifact or an authoritative service contract.

## Required Execution Steps

| Step | Required Assessment | Scientific Intuition and Expected Evidence |
| --- | --- | --- |
| 1. Resolve inputs | Verify target, reference, construct, chain mapping, annotations, protocol, and resource limits. | Correct identity is the foundation of every comparison; return `NEEDS_INPUT` or `PROTOCOL_REQUIRED` when necessary. |
| 2. Establish the reference | Evaluate the reference under the frozen comparison conditions. | A claimed improvement requires a comparable baseline with recorded evidence. |
| 3. Register candidate pairs | Check candidate identity, pairing, uniqueness, framework constraints, and provenance. | Candidate handling must preserve the intended molecular entity across stages. |
| 4. Assess structures | Examine predicted fold/complex confidence, local uncertainty, and coordinate integrity. | A structurally plausible antibody is necessary for interpreting its predicted interface. |
| 5. Assess target binding | Evaluate antigen-interface confidence, contacts, geometry, and predicted interaction energetics. | Correct target placement and complementary interactions support a binding hypothesis; they do not establish measured affinity. |
| 6. Assess developability | Evaluate stability, aggregation, solubility, expression-related liabilities, polyreactivity, and immunogenicity indicators separately. | Experimental feasibility depends on several properties beyond target binding. |
| 7. Assess dynamics | When required, assess numerical structural deviations, residue fluctuations, and interface persistence. | Dynamic evidence tests aspects of a static structural hypothesis; insufficient sampling remains unresolved. |
| 8. Qualify and rank | Recompute frozen rule outcomes from current evidence and order eligible unique pairs. | Missing or failed mandatory evidence cannot be compensated by an unrelated favorable score. |
| 9. Export results | Return paired sequences, metrics, ranking, provenance, limitations, and resource use. | A result must be independently inspectable and traceable to its inputs. |

## Evaluation Metrics

Report the protocol-defined structural-confidence, target-interface, predicted-binding, stability, aggregation, solubility, expression, polyreactivity, immunogenicity, and applicable dynamics measurements. Include the reference comparison, units, scale, calculation method, uncertainty, and native evidence for each measurement.

Keep local structural confidence separate from interface confidence. Antigen–antibody interface evidence must not be replaced by heavy/light-chain interface evidence. Report missing numeric values as `null` with `UNRESOLVED` status and a reason. The qualified protocol supplies scientific thresholds; historical shortlist values are not thresholds.

## Expected Output

**Format:** `antibody_design_bundle`

**Required Output Files in `08_results/`:**

- `designed_sequences.fasta`: shortlisted candidate pairs only, with `>candidate_id|H` and `>candidate_id|L` headers.
- `metrics.json`: all evaluated candidate and reference records, measurements, rule decisions, evidence hashes, exclusions, shortlist, provenance, resource use, and stop reason.
- `shortlist.csv`: ordered `rank,candidate_id,sequence_sha256` rows matching the FASTA and metrics.
- `report.md`: findings, tradeoffs, unresolved questions, and requested-versus-returned counts.

Include native evidence artifacts with relative paths and SHA-256 hashes. Reference results belong in `metrics.json`; the reference cannot appear as a designed candidate. A completed negative result has an empty FASTA and a header-only shortlist. A preflight failure returns structured `metrics.json` with the missing requirements and no candidate results.

## Constraints

- **Candidate and time limits:** use the frozen request. The example request demonstrates a maximum of 10 candidates, a final count of up to 10, and a 120-minute wall-time budget; these are illustrative limits, not demonstrated scientific throughput.
- **Knowledge cutoff:** use the request's cutoff, initially `2024-09-01`. Verify the availability of code, model, and dataset versions before execution. Unknown or incompatible eligibility requires `PROTOCOL_REQUIRED`.
- **Compute:** enforce CPU, GPU, wall-time, and service budgets. Required assessments cannot be silently dropped when the budget is exhausted.
- **Evaluation integrity:** keep historical candidate rankings and experimental outcomes hidden until computational conclusions are frozen.
- **Scope:** computational predictions and artifact validation. No measured binding, neutralization, or clinical claim is established by this task.

## Important Instructions

- Do not invent biological inputs, implementation settings, confidence values, or a qualified protocol.
- Distinguish predicted binding energy, measured Kd, ELISA binding EC50, and neutralization potency.
- Keep both chains and their pairing intact in every conversion and export.
- Invalidate prior evidence whenever the evaluated sequence changes.
- Use `PASS`, `FAIL`, and `UNRESOLVED` consistently; qualification requires every mandatory rule to pass.
- Distinguish `NO_QUALIFYING_DESIGNS` from `INCOMPLETE`: unresolved work cannot establish a completed negative result.
- Report scientific methods actually used even when this task does not prescribe them.
- Passing file/schema validation does not establish biological validity or successful scientific execution.
