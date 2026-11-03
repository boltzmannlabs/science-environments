# Task: antibmpnn_fixed_framework_design

## Description

Design and structurally assess **humanized J3 (huJ3) VHH candidates against HIV-1 gp120** using the published **AntiBMPNN** workflow: fixed-backbone sequence sampling, frequency/descriptor analysis, **AlphaFold 3 monomer prediction**, and **AlphaFold 3 antigen-complex prediction**. Execute **AB-H3**, using the paper's Figure 2 six-site CDR3 mask, and **AB-H1**, redesigning CDR1.

The objective is to evaluate constrained inverse folding and real structural-model execution while preserving the parent framework sequence and canonical framework backbone. Compare new predictions with explicitly identified published structural references. A high-confidence model is structural evidence and must not be reported as measured binding or neutralization.

## Target

**Target:** HIV-1 C1086 gp120 construct represented by PDB **7RI1 polymer entity 1**, 382 residues\
**Reference Antibody:** Humanized J3, supplied as AntiBMPNN `inputs/HuJ3/HuJ3.pdb`\
**Binding Region:** J3-associated gp120 interface; assess contacts in the complex prediction using the declared antigen mapping\
**Structure and Context:** Bundled huJ3 chain **B**, **121 residues**, continuously numbered 1–121; separate gp120 sequence/context for AF3 complex prediction\
**Reference Inputs:** Full huJ3 sequence below; use 7RI1 entity 1 for the explicit public antigen reconstruction\
**Antibody Format:** Single-domain VHH, without a light chain\
**Objective:** Generate masked huJ3 variants, analyze sequence frequencies, and execute matched monomer/complex structural assessments of candidates and controls

## Design Constraints

- Use this native sequence and assert it against the supplied PDB before sampling:

  ```text
  EVQLVESGGGLVQPGGSLRLSCAASGSIFNQYAMAWFRQAPGKEREFVAGMGAVPHYGEFVKGRFTISRDNSKNTVYLQMNSLRAEDTAVYYCARSKSTYISYNSNGYDYWGQGTLVTVSS
  ```

- Interpret AntiBMPNN mask positions as **one-based parsed-chain positions**. For the supplied continuous chain B, these coincide with the displayed residue numbers.
- For AB-H3, allow changes only at **97, 101, 103, 104, 105, 106**. Preserve every other residue, including **STY at 98–100**. Assert native CDR3 segment **94–110 = `ARSKSTYISYNSNGYDY`**.
- For AB-H1, allow changes only at **26–33**, whose native sequence is `GSIFNQYA`. Preserve CDR3 and every other position.
- Keep the canonical input backbone immutable, with zero inference-coordinate noise in the initial task. Store full sequences plus the immutable backbone and substitution map; independent AF3 predictions are separate evaluation artifacts.
- Preserve the antigen sequence and construct across all candidate/control evaluations. **7RI1 contains llama J3, not huJ3**; do not substitute its VHH sequence for the humanized design parent.
- Assign unique case/candidate IDs and full-sequence hashes. Count sequence draws, unique sequences, native recoveries, selected structures, and failed evaluations separately.
- Return up to three eligible non-native unique candidates per configuration. Missing or failed candidates must not be used to fill the shortlist.

## Computational Tool Capabilities

