# Task: rfantibody_fixed_framework_design

## Description

Design and assess VHH antibody candidates against **influenza hemagglutinin** and **respiratory syncytial virus (RSV) site III** using the published **RFantibody** workflow. Use **RFdiffusion** for CDR backbone design, **ProteinMPNN** for CDR sequence design, **antibody-tuned RoseTTAFold2** for structural assessment, and **Rosetta** for interface assessment when included in the evaluation protocol.

Preserve the supplied antibody framework sequence and internal framework backbone. Generate candidates independently and assess each target in a separate campaign. Published finalized sequences and mutation identities are withheld.

## Target

**Targets:** Influenza hemagglutinin and RSV site III\
**Reference Antibody:** Supplied NbBCII10 VHH scaffold\
**Binding Regions:** Supplied target hotspots: HA B146, B170, B177; RSV T305, T456\
**Structure and Context:** Supplied antigen and framework structures with verified chain mapping and CDR annotations\
**Reference Inputs:** Native scaffold sequence, framework backbone, antigen coordinates, and target-specific hotspot mapping\
**Antibody Format:** Single-domain VHH\
**Objective:** Generate CDR designs and evaluate framework preservation, structural consistency, and antigen interfaces

## Design Constraints

- Preserve every framework amino acid and its internal backbone geometry. Whole-antibody rigid-body movement is permitted.
- Design only HCDR1, HCDR2, and HCDR3. Use lengths of **7**, **6**, and **5–13 residues**, respectively, for the declared initial profile.
- Preserve antigen sequence and maintain the case-specific target and hotspot mapping throughout evaluation.
- Verify framework preservation from the actual generated structures. Framework conditioning alone does not establish exact preservation.
- Use a declared framework audit tolerance of **0.01 Å** for both aligned backbone RMSD and maximum backbone-atom displacement. This is a task-specific numerical tolerance.
- Keep independently predicted structures separate from canonical designs. Report predicted framework movement without replacing the fixed design backbone.
- Assign unique candidate IDs and sequence hashes. Return up to three eligible unique candidates per target without filling the shortlist with failed or unresolved designs.

## Computational Tool Capabilities

Use the following tools and capabilities in order. Record unavailable capabilities and leave their required evidence unresolved.

| Stage | Capability | Expected Evidence |
| --- | --- | --- |
| 1. Validate inputs and baseline | Verify scaffold identity, framework/CDR boundaries, antigen chains, and hotspot mapping. | Verified reference sequences, structural inputs, residue correspondence, and edit masks. |
| 2. Generate CDR backbones | Use **RFdiffusion** with the supplied framework and target-specific hotspots. | Generated structures, loop lengths, target poses, and framework-preservation measurements. |
| 3. Design CDR sequences | Use **ProteinMPNN** on the generated backbones with only the declared CDRs designable. | Full candidate sequences, allowed-position edits, and zero framework substitutions. |
| 4. Assess structural consistency | Use **antibody-tuned RoseTTAFold2** to predict the generated antibody–target complexes. | Predicted structures, interface uncertainty, and antibody/CDR consistency measurements. |
| 5. Assess interfaces | Use **Rosetta** when required by the declared scoring protocol. Assess contacts, clashes, and buried surface area. | Protocol-specific interface scores, interface geometry, and score-function identity. |
| 6. Select and report | Apply framework and structural criteria independently for HA and RSV. | Eligible candidates, exclusions, ranking rationale, numerical results, and unresolved evidence. |

For the initial environment evaluation, request **2 backbones × 2 sequences per backbone per target**. Use **50 diffusion steps**, ProteinMPNN temperature **0.2**, coordinate augmentation **0.0**, and **10 RoseTTAFold2 recycles**. Use a hotspot-conditioning proportion of **0.0** during RoseTTAFold2 evaluation and record the actual random seeds. This is a small task evaluation profile rather than the original experimental campaign size.

## Evaluation Metrics

| Criterion | Measurements and Evidence | Evaluation Rule |
| --- | --- | --- |
| Framework sequence | Framework identities, residue correspondence, and candidate sequence hashes. | Require zero framework substitutions. |
| Framework backbone | Framework N, Cα, C, and O RMSD and maximum atom displacement after framework alignment. | Require both ≤ **0.01 Å** on the canonical design. |
| Interface confidence | RoseTTAFold2 mean interchain predicted aligned error, in Å. | Require **< 10 Å** under the declared task protocol. |
| Structural consistency | Target-aligned antibody and CDR Cα RMSDs; framework-aligned antibody and per-CDR Cα RMSDs, in Å. | Require target-aligned antibody RMSD **< 2 Å** as the declared interpretation of the generic consistency filter. Retain the other measurements. |
| Interface quality | Target contacts, hotspot correspondence, buried area, clashes, and Rosetta interface energy when assessed. | Define the scoring protocol before evaluation. Apply the reported **−20** Rosetta energy threshold only with its matching energy protocol. |
| Published structural references | Influenza lead CDR3 RMSD **0.8 Å** and VHH backbone RMSD **1.45 Å** against cryo-EM. | Historical reference outcomes only; sequence-specific comparison belongs to the evaluator after outputs are frozen. |
| Published experimental references | Influenza lead SPR KD **78 nM**; RSV site-III lead SPR KD **1.4 µM**. | Keep experimental references separate from new-candidate predictions. |
| Evidence completeness | Requested draws, successful structures, unique sequences, filters, method versions, and uncertainty. | Every mandatory criterion must pass; report missing stages and genuine zero-pass outcomes. |

Rank eligible candidates separately for each target by increasing interchain predicted aligned error, then increasing target-aligned antibody RMSD, with candidate ID as the tie-breaker. This is a structural ranking, not an experimental affinity claim.

## Expected Output

**Format:** `antibody_design_bundle`\
**Directory:** `08_results/rfantibody_fixed_framework_design/`

- `designed_sequences.fasta`: eligible full-length VHH candidates with target and candidate identifiers.
- `metrics.json`: reference and candidate measurements, framework checks, tool versions, parameters, rule decisions, exclusions, provenance, and stop reason.
- `shortlist.csv`: ordered `rank,candidate_id,sequence_sha256,case_id` rows, ranked separately for HA and RSV.
- `report.md`: execution counts, structural results, ranking rationale, reference comparisons, limitations, and unresolved evidence.
- Supporting input records, generated structures, predicted complexes, confidence outputs, scoring results, and execution logs with relative paths and SHA-256 hashes.

Keep historical designs out of the generated shortlist. Report missing inputs as `NEEDS_INPUT`, missing evaluation requirements as `PROTOCOL_REQUIRED`, and distinguish incomplete evaluation from a completed result with no qualifying candidates.

## Important Instructions

- Article: Bennett et al., *Atomically accurate de novo design of antibodies with RFdiffusion*, Nature, DOI `10.1038/s41586-025-09721-5`.
- Use the supplied sequence-redacted article and supplementary material. Do not retrieve published finalized sequences, mutation identities, or historical output libraries during design.
- Execute RFdiffusion, ProteinMPNN, and antibody-tuned RoseTTAFold2 on newly generated candidates. Published-score lookup alone does not complete this task.
- Freeze generated outputs and rankings before evaluator comparison with held-out designs or experimental outcomes.
- Record actual methods, model versions, parameters, seeds, structural mappings, units, and provenance. Distinguish paper settings from task-specific settings.
- A confident complex or favorable interface score does not establish experimental binding or neutralization.
