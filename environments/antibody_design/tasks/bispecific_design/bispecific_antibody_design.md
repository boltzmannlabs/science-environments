# Task: bispecific_antibody_design

## Description

Design and assess **HER2-directed biparatopic antibody candidates** using **zanidatamab** as the reference antibody. The two binding specificities recognize **extracellular domain II and extracellular domain IV of human HER2 (ERBB2)** in one molecular product.

This task concerns two distinct regions of the same antigen. Compare candidates with the supplied zanidatamab reference evidence, evaluating both binding components and the assembled molecule. A candidate must not be described as equivalent to zanidatamab merely because it recognizes the same two HER2 domains.

## Target

**Target:** Human HER2 (ERBB2), extracellular domain\
**Reference Antibody:** Zanidatamab, a HER2-directed biparatopic antibody\
**Specificity A:** HER2 extracellular domain II\
**Specificity B:** HER2 extracellular domain IV\
**Target Context:** Supplied HER2 constructs and structures, domain/residue mapping, cell-surface accessibility, and receptor arrangement\
**Reference Inputs:** Verified zanidatamab component identities, architecture, domain assignments, and available comparison evidence\
**Architecture:** Explicitly declared chain composition, pairing, valency, linker/hinge, and Fc policy; document any difference from the reference\
**Objective:** Retain both HER2 specificities in a defined molecular product and assess joint engagement, assembly, and developability against the reference

## Design Constraints

- Represent the complete molecule and chain assembly; do not assume every format uses four chains.
- Preserve the domain II/domain IV binding assignments and declared chain composition and valency. Record any permitted changes relative to the zanidatamab reference.
- Assess each arm independently, then assess whole-molecule geometry, assembly, and developability.
- Evaluate joint engagement in the declared receptor arrangement; distinguish affinity, avidity, and occupancy. Do not assume that binding two HER2 domains means both are engaged on the same receptor molecule.
- Check chain mispairing, incomplete assembly, steric occlusion, linker incompatibility, and loss of either specificity.
- Require verified reference-component evidence for reference-derived claims. If zanidatamab inputs are missing, report the gap instead of inventing its sequences or architecture.
- Shortlist only candidates meeting all mandatory arm-level and whole-molecule criteria. A strong first arm cannot compensate for a failed second arm.

## Computational Tool Capabilities

Use verified capabilities supplied by the execution environment in the following order. Record unavailable capabilities and leave their required evidence unresolved.

| Stage | Capability | Expected Evidence |
| --- | --- | --- |
| 1. Validate HER2, reference, and architecture | Check HER2 domain II/IV assignments, zanidatamab reference evidence, named chains, valency, and intended mechanism. | Target/epitope records, chain map, and architecture constraints. |
| 2. Generate or register complete candidates | Create or register HER2 biparatopic candidates within the declared architecture and reference-change policies. | Complete chain sets, HER2 domain assignments, reference/change records, and construct hashes. |
| 3. Assess each arm | Evaluate each binding component against its assigned HER2 domain and corresponding reference evidence. | Separate evidence for each specificity, including uncertainties. |
| 4. Assess assembly and geometry | Evaluate pairing, stoichiometry, steric compatibility, and joint engagement when required. | Whole-molecule assembly checks and mechanism-relevant geometry evidence. |
| 5. Assess function | Analyze supplied mechanism-specific measurements and applicable computational evidence. | Endpoint definitions, controls, target-expression context, and unresolved requirements. |
| 6. Assess product properties | Evaluate whole-molecule stability, aggregation, solubility, expression/assembly, and nonspecific interactions. | Product-level risks alongside individual-arm results. |
| 7. Refine and reassess | Revise permitted components while retaining target assignments and architecture constraints. | Updated chains and repeat assessment of affected arms and the assembled molecule. |
| 8. Select and report | Apply every required arm-level and product-level criterion. | Shortlist supported by both specificities and whole-molecule evidence. |

## Evaluation Metrics

| Criterion | Measurements and Evidence | Evaluation Rule |
| --- | --- | --- |
| Molecular identity | Chain completeness, stoichiometry, HER2 domain assignments, zanidatamab comparison records, and construct hashes. | The candidate must represent one defined molecule with two distinct specificities. |
| Arm-level binding | Separate domain II and domain IV binding evidence, compared with the corresponding zanidatamab reference data under matched conditions. | Evaluate both arms separately; avidity, intrinsic affinity, and occupancy must not be interchanged. |
| Assembly integrity | Predicted pairing/steric conflicts and any supplied measurements of correctly assembled product, fragments, or aggregates. | Keep assembly predictions separate from measured product composition; do not assume a four-chain format. |
| Joint engagement | HER2 receptor geometry, membrane accessibility, and supplied concurrent-binding evidence relative to the zanidatamab reference. | Do not infer reference-like joint engagement from two isolated domain-binding results; verify the declared receptor arrangement. |
| Mechanism | Declared HER2 functional endpoint, matched reference/control evidence, receptor density, and relevant effector/Fc context. | Binding or a dual-target structure alone does not establish the proposed biological effect. |
| Specificity and developability | Panel coverage and whole-molecule stability, aggregation, solubility, expression/assembly, polyreactivity, and relevant immunogenicity descriptors. | Product-level liabilities remain mandatory even when both isolated arms look favorable. |
| Selection and uncertainty | Comparison basis, method revisions, source data, uncertainty, failures, and missing requirements. | A passing arm cannot compensate for a failed mandatory arm or product criterion. |

Use architecture- and mechanism-appropriate criteria from the supplied protocol. Record unsupported endpoints explicitly; do not turn predictive scores into claims of function, delivery, or safety.

## Expected Output

**Format:** `bispecific_design_bundle`\
**Directory:** `08_results/`

- `designed_sequences.fasta`: all chains of eligible molecules with candidate, chain, and arm identifiers.
- `metrics.json`: target/epitope profiles, chain and arm assignments, arm-level and whole-molecule evidence, decisions, limitations, and provenance.
- `shortlist.csv`: rank, candidate ID, construct digest, both arm statuses, and overall eligibility.
- `report.md`: comparison with zanidatamab, HER2 domain II/IV evidence, architecture differences, selection decisions, and missing evidence.
- Supporting structures, annotation records, scoring outputs, and supplied assay data with relative paths and SHA-256 hashes.

Return `NEEDS_INPUT` or `PROTOCOL_REQUIRED` when required inputs or evaluation rules are missing. Preserve failed and unresolved outcomes.

## Important Instructions

- Do not invent zanidatamab sequences, HER2 annotations, reference measurements, or qualification thresholds.
- Report methods and revisions actually used and follow the request's knowledge cutoff.
- Do not equate predicted interface confidence with simultaneous engagement, functional activity, tissue delivery, or safety.
- Assess supplied experimental evidence without claiming that this task performed the experiments.