Use the tools in the following order. [Runbook Section 6](../ANTIBODY_STRUCTURAL_CASE_STUDY_RUNBOOK.md#6-antibmpnn-cases-ab-h3-and-ab-h1) provides the checked installation, preprocessing, sampling, parsing, and AF3 commands. [Section 8.2](../ANTIBODY_STRUCTURAL_CASE_STUDY_RUNBOOK.md#82-construct-concrete-antibmpnn-af3-structural-replay-inputs) creates native huJ3 AF3 inputs using the verified antigen entity. Prepare non-native inputs only from newly generated candidates.

| Stage | Capability | Expected Evidence |
| --- | --- | --- |
| 1. Validate inputs and baseline | Parse huJ3 chain B, assert native segments, retrieve the gp120 entity sequence, and record numbering. | Parent/antigen sequences and hashes, PDB atom map, entity provenance, and two explicit mutation masks. |
| 2. Prepare constrained design inputs | Run `parse_multiple_chains.py`, `assign_fixed_chains.py`, and `make_fixed_positions_dict.py`. | Parsed JSONL, chain-designability JSONL, and fixed-position JSONL with the exact mutable complement verified. |
| 3. Generate sequences | Run `Running_AntiBMPNN_run.py` separately for AB-H3 and AB-H1. | Full generated sequences, chosen checkpoint, noise/temperature settings, generation logs, and actual output counts. |
| 4. Analyze sequence frequencies | Run `parsing_design_result.py` on the case-specific CDR segment and independently audit full-sequence uniqueness. | Frequency tables, counts, substitutions, recovery definition, volume/hydrophilicity descriptors, and charge at pH 7.4. |
| 5. Assess monomer structures | Execute AF3 with five samples per selected candidate/control. | All five structures and confidence outputs, per-sample mean pLDDT, and the pLDDT-selected monomer. |
| 6. Assess antigen complexes | Execute AF3 with the same candidate and declared gp120 input, five samples per pair. | All complex structures, ranking scores, confidence outputs, selected complex, contact map, clashes, and uncertain regions. |
| 7. Select and report | Apply mask/structural-completeness rules and report frequency plus structural-confidence rankings. | Separate case shortlists, matched control comparisons, exclusions, and clearly bounded conclusions. |

**Source:** [AntiBMPNN](https://github.com/zeysun/AntiBMPNN), inspected commit `7e6329ba3c317e7344c6b09add72dea2390af39a`. Run `bash Initialize.sh`, activate `mlfold`, and execute the sampling command from **`AntiBMPNN/example`**. The pinned runner resolves weights using `../antibmpnn_model_weights`; its `--path_to_model_weights` argument is not used by the implementation.

**Required initial generation profile:** For each case request **1,000 sequences**, batch size **10**, temperature **0.1**, model **`antibmpnn_000`**, and inference backbone noise **0.0**. Use `--specify_non_fixed` when giving the mutable positions to `make_fixed_positions_dict.py`; otherwise the mask semantics are reversed. Parse CDR3 positions **94–110** for AB-H3 and CDR1 **26–33** for AB-H1.

**Sampling controls:** The pinned runner generates an internal random seed independently of `--seed`; preserve the actual behavior and do not claim determinism from that argument. A deterministic adapter must retain its patch and actual seed. The paper's reported **BN = 0.5** and **T = 0.1** profile must remain distinct from the task's explicit zero-inference-noise adaptation; checkpoint training noise and runtime coordinate noise are separate settings.

**Larger sampling profile:** To request **32,768** actual draws, use batch size **8**. The runner floors the number of batches; batch size 10 would produce only **32,760** draws.

**Structural candidate selection:** Before examining experimental outcomes, select the **three most frequent non-native unique full sequences per case**, or all if fewer exist, after mask auditing. Break frequency ties by candidate ID. Run both AF3 stages on this frozen set and the native huJ3 control. Published mutant controls and their mutation identities are withheld; do not reconstruct them from paper results.

**AF3 execution profile:** Use a declared reconstruction seed **1** and **five diffusion samples per seed**, `--num_diffusion_samples 5`. Select monomers by highest mean `atom_plddts` and complexes by highest `ranking_score`. Save all samples and use separate output directories. Use the actual AF3 code/model/database paths from the environment. Original article seeds, MSAs, and exact antigen input files are not fully released, so this public reconstruction is not a promise of identical historical numbers.

## Evaluation Metrics

| Criterion | Measurements and Evidence | Evaluation Rule |
| --- | --- | --- |
| Sequence-mask compliance | Full 121-residue sequences, mutable-position lists, fixed-position dictionaries, and substitution traces. | Require zero substitutions outside each case's mask, unchanged sequence length, and preserved AB-H3 STY motif. |
| Canonical backbone preservation | Input-coordinate hash, canonical backbone/substitution manifest, and actual inference-noise setting. | Require unchanged canonical framework coordinates and noise **0.0** for the initial task. Report independent predicted framework movement separately. |
| Sampling and frequencies | Draw count, unique full-sequence count, cluster frequencies, and frequency-parser outputs. | Exclude the synthetic native row with count zero and the original native FASTA record from generated-draw counts. |
| Sequence recovery and descriptors | Fraction of unchanged identities on an explicitly named residue set, volume, hydrophilicity, and charge at pH 7.4. | State the denominator and descriptor implementation. Distinguish full-sequence, segment, and mutable-site recovery. |
| Monomer confidence | Mean pLDDT of each AF3 sample, with local/CDR confidence retained where available. | Select the highest-mean-pLDDT monomer. No universal binding threshold is asserted. |
| Complex confidence | Each sample's `ranking_score`, interchain uncertainty, mapped contacts, and geometry. | Select the highest-ranking-score complex. Confidence alone does not establish binding. |
| Structural completeness | Correct candidate/antigen chains, complete expected sequence mapping, five monomer samples, five complex samples, and native confidence outputs. | Incomplete outputs or unresolved mappings leave structural evaluation incomplete. Report clashes and uncertain loops explicitly. |
| Native reference comparison | New native huJ3 monomer/complex scores minus the baseline values below. | Compare the same parent and declared construct/protocol. Preserve reconstruction/version differences. |
| Experimental comparison | Supplied ELISA EC50 values, separate from AF3 confidence. | Do not equate EC50 with SPR KD or predicted affinity. |

Use the native-parent values as structural references. Published output sequences and mutation-labelled rows are withheld.

| Reference | Monomer pLDDT | Complex ranking_score | Experimental ELISA EC50, nM |
| --- | --- | --- | --- |
| huJ3 | 91.75 | 0.9187 | 2.9 |

The paper's example reports **32,768 draws** and **147 clusters**. Its top output sequence, output-specific descriptors, and substitution list are withheld. Calculate frequencies and descriptors from the current run's independently generated sequences.

Shortlist eligibility requires a valid non-native unique sequence, passing framework/mask checks, both completed AF3 stages, and valid structure/sequence correspondence. Rank eligible candidates by decreasing selected complex `ranking_score`, then decreasing monomer mean pLDDT, frequency, and candidate ID. This is a declared confidence ranking, not a binding-affinity ranking. Report zero eligible candidates when appropriate.

## Expected Output

**Format:** `antibody_design_bundle`\
**Directory:** `08_results/antibmpnn_fixed_framework_design/`

- `designed_sequences.fasta`: eligible full-length VHH candidates with case/candidate identifiers.
- `metrics.json`: every generated/selected/control record, sequence hashes, checkpoint identity, actual sampling settings, frequency descriptors, per-sample AF3 scores, mask audits, decisions, provenance, and stop reason.
- `shortlist.csv`: ordered `rank,candidate_id,sequence_sha256,case_id` rows, with rankings evaluated separately for AB-H3 and AB-H1.
- `report.md`: draw/unique counts, structural candidate selection, framework checks, monomer/complex results, published-reference differences, uncertainty, and unresolved evidence.
- `runs/AB-H3/`, `runs/AB-H1/`, and `controls/`: native inputs/hashes, residue maps, design masks, parsed/chain/fixed JSONLs, FASTAs, frequency tables ending `_Paresd_Result.csv`, resolved parameters, AF3 input JSONs, all sample structures/confidence outputs, normalized `metrics.csv`, and execution logs.
- Supporting artifacts must have relative paths and SHA-256 hashes. Keep downloaded gp120 entity metadata as provenance, separate from AF3 job JSONs.

Keep controls out of the designed shortlist. Report missing inputs as `NEEDS_INPUT`, undefined required evaluation rules as `PROTOCOL_REQUIRED`, and distinguish `constraint_failed`, `evaluation_incomplete`, and `complete_for_declared_profile`. Sequence generation or published-score lookup without actual AF3 monomer and complex execution is incomplete.

## Important Instructions

- Article: [Sun et al., *AntiBMPNN: Structure-Guided Graph Neural Networks for Precision Antibody Engineering*](../articles_sequence_pages_removed/antibmpnn_article_sequence_pages_removed.pdf), Advanced Science, 2025, DOI `10.1002/advs.202504278`. Use the local page-filtered copy. Output-bearing supplementary tables are withheld during generation.
- Use [the redacted runbook](../ANTIBODY_STRUCTURAL_CASE_STUDY_RUNBOOK.md) for checked commands, input construction, framework auditing, and distinctions between design masks.
- During the design phase, do not read published output-sequence tables, repository README output examples, precomputed example results, unedited papers, or evaluator backups. Use source code, checkpoints, native structural inputs, and the local page-filtered article. Unblind only after freezing outputs and rankings.
- The repository example's mutable interval 102–106 is different from the Figure 2 six-site mask. Do not silently replace one with the other.
- D6–CD16 is outside this task because the supplied repository lacks a ready D6 starting PDB. Its reported output mutation details are withheld.
- Freeze candidate selection and ranking before inspecting experimental outcomes. Distinguish generated-candidate predictions from the native control's measured baseline.
- Record actual tool versions, checkpoint hashes, seeds/seed limitations, AF3 MSA/template settings, hardware, atom maps, metric units, and execution date. Never invent missing outcomes or infer measured affinity from confidence.
