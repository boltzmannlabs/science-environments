# Task: mab_reference_guided_design

**Task family:** reference-guided monoclonal antibody design and assessment  
**Task variant:** tool-neutral  
**Status:** benchmark specification; molecular inputs and a qualified protocol must be supplied before execution.

**Initial environment lane:** paired heavy/light monoclonal reference optimization. This task is computational-only and uses the tools declared in the frozen protocol and Agent-Scientist run manifest. The environment does not run wet-lab assays.

## Description

Using the supplied target profile and reference monoclonal antibody, produce an evidence-supported shortlist of reference-derived candidate antibodies for the stated biological objective. Preserve heavy/light pairing and follow the declared molecular format, sequence-edit boundaries, and framework policy. This task covers constrained redesign or optimization around a known antibody; it is not unrestricted de novo design.

The request must choose one primary design mode and freeze its required evidence domains. The decision may consider target interaction, the requested computational mechanism evidence, antibody structure, selectivity, and developability as separate gates. A favorable interface prediction alone is not sufficient evidence that a candidate is useful or suitable for the requested use.

## Supported reference-guided objectives

Use one row per run. Do not combine the objectives into a single uncalibrated score.

| `design_mode` | Primary computational objective | Mandatory comparison/gates |
|---|---|---|
| `reference_guided` | Produce a constrained, evidence-supported candidate set for the declared objective | Reference baseline; paired-chain identity; declared framework/edit policy; structure, interface, binding, and developability rules |
| `affinity_maturation` | Improve predicted binding evidence while preserving the declared epitope and framework | Same target construct and protocol for reference/candidates; binding and interface evidence; hard developability gates; call the result computational enrichment, not measured affinity improvement |
| `humanization` | Apply the declared human-framework policy while retaining the reference binding-site design | Reference origin, selected germline/framework policy, mutation trace, framework rules, binding-retention proxy, and immunogenicity-risk descriptors; never claim reduced clinical immunogenicity from a sequence score |
| `developability_optimization` | Reduce a specifically named computational liability while preserving target-recognition evidence | Named risk metric and applicability domain; stability, aggregation, solubility, expression, and polyreactivity groups as required by the protocol; binding-retention gate |
| `specificity_optimization` | Prefer the intended target over a frozen homolog/variant/ortholog panel | Hashed panel; per-member target identity; same declared scoring protocol; specificity results for every panel member; missing panel members remain unresolved |
| `mechanism_optimization` | Prioritize candidates for one declared mechanism hypothesis | Declared functional endpoint and computational method; antigen-interface and binding evidence; function remains unresolved if no qualified computational method/benchmark evidence is available |

The `de_novo` mode belongs to the separate target-only task and cannot use a reference record. Fc/isotype engineering, format conversion, multispecific design, and conjugate design are outside this paired-chain reference-optimization task.

## Target and reference inputs

The run package must identify and hash the following records. Missing or conflicting identity information must stop dependent assessment rather than be inferred.

| Record | Required content |
| --- | --- |
| Target profile | Target name and organism; accession or stable identifier when available; exact full sequence; target construct sequence; isoform, strain, or variant; expression and presentation context; oligomeric state; known post-translational modifications; structure or an explicit statement that none is supplied. |
| Epitope definition | Epitope residues or region with sequence-to-structure mapping and source; whether the epitope is fixed, constrained, or open for exploration; any excluded, inaccessible, glycan-occluded, or biologically irrelevant surface. |
| Reference antibody | Reference ID; complete paired heavy and light sequences; product format; explicit sequence scope (`variable_domains`, `Fab_chains`, or `full_length_chains`); variable-domain numbering scheme; framework/CDR annotations; species origin; isotype and Fc design when applicable; available structure and experimental evidence. |
| Biological objective | Intended mechanism and target context, such as blocking, neutralization, agonism, depletion, or binding-only characterization; required functional readout and the conditions under which it is interpreted. |
| Frozen protocol | Candidate budget; permitted edits; required measurements; acceptance predicates; ranking rule; sequence and artifact provenance; resource limits; knowledge cutoff. |

The generic request records a requested shortlist count, a fixed random seed, the complete candidate budget, and a relative-path/hash reference to the qualified protocol. The target-agnostic result uses `generic-antibody-metrics.schema.json`; the DENV profile retains `metrics.schema.json`.

## Design constraints

