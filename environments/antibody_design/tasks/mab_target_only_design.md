# Task: mab_target_only_design

**Task family:** target-conditioned de novo monoclonal antibody design and assessment  
**Task variant:** tool-neutral  
**Status:** benchmark specification; target inputs, design policy, and a qualified protocol must be supplied before execution.

**Environment status:** secondary computational monoclonal mode. It is not the initial reference-guided lane and does not establish experimental binding or function.

## Description

Starting from the supplied antigen profile and no supplied reference antibody, propose and assess a bounded set of monoclonal antibody candidates for the specified biological objective. The task is target-conditioned antibody discovery: it must produce paired heavy/light-chain candidates in a declared antibody format, and assess them against the target and the stated mechanism.

This task has no reference antibody sequence against which to claim affinity improvement, framework preservation, or lineage. The benchmark must instead define acceptable antibody sequence families, molecular format, humanization policy, and comparison controls in advance. If those inputs are absent, return `NEEDS_INPUT` or `PROTOCOL_REQUIRED`; do not fabricate a reference clone or claim superiority to one.

## Target inputs

The run package must identify and hash:

- the target accession or stable identifier, organism, full amino-acid sequence, relevant isoform/strain/variant, and construct sequence;
- structure coordinates for the relevant construct or a clear declaration that none is supplied, including chain IDs and sequence-to-coordinate residue mapping;
- native biological context: soluble or cell-surface presentation, oligomeric/complex state, membrane orientation where relevant, known cofactors and post-translational modifications, and evidence for epitope accessibility;
- intended epitope residues or region when specified; otherwise, the permissible search surface, excluded regions, and evidence needed to establish an accessible epitope;
- disease-relevant target variants or homologs for breadth and cross-reactivity assessment;
- intended mechanism, product format, and functional assay context.

The target construct must be biologically relevant to the intended use. A truncated isolated domain may support local structural assessment, but it cannot establish accessibility in a full-length, multimeric, glycosylated, membrane-bound, or particle-associated target unless that context is modeled or otherwise evidenced.

## Design constraints

- The request must declare paired-chain IgG/Fab/F(ab')2 product context, sequence scope (`variable_domains`, `Fab_chains`, or `full_length_chains`), species origin/humanization requirement, allowed variable-domain frameworks or framework-selection policy, numbering convention, candidate count, and sequence constraints. scFv and VHH/nanobody architectures require a separate chain contract.
- Candidates must be complete paired heavy/light antibodies unless the requested format explicitly defines another chain architecture.
- Preserve conserved domain features, disulfide-forming residues, and valid variable-domain boundaries. Flag unusual CDR lengths, insertions, deletions, or framework changes for review.
- Keep the candidate-generation objective and epitope policy frozen before design. Do not let held-out target binders, assay labels, or future experimental outcomes influence generation or ranking.
- Record the model/harness, enabled tools, prompt hashes, execution backend, environment digest, isolated workspace, seed, candidate budget, and resource use in the generic result provenance.
- Establish positive and negative controls or an explicit no-control limitation. Do not describe a candidate as improved over a reference when no reference was supplied.
- Limit the design campaign to the frozen candidate and compute budget. Preserve diversity and lineage metadata; deduplicate paired sequences before ranking.

## Required assessment stages

| Stage | Required assessment | Decision purpose |
| --- | --- | --- |
| 1. Resolve target and objective | Validate target sequence/construct, native state, variant scope, epitope policy, intended mechanism, format, and budget. | Ensure candidate generation addresses the intended biological molecule and use. |
| 2. Define design space | Record framework policy, variable regions, antibody format, target epitope constraints, and allowed sequence diversity. | Make the design task reproducible and avoid uncontrolled changes in molecular format. |
| 3. Register candidates | Validate complete chain pairing, sequence syntax, uniqueness, ancestry, and construct compatibility. | Prevent malformed or duplicate outputs from inflating the shortlist. |
| 4. Assess antibody structures | Examine variable-domain fold, CDR conformations, chain pairing, local uncertainty, and structural integrity. | Test whether the proposed antibody is structurally plausible. |
| 5. Assess target complexes | Examine epitope compatibility, interface geometry, steric access, confidence, and alternative poses or target states. | A plausible antibody fold does not establish correct target docking. |
| 6. Assess function and specificity | Evaluate target-specific functional hypotheses and cross-reactivity against the frozen variant/homolog panel. | Identify candidates whose apparent binding is inconsistent with the stated objective or specificity scope. |
| 7. Assess developability | Evaluate sequence liabilities, aggregation, solubility, stability, self-interaction, expression risk, and immunogenicity indicators. | Avoid ranking solely by predicted binding. |
| 8. Qualify and export | Apply every mandatory rule, preserve failures and uncertainty, and report the candidate set with evidence. | Produce an auditable shortlist without unsupported claims of affinity or efficacy. |

## Evaluation metrics

Report antibody-chain fold confidence and loop uncertainty separately from target-interface confidence. Include interface contacts/geometry, clashes, epitope mapping, predicted interaction scores, variant-panel coverage, and per-candidate developability flags with their score scales and limitations.

Where experimental data are provided, distinguish measured equilibrium affinity (`Kd`), association and dissociation kinetics, avidity-dependent cell binding, biochemical binding assays, and the mechanism-specific functional endpoint. These are not interchangeable. If no experimental results are supplied, label all such endpoints `NOT_MEASURED`; do not substitute structure confidence or predicted energy.

Use an all-required-gates rule for qualification. When candidates trade off binding, breadth, specificity, and developability, report a multi-objective/Pareto view or the frozen priority order; do not invent an uncalibrated composite score.

## Expected output

**Format:** `antibody_design_bundle`  
**Directory:** `08_results/`

- `designed_sequences.fasta`: eligible paired sequences with explicit heavy/light chain identifiers.
- `metrics.json`: target/profile hashes; declared sequence scope; candidate sequences and hashes; all structure, interface, function-proxy, specificity, and developability evidence; statuses; exclusions; provenance; and resource use.
- `assay_records`: optional hashed files containing external or historical assay evidence; the computational environment does not execute those assays.
- `shortlist.csv`: ordered candidate IDs, paired-sequence hashes, and eligibility status.
- `report.md`: design-space definition, candidate diversity, ranking rationale, uncertainty, limitations, and the evidence required next.
- Native structures and evidence artifacts with relative paths and SHA-256 digests.

If target identity, relevant construct, format, or evaluation rules are missing, return a structured preflight result with no candidate sequences. A candidate set that passes computational rules remains a hypothesis until independently tested.

## Important instructions

- This task has no reference antibody. Never invent one, report a reference-derived improvement, or use an unverified known binder as an implicit control.
- Use the [generic target/reference request contract](../config/generic-antibody-request.schema.json); for this mode, the reference field is `null` and design mode is `de_novo`.
- Do not invent amino-acid sequences, epitopes, assay outcomes, or acceptance thresholds.
- Record actual computational methods and versions in run evidence; the task does not prescribe software.
- Do not claim a model-predicted structure proves binding, function, specificity, or clinical suitability.
