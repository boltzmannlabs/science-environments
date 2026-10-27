# Task: bispecific_antibody_design

**Task family:** bispecific monoclonal antibody design and integrated assessment  
**Task variant:** tool-neutral  
**Status:** benchmark specification; target profiles and a qualified format-specific protocol must be supplied before execution.

## Description

Design and assess a bounded set of bispecific antibody candidates that engage two declared targets or epitopes in one molecular product. The task must begin with a biological rationale for the two binding arms and state whether the desired action requires simultaneous engagement, target bridging, co-blockade, receptor clustering, cell redirection, tissue transport, or another defined mechanism.

The two arms are not independent binders in the final product. Candidate assessment must account for arm specificity, simultaneous binding geometry, valency, chain assembly, molecular format, target context, and the intended functional readout. A strong score for one arm does not compensate for a failed second arm or an incompatible overall geometry.

## Required inputs

Provide exact, hashed profiles for **Target A** and **Target B**, including organism, sequence, construct, structure or explicit structure absence, chain/residue mapping, native presentation context, oligomeric state, post-translational modifications, disease-relevant variants, and epitope policy. State whether both targets are on one cell, on different cells, in circulation, in a tissue barrier, or in another spatial context.

The request must also declare:

- the intended biological mechanism and whether simultaneous occupancy is required;
- the bispecific architecture, chain composition, valency for each target, linker/hinge policy where applicable, and intended Fc/isotype behavior;
- the reference format or parental arm sequences if supplied; if none are supplied, state that the task is de novo and provide an allowed antibody-family/framework policy;
- desired target selectivity, homolog/variant panel, and any acceptable cross-reactivity;
- whether Fc effector function should be active, enhanced, attenuated, or irrelevant, and why;
- the functional assays, controls, target-expression context, and candidate/resource limits;
- the frozen qualification rules, method revisions, output format, and knowledge cutoff.

## Design constraints

- Represent the full bispecific molecule and its chain-pairing/assembly rules, not just isolated variable domains.
- Preserve the declared arm-to-target assignment and distinguish Target A binding from Target B binding in every record.
- Evaluate each arm separately, then evaluate the assembled molecule for simultaneous engagement and the task's required geometry.
- Check for chain mispairing, unintended homodimers, incomplete assembly, linker/hinge incompatibility, steric occlusion, aggregation risk, and loss of either arm's activity.
- Keep valency, avidity, affinity, and cell-surface occupancy distinct. State the target-density and assay context needed to interpret a functional result.
- If the mechanism depends on Fc receptors or immune-cell recruitment, include Fc design, glycosylation/production context, relevant receptor engagement, and a mechanism-specific assay. If the Fc is intentionally silent, verify that the requested action does not rely on Fc activity.
- Do not infer safety, pharmacokinetics, tissue delivery, or clinical dose interval from a binding score or one biodistribution measurement.

## Required assessment stages

| Stage | Required assessment | Decision purpose |
| --- | --- | --- |
| 1. Resolve both targets | Verify each target, construct, state, epitope, chain map, and biological co-localization or spatial relationship. | A dual binder is useful only if both targets exist in the relevant context and can be engaged as intended. |
| 2. Freeze molecular format | Record architecture, chain stoichiometry, arm valency, linkers/hinges, Fc behavior, and assembly constraints. | Interpret candidate geometry and expression in the context of the final molecule. |
| 3. Register parental arms and candidates | Verify chain identity, arm assignment, sequence lineage, and construct completeness. | Prevent arm swapping or incomplete records from producing false dual-binding claims. |
| 4. Assess each arm | Evaluate fold, CDR uncertainty, target-interface evidence, binding evidence, and selectivity for both targets independently. | Confirm that each specificity is supported on its own. |
| 5. Assess the assembled complex | Evaluate simultaneous target engagement, inter-target geometry, steric accessibility, avidity effects, and assembly plausibility. | Isolated arm compatibility does not prove a productive bispecific complex. |
| 6. Assess mechanism | Measure or analyze the mechanism-specific outcome under the declared cell, target-density, stimulus, and effector conditions. | Binding and co-engagement are not equivalent to cell killing, agonism, blockade, transport, or another function. |
| 7. Assess product risks | Evaluate stability, aggregation, solubility, expression/assembly, polyspecificity, immunogenicity, and relevant Fc risks. | Screen the complete construct for liabilities created by combining the two arms. |
| 8. Assess translation when requested | Evaluate exposure, tissue distribution, target-mediated disposition, durability, and safety evidence using suitable assays and controls. | Do not turn a single tissue or timepoint readout into a dosing commitment. |
| 9. Qualify and export | Apply all required gates, preserve unresolved evidence, and provide the complete molecular and evidence bundle. | Support a decision that is traceable to both arms and the intended use. |

## Evaluation metrics

Report each target arm's structure and binding evidence separately; paired-chain and full-construct integrity; dual-target or ternary-complex evidence; simultaneous occupancy or geometry where required; cell-based function; target density and effector/stimulus context; cross-reactivity; assembly and developability; and any PK/distribution measurements requested.

For functional classifiers, provide the independent annotation protocol, number and expertise of raters, consensus definition, per-class confusion matrices, class prevalence, macro- and per-class metrics, confidence intervals, and performance on held-out examples from each relevant stimulus or assay domain. An expert's agreement with model predictions is not independent ground truth. Agreement measured on the model's training-condition images does not by itself show that class meaning is preserved under a mechanistically different stimulus.

For delivery studies, report the analyte, label chemistry, dose, timepoints, tissue processing, assay quantification method, replicate counts, individual observations, means, uncertainty, and control arms. Whole-organ concentration alone does not distinguish vascular retention from parenchymal exposure. Use orthogonal tissue fractionation and spatial evidence where available, and identify label behavior that could decouple measured signal from intact antibody.

All numeric values must be read from supplied data and retain units. If data artifacts are absent, do not fabricate proof-of-work values; return `NEEDS_INPUT`. If replicate data are small or variable, report that limitation and avoid claiming a clean rank order unless the frozen decision rule supports it.

## Expected output

**Format:** `bispecific_design_bundle`  
**Directory:** `08_results/`

- `designed_sequences.fasta`: all chains for each eligible molecule, with candidate, chain, and arm identifiers.
- `metrics.json`: both target profiles; construct/assembly map; arm-level and whole-molecule evidence; functional and developability metrics; failures; uncertainty; and resource/provenance records.
- `shortlist.csv`: rank, candidate ID, paired/full-construct sequence digest, both arm statuses, and overall eligibility.
- `report.md`: mechanism rationale, format choice, arm-by-arm and whole-product evidence, limitations, and recommended next evidence.
- Native structures, assay tables, annotation records, and analysis outputs with relative paths and SHA-256 hashes.

When this task is configured as evidence-only assessment rather than sequence design, omit candidate sequence generation and return the decision/evidence fields requested by that task profile. Never state an assay-derived number unless it is calculated from the supplied artifact and accompanied by its source column, filter, and replicate denominator.

## Important instructions

- Use the [generic target/reference request contract](../config/generic-antibody-request.schema.json) as a starting point, then add a reviewed bispecific architecture and two-target profile before execution.
- If no parental arms, target structures, assay tables, or model-validation data are supplied, report the corresponding evidence as unresolved.
- Do not equate predicted interface confidence with simultaneous binding or mechanism of action.
- Do not infer a weekly or longer dosing interval from a single-dose biodistribution time course alone.
- This task does not prescribe software or experimental protocols. Report only methods actually used and their recorded revisions.
