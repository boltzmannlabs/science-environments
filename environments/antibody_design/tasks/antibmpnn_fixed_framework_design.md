# Task: antibmpnn_fixed_framework_design

## Description

Design and assess **humanized J3 (huJ3) VHH candidates against HIV-1 gp120** using **AntiBMPNN** for fixed-backbone sequence design and **AlphaFold 3** for monomer and antibody–antigen complex assessment. Execute two configurations: **AB-H3**, using the six-site CDR3 design mask, and **AB-H1**, redesigning CDR1.

Preserve the supplied framework sequence and canonical framework backbone. Generate candidates independently, analyze their sequence frequencies and physical descriptors, and compare their structural assessments with the native parent. Published finalized sequences and mutation identities are withheld.

## Target

**Target:** HIV-1 C1086 gp120 construct represented by PDB 7RI1 polymer entity 1, **382 residues**\
**Reference Antibody:** Humanized J3 (huJ3)\
**Binding Region:** J3-associated gp120 interface with verified antigen mapping\
**Structure and Context:** Supplied huJ3 structure, chain B, **121 residues**, continuously numbered 1–121\
**Reference Inputs:** Native huJ3 sequence and backbone; verified gp120 construct and chain mapping\
**Antibody Format:** Single-domain VHH\
**Objective:** Generate constrained CDR variants and assess sequence frequencies, monomer structures, and gp120 complexes

## Design Constraints

- Use one-based positions in the supplied observed huJ3 chain sequence. Verify correspondence with the structure before generation.
- For AB-H3, allow changes only at **97, 101, 103, 104, 105, and 106**. Preserve every other residue, including the native motif at **98–100**.
- For AB-H1, allow changes only at **26–33**. Preserve all other positions and keep the full length at **121 residues**.
- Preserve framework amino-acid identities and canonical backbone coordinates. Use zero coordinate noise for the initial fixed-backbone evaluation.
- Keep AlphaFold 3 predictions separate from the canonical design. Report predicted framework movement without replacing the fixed input backbone.
- Keep the same antigen construct across candidates and controls. PDB 7RI1 contains llama J3; do not substitute that antibody for the humanized huJ3 parent.
- Assign unique candidate IDs and sequence hashes. Distinguish generated draws, unique sequences, native recoveries, and structurally evaluated candidates.
- Return up to three eligible unique non-native candidates per configuration without filling the shortlist with failed or unresolved candidates.

## Computational Tool Capabilities

Use the following tools and capabilities in order. Record unavailable capabilities and leave their required evidence unresolved.

| Stage | Capability | Expected Evidence |
| --- | --- | --- |
| 1. Validate inputs and baseline | Verify huJ3 identity, antigen construct, native backbone, chain mapping, and design boundaries. | Verified reference records, residue correspondence, and separate CDR1/CDR3 masks. |
| 2. Generate constrained sequences | Use **AntiBMPNN** to sample the declared CDR positions while preserving the remaining sequence and backbone. | Full candidate sequences, edit traces, model identity, sampling parameters, and actual draw counts. |
| 3. Assess sequence frequencies | Use the **AntiBMPNN** frequency-based assessment to group candidates and calculate recovery and physical descriptors. | Unique-sequence counts, frequencies, substitutions, recovery definitions, volume, hydrophilicity, and charge at pH 7.4. |
| 4. Select structural candidates | Select the three most frequent eligible non-native unique candidates per configuration, or all if fewer exist. | Frozen candidate set, frequency ranking, mask compliance, and duplicate exclusions. |
| 5. Assess monomer structures | Use **AlphaFold 3** for each selected candidate and the native huJ3 control. | Five monomer structures per sequence, confidence outputs, local uncertainty, and the selected monomer. |
| 6. Assess target complexes | Use **AlphaFold 3** for each selected candidate–gp120 pair and the native control complex. | Five complex structures per pair, interface confidence, ranking scores, contact maps, clashes, and selected complexes. |
| 7. Select and report | Apply framework, sequence, and structural-completeness requirements before ranking. | Separate configuration shortlists, native comparisons, exclusions, numerical results, and unresolved evidence. |

For the initial environment evaluation, request **1,000 AntiBMPNN sequence draws per configuration**, sampling temperature **0.1**, batch size **10**, the supplied zero-noise model, and inference coordinate noise **0.0**. This fixed-backbone task profile differs from the paper's reported **BN 0.5, T 0.1** profile. Record training-noise and inference-noise settings separately, along with actual random seeds or any seed limitations.