- Treat one paired heavy/light antibody as the candidate identity. Keep both chains and their pairing intact in every structure, score, and export.
- Apply the declared numbering scheme and allowed edit mask. Preserve protected framework positions, conserved cysteines, and required chain features unless the request explicitly permits changes.
- Keep product format, sequence scope, isotype, Fc modifications, and valency fixed unless the task explicitly evaluates those choices. The initial contract supports paired-chain IgG, Fab, and F(ab')2 contexts; scFv, VHH/nanobody, fusion, conjugate, and multispecific architectures need separate chain-architecture contracts.
- Register the reference as a baseline and assess it under the same target construct and evaluation definitions as every candidate.
- Assign every candidate a unique ID, parent reference ID, and paired-sequence digest. Re-score any candidate after a sequence or construct change.
- Do not infer an experimental affinity, functional potency, or safety result from a structure or model score.
- Computational mechanism scores remain predictions. If a required function endpoint has no qualified computational method or supplied benchmark labels, mark it `UNRESOLVED`; do not represent a wet-lab assay as executed.
- Return fewer candidates when fewer satisfy all required gates. Do not fill the requested shortlist with unresolved candidates.

## Required assessment stages

| Stage | Required assessment | Decision purpose |
| --- | --- | --- |
| 1. Input and identity review | Verify target, construct, reference sequences, chain mapping, numbering, annotations, protocol, and hashes. | Prevent a correct calculation on the wrong molecular entity. |
| 2. Reference baseline | Record the reference's sequence, structure, target binding, assay, and developability evidence with conditions and provenance. | Define the comparison and expose gaps in the starting evidence. |
| 3. Candidate registration | Check paired-chain integrity, edit-mask compliance, uniqueness, framework preservation, and lineage. | Ensure each record still represents an allowed descendant of the reference. |
| 4. Antibody structure | Assess chain-level fold plausibility, variable-domain geometry, CDR loop uncertainty, and coordinate integrity. | Separate antibody folding confidence from target recognition. |
| 5. Target-complex assessment | Assess pose plausibility, epitope compatibility, interface geometry, clashes, contacts, buried area, and confidence. | Determine whether the proposed antibody orientation is consistent with the supplied target context. |
| 6. Binding and mechanism | Report model-derived binding evidence separately from measured affinity and from the intended functional endpoint. | A target-binding hypothesis does not establish blocking, agonism, neutralization, or another mechanism. |
| 7. Selectivity and breadth | Assess the declared homolog, isoform, species, and variant panel; report untested members explicitly. | Identify cross-reactivity or escape risks relative to the requested target scope. |
| 8. Developability | Evaluate stability, aggregation, solubility, self-interaction, expression-related risks, sequence liabilities, and immunogenicity indicators as distinct measures. | Avoid advancing an attractive binder whose physical or sequence risks are unresolved. |
| 9. Qualification and export | Apply the frozen hard gates, preserve failed and unresolved rows, rank eligible pairs, and package native evidence. | Make the recommendation traceable and reproducible. |

Dynamics or glycan-aware modeling is conditional: include it when the target state, epitope, or task protocol requires it, and report sampling limits. Neither is a universal substitute for experimental evidence.

## Evaluation metrics

For each metric, record its definition, unit or score scale, target and antibody scope, method revision, applicability, uncertainty, and evidence artifact. At minimum, cover:

- paired-chain identity, numbering, framework/edit-mask compliance, and sequence uniqueness;
- antibody-domain confidence and CDR-specific uncertainty;
- target-interface confidence and structural geometry, with antigen–antibody chain scope;
- predicted interaction or affinity proxy, clearly labeled as computational;
- experimental affinity or kinetic measurements only when supplied, preserving assay format and conditions;
- target-specific function under the declared mechanism;
- cross-reactivity or variant panel results;
- stability and developability risks, with prediction separated from measured assay results;
- humanization or immunogenicity risk indicators when required by the task.

Do not combine unlike endpoints into one score unless the evaluator supplies a validated, frozen calibration. A missing value is `UNRESOLVED`, not zero. A model confidence score is not a probability of clinical success.

## Expected output

**Format:** `antibody_design_bundle`  
**Directory:** `08_results/`

- `designed_sequences.fasta`: eligible paired heavy and light sequences, identified by candidate and chain.
- `metrics.json`: reference and candidate identities; declared sequence scope; all metric values and statuses; hard-gate decisions; exclusions; limitations; provenance; resource use; and stop reason.
- `shortlist.csv`: rank, candidate ID, paired-sequence digest, and eligibility status.
- `report.md`: concise decision rationale, reference comparison, uncertainty, unresolved evidence, and requested-versus-returned counts.
- Native candidate structures and scoring artifacts, each with relative path and SHA-256 digest.
- Optional externally sourced assay-record files referenced by `assay_records`; the environment validates their identity/provenance but does not perform the assays.

A preflight result may contain no candidate outputs and must state missing inputs. A completed result with no qualifying candidates must distinguish verified failure from incomplete or unresolved evidence.

## Important instructions

- Use the [generic target/reference request contract](../config/generic-antibody-request.schema.json) when constructing the task input.
- Do not invent target residues, sequence mutations, assay results, or thresholds.
- Do not expose held-out experimental outcomes or historical candidate rankings to the design process before the evaluation is frozen.
- Report actual methods and versions in the run evidence, but this task does not prescribe software.
- Bind the result to an Agent-Scientist run manifest containing provider/model revision, harness revision, prompt hashes, enabled-tools hash, execution backend, environment digest, isolated workspace ID, and seed.
- A passing file or schema check is not evidence of antibody binding or function.
