# Task: igdesign_fixed_framework_design

## Description

Design and assess **Bimagrumab-derived antibody candidates against ACVR2B** using **IgDesign** and **IgMPNN**. Execute two configurations: **IG-H3**, redesigning HCDR3 only, and **IG-H123**, redesigning HCDR1, HCDR2, and HCDR3. Assess structural self-consistency using **ABodyBuilder2**, with **ABodyBuilder3** and **ESMFold** for the expanded predictor comparison.

Preserve the supplied framework sequence, framework backbone, and heavy/light pairing. Evaluate the native parent alongside independently generated candidates. Published finalized sequences and mutation identities are withheld.

## Target

**Target:** ACVR2B\
**Reference Antibody:** Bimagrumab, paired VH and VL\
**Binding Region:** Supplied antibody–ACVR2B interface represented by PDB 5NGV\
**Structure and Context:** Supplied processed 5NGV structure; H = antibody heavy, L = antibody light, A = antigen\
**Reference Inputs:** Observed heavy-chain sequence of **113 residues**, light-chain sequence of **111 residues**, and antigen sequence of **93 residues**\
**Antibody Format:** Paired antibody variable domains\
**Objective:** Generate constrained CDR variants and assess their structural consistency against the native reference backbone

## Design Constraints

- Use the supplied processed structure and preserve its chain mapping and observed-residue correspondence.
- Number design positions using zero-based indices in the observed heavy-chain sequence. Verify native HCDR1 **24–31**, HCDR2 **49–56**, and HCDR3 **95–102** before generation.
- For IG-H3, allow changes only at **95–102**. For IG-H123, allow changes only at **24–31, 49–56, and 95–102**. Keep loop lengths unchanged.
- Preserve the entire light chain, antigen sequence, and every heavy-chain residue outside the selected design mask.
- Keep the canonical backbone unchanged. Reconstruct complete VH/VL candidates from the native inputs and generated CDRs; CDR fragments alone are insufficient.
- Retain independent predictions as evaluation structures. Measure predicted framework movement without replacing the canonical framework coordinates.
- Assign unique candidate IDs and sequence-pair hashes. Treat regenerated native sequences as recoveries.
- Return up to three eligible unique non-native candidates per configuration without filling the shortlist with failed or unresolved candidates.

## Computational Tool Capabilities

Use the following tools and capabilities in order. Record unavailable capabilities and leave their required evidence unresolved.

| Stage | Capability | Expected Evidence |
| --- | --- | --- |
| 1. Validate inputs and baseline | Verify Bimagrumab/ACVR2B identity, native sequences, chain pairing, and design boundaries. | Verified inputs, residue correspondence, native baseline, and configuration-specific edit masks. |
| 2. Generate CDR candidates | Use **IgDesign** with **IgMPNN** to generate sequences within the declared mask. | Generated CDRs, model identity, generation scores, sampling parameters, and actual draw counts. |
| 3. Reconstruct complete antibodies | Incorporate generated CDRs into the native paired variable domains. | Full VH/VL sequences, edit traces, unique sequence hashes, and zero out-of-mask changes. |
| 4. Assess antibody structures | Use **ABodyBuilder2** for the native parent and generated candidates. | Predicted paired structures, residue mapping, confidence where available, and geometry findings. |
| 5. Compare structure predictors | For the expanded comparison, use **ABodyBuilder3**, including its ProtT5-embedding variant, and **ESMFold** on the same candidate set. | Predictor-specific structures, model identities, and comparable structural measurements. |
| 6. Measure structural self-consistency | Align whole-Fv Cα atoms using Kabsch superposition and calculate region-specific RMSDs. | HCDR1, HCDR2, HCDR3, HCDR123, and Fv self-consistency RMSDs, in Å. |
| 7. Select and report | Apply edit, backbone, structural-completeness, and ranking requirements. | Separate configuration shortlists, native comparisons, exclusions, and unresolved evidence. |

For the initial environment evaluation, request **2 decoding orders × 2 IgMPNN samples × 2 language-model samples = 8 candidate draws per configuration**. Use sampling temperatures **0.5/0.5** and seed **0**. Generate HCDR3 before HCDR1 and HCDR2 in the three-loop configuration. Use the supplied ACVR2B-holdout models. Fold all successfully reconstructed unique candidates and the native parent with ABodyBuilder2.