For the larger sampling profile, request **32,768 draws** with batch size **8** and verify the actual output count. The paper reports **147 clusters** for its example; new random runs are not required to reproduce that count.

Use **five AlphaFold 3 samples per sequence or complex** with a declared reconstruction seed of **1** for the initial evaluation. Select monomers by highest mean pLDDT and complexes by highest ranking score. Keep all samples and record MSA/template settings. Original article inputs and seeds are not fully released, so these reconstruction settings do not guarantee historical numerical identity.

## Evaluation Metrics

| Criterion | Measurements and Evidence | Evaluation Rule |
| --- | --- | --- |
| Identity and allowed edits | Full sequence, residue correspondence, substitutions, length, and sequence hash. | Require zero out-of-mask substitutions and unchanged antibody length. |
| Framework backbone | Canonical input coordinates, coordinate-noise setting, and independently predicted framework movement. | Require unchanged canonical framework coordinates and initial inference noise **0.0**. |
| Sampling and frequencies | Requested draws, actual outputs, unique sequences, cluster frequencies, and native recoveries. | Exclude native input/control records from generated-draw counts. |
| Recovery and physical descriptors | Unchanged-identity fraction, volume, hydrophilicity, and charge at pH 7.4. | State the residue set, denominator, and calculation method. |
| Monomer confidence | Per-sample mean pLDDT, local/CDR confidence, missing coordinates, and geometry. | Select the highest-mean-pLDDT monomer. Confidence is not a binding threshold. |
| Complex assessment | Per-sample AlphaFold 3 ranking score, interchain uncertainty, contacts, clashes, and pose consistency. | Select the highest-ranking-score complex and retain its interface uncertainty. |
| Native structural references | huJ3 monomer pLDDT **91.75** and complex ranking score **0.9187**. | Compare the same native parent and declared antigen construct under recorded reconstruction settings. |
| Native experimental reference | huJ3 ELISA EC50 **2.9 nM**. | Keep experimental EC50 separate from structural confidence and SPR KD. |
| Evidence completeness | Five monomer and five complex samples per selected sequence, correct chain mappings, native outputs, method versions, and provenance. | Missing structures or unresolved mappings leave evaluation incomplete. |

Rank eligible candidates separately for each configuration by decreasing selected complex ranking score, then decreasing selected monomer mean pLDDT, then decreasing sequence frequency, with candidate ID as the tie-breaker. This is a confidence ranking rather than an affinity ranking.

## Expected Output

**Format:** `antibody_design_bundle`\
**Directory:** `08_results/antibmpnn_fixed_framework_design/`

- `designed_sequences.fasta`: eligible full-length VHH candidates with candidate and configuration identifiers.
- `metrics.json`: native and candidate records, sequence hashes, sampling parameters, frequencies, physical descriptors, structural measurements, framework checks, rule decisions, exclusions, provenance, and stop reason.
- `shortlist.csv`: ordered `rank,candidate_id,sequence_sha256,case_id` rows, ranked separately for AB-H3 and AB-H1.
- `report.md`: generation counts, structural candidate selection, native comparison, numerical results, ranking rationale, limitations, and unresolved evidence.
- Supporting native input records, design masks, generated sequences, frequency summaries, all predicted structures and confidence outputs, and execution logs with relative paths and SHA-256 hashes.

Keep the native parent out of the designed shortlist. Report missing inputs as `NEEDS_INPUT`, missing evaluation requirements as `PROTOCOL_REQUIRED`, and distinguish incomplete evaluation from a completed result with no qualifying candidates.

## Important Instructions

- Article: Sun et al., *AntiBMPNN: Structure-Guided Graph Neural Networks for Precision Antibody Engineering*, Advanced Science, DOI `10.1002/advs.202504278`.
- Use the supplied sequence-redacted article. Do not retrieve published output sequences, mutation identities, example output tables, or historical variant libraries during design.
- Execute AntiBMPNN and both AlphaFold 3 stages on newly generated candidates. Sequence generation or published-score lookup alone does not complete this task.
- Keep the six-site CDR3 mask distinct from other design intervals described in the study. Design positions are input constraints, not disclosed output mutations.
- Freeze generated outputs, structural candidate selection, and rankings before evaluator comparison with held-out outcomes.
- Record actual methods, model versions, parameters, seed limitations, MSA/template settings, structural mappings, units, and provenance. Structural confidence does not establish experimental affinity or neutralization.