For the expanded comparison, use **10 × 10 × 10** sampling draws and execute the additional structure predictors on a predeclared matched candidate set. For ESMFold, join VH and VL using **25 glycine residues**, then exclude the linker and restore chain correspondence before Fv evaluation. The paper's intended **100 H3 and 100 H123 designs per antigen** is an experimental library size, not a generation-draw count.

## Evaluation Metrics

| Criterion | Measurements and Evidence | Evaluation Rule |
| --- | --- | --- |
| Identity and allowed edits | Paired sequences, observed-residue numbering, sequence lengths, framework edits, and sequence hashes. | Require unchanged pairing and zero substitutions outside the configuration-specific mask. |
| Framework backbone | Canonical input coordinates and sequence-substitution records; independent predicted framework movement. | Require unchanged canonical framework coordinates. Keep prediction movement as a separate assessment. |
| Generation behavior | Requested draws, successful reconstructions, unique candidates, native recoveries, and generation scores. | Distinguish sampling scores from binding evidence. |
| Structural self-consistency | Whole-Fv-aligned Cα RMSDs for each heavy-chain CDR, HCDR123, and Fv, in Å. | Follow the paper's Fv alignment and consistently handle missing residues. |
| Structure quality | Chain pairing, sequence correspondence, missing coordinates, local confidence, and clashes. | Require a valid paired structure and residue correspondence before accepting its RMSD. |
| Predictor coverage | Completed ABodyBuilder2, ABodyBuilder3, ProtT5-embedding variant, and ESMFold assessments. | ABodyBuilder2 completes the initial structural branch; report additional predictor branches separately. |
| Native structural references | Native H3 RMSD: ABodyBuilder2 **0.298792 Å**, ABodyBuilder3 **0.877217 Å**, ESMFold **0.576831 Å**; native ABodyBuilder2 Fv RMSD **0.435010 Å**. | Compare the native baseline under recorded versions and mappings. Historical equality is not guaranteed across model versions. |
| Native experimental reference | Native parent KD **1.907143 nM**. | Keep this experimental reference separate from candidate structural predictions. |
| Evidence completeness | Method versions, parameters, atom correspondence, units, input provenance, exclusions, and uncertainty. | All mandatory criteria must pass; preserve missing and failed evaluations. |

Rank eligible non-native candidates by increasing ABodyBuilder2 H3 RMSD for IG-H3 and HCDR123 RMSD for IG-H123, then Fv RMSD and candidate ID. No universal binding threshold is asserted; this ranks structural consistency rather than affinity.

## Expected Output

**Format:** `antibody_design_bundle`\
**Directory:** `08_results/igdesign_fixed_framework_design/`

- `designed_sequences.fasta`: eligible paired VH/VL candidates with candidate and chain identifiers.
- `metrics.json`: native and candidate measurements, sequence hashes, generation parameters, framework checks, predictor coverage, rule decisions, exclusions, provenance, and stop reason.
- `shortlist.csv`: ordered `rank,candidate_id,sequence_sha256,case_id` rows, ranked separately for IG-H3 and IG-H123.
- `report.md`: generation counts, native comparison, structural results, ranking rationale, limitations, and unresolved evidence.
- Supporting input records, reconstructed sequences, predicted structures, residue mappings, confidence outputs, and execution logs with relative paths and SHA-256 hashes.

Keep the native parent out of the designed shortlist. Report missing inputs as `NEEDS_INPUT`, missing evaluation requirements as `PROTOCOL_REQUIRED`, and distinguish incomplete evaluation from a completed result with no qualifying candidates.

## Important Instructions

- Article: Shanehsazzadeh et al., *IgDesign: In vitro validated antibody design against multiple therapeutic antigens using inverse folding*, DOI `10.1101/2023.12.08.570889`, version 2.
- Use the supplied sequence-redacted article. Do not retrieve published designed sequences, mutation identities, or historical output libraries during generation.
- Generate candidates independently and run the structural predictors. A published-results lookup alone does not complete this task.
- Keep the supplied ACVR2B model and target provenance explicit; do not transfer results to another antigen without a separate evaluation.
- Freeze candidate selection and ranking before inspecting held-out experimental outcomes.
- Record actual methods, model versions, parameters, seeds, structural mappings, units, and provenance. Structural confidence and self-consistency do not establish experimental binding.
