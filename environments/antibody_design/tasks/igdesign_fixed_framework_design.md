# Task: igdesign_fixed_framework_design

## Description

Design and structurally assess **Bimagrumab-derived antibody variable regions against ACVR2B** using the published **IgDesign/IgMPNN** workflow. Execute two independent configurations: **IG-H3**, redesigning HCDR3 only, and **IG-H123**, redesigning HCDR1, HCDR2, and HCDR3. Preserve the supplied framework sequence, framework backbone, and heavy/light pairing.

The objective is to test constrained inverse folding, complete antibody-sequence reconstruction, new structure prediction, and numerical self-consistency evaluation. Evaluate the native parent as a baseline and generate all non-native candidates independently. Published output sequences and mutation identities are withheld from this task.

## Target

**Target:** ACVR2B, using the bundled observed antigen construct\
**Reference Antibody:** Bimagrumab, paired heavy and light variable regions\
**Binding Region:** Supplied 5NGV antibody–ACVR2B interface and chain mapping\
**Structure and Context:** IgDesign `examples/5ngv.pdb`; H = antibody heavy, L = antibody light, A = ACVR2B\
**Reference Inputs:** Bundled H chain, **113 observed residues**; L chain, **111 observed residues**; antigen chain, **93 observed residues**\
**Antibody Format:** Paired VH/VL; preserve the entire light chain and all undeclared heavy-chain positions\
**Objective:** Generate constrained CDR sequences, predict their structures, and compare loop/Fv self-consistency with the reference backbone

## Design Constraints

- Use the bundled structure rather than an unprocessed PDB replacement. Store a residue map connecting parsed sequence indices, chain identifiers, and original PDB numbering.
- Interpret IgDesign configuration positions as **zero-based indices in the parsed chain sequence**. Before generation, assert HCDR1 indices **24–31** equal `GYTFTSSY`, HCDR2 **49–56** equal `INPVSGST`, and HCDR3 **95–102** equal `ARGGWFDY`.
- For IG-H3, permit substitutions only at H indices **95–102**. For IG-H123, permit substitutions only at the union of **24–31, 49–56, and 95–102**. Keep loop lengths unchanged.
- Require zero changes in framework, light chain, and antigen. Reconstruct complete VH/VL from the native sequences and generated CDR strings; a CDR-only field is not a complete antibody.
- Keep the supplied design backbone immutable and hash its coordinates. Store canonical designs as the unchanged backbone plus explicitly indexed sequence substitutions. Do not substitute unrestricted folded coordinates for the canonical framework.
- Independent predicted structures may move framework atoms. Measure and report that movement separately from the fixed-backbone generation contract.
- Assign unique case/candidate IDs and sequence-pair hashes, remove duplicate designs from the shortlist, and identify rediscovered native sequences as recoveries.
- Evaluate the native parent under the same tool settings as candidates. Return up to three eligible unique non-native candidates per configuration without filling missing slots with failed or unresolved candidates.

## Computational Tool Capabilities

Use the tools in the following order. [Runbook Section 5](../ANTIBODY_STRUCTURAL_CASE_STUDY_RUNBOOK.md#5-igdesign-cases-ig-h3-and-ig-h123) supplies installation, exact configuration-generation code, and `predict.py` commands. [Section 8.1](../ANTIBODY_STRUCTURAL_CASE_STUDY_RUNBOOK.md#81-fold-the-native-igdesign-baseline-and-locally-generated-candidates) supplies runnable native-baseline prediction, ABodyBuilder2 evaluation, and whole-Fv Kabsch/scRMSD calculation. Reconstruct new candidates only from the current run's generated CDR outputs.

| Stage | Capability | Expected Evidence |
| --- | --- | --- |
| 1. Validate inputs and baseline | Parse bundled H/L/A chains, assert native loop sequences, and define exact immutable/designable positions. | Input hashes, native paired sequences, residue maps, and separate IG-H3/IG-H123 masks. |
| 2. Generate constrained sequences | Execute IgDesign/IgMPNN with `python predict.py` and explicit per-case YAML configurations. | Generated CDR CSVs, resolved YAML/configuration records, model identifiers, seeds, and generation logs. |
| 3. Reconstruct full candidates | Substitute generated loops into the observed native VH while preserving VL and every protected position. | Paired full-length sequences, substitution traces, sequence hashes, and zero out-of-mask changes. |
| 4. Assess antibody structure | Run ABodyBuilder2 on each selected complete VH/VL pair and on the native parent. | New predicted PDBs, local confidence where available, chain maps, geometry findings, and prediction logs. |
| 5. Execute predictor comparison | For the expanded comparison, also run ABodyBuilder3, its language-model-embedding variant where available, and ESMFold. | Predictor-specific structures, model/embedding identities, and matched residue maps. |
| 6. Compute self-consistency | Align whole-Fv Cα atoms to the reference Fv with proper Kabsch rotation; compute region-specific scRMSDs. | HCDR1, HCDR2, HCDR3, HCDR123, and Fv Cα scRMSDs in Å with explicit atom correspondence. |
| 7. Select and report | Audit protected positions, compare candidates and controls, and rank eligible unique candidates using the declared structural rule. | Separate case shortlists, all exclusions, reference differences, and declared coverage of predictor branches. |

**Source:** [IgDesign](https://github.com/AbSciBio/igdesign), inspected commit `70431eef0afaf0496d7d84e22dfdc1980ec9e70e`. Install from `environment.yml`, install the package with `pip install -e .`, and run `bash download_ckpts.sh` in its own environment.

**Models:** Use `ckpts/igdesign_acvr2b_holdout.ckpt` and `ckpts/igmpnn_acvr2b_holdout.ckpt`. Record which role each checkpoint has in the resolved pipeline. These are ACVR2B-holdout checkpoints; do not describe reuse on another antigen as its original target-held-out experiment.

**Required initial execution profile:** Use **2 decoding orders × 2 MPNN samples × 2 language-model samples = 8 requested candidate draws per configuration**, seed **0**, and MPNN/language-model temperatures **0.5/0.5**. For IG-H123 use region order **HCDR3 → HCDR1 → HCDR2**, following the article; record that the checked repository example uses another ordering. Use the H3-only restricted configuration for IG-H3. Fold every successfully reconstructed unique candidate with ABodyBuilder2, plus the native parent. Report actual counts rather than assuming eight unique outputs.

**Expanded comparison profile:** Increase sampling counts to **10 × 10 × 10**, as in the repository defaults, and execute the additional predictor branches on a predeclared matched candidate set. The paper's intended **100 H3 + 100 H123 designs per antigen** is an experimental library size, not the number of stochastic generation draws.

**ESMFold representation:** Use `VH + G*25 + VL`. Remove linker coordinates, recover separate antibody chains, and preserve the residue correspondence before calculating Fv RMSD. Report any predictor trimming or missing coordinates explicitly.

## Evaluation Metrics

| Criterion | Measurements and Evidence | Evaluation Rule |
| --- | --- | --- |
| Allowed sequence changes | Full VH/VL sequences, mutation traces, native identities at every protected index, and sequence hashes. | Require zero out-of-mask substitutions and no sequence-length changes. |
| Fixed design backbone | Input-coordinate hash and immutable backbone/substitution manifest. | Canonical framework coordinates must remain unchanged; predicted framework movement is evaluated separately. |
| Generation behavior | Requested draws, successful reconstructions, unique pairs, native recoveries, and cross-entropy outputs where produced. | Preserve generator metrics and distinguish sampling likelihood from binding evidence. |
| Self-consistency RMSD | Whole-Fv-aligned Cα H1/H2/H3/H123/Fv RMSDs, in Å. | Use the article's Fv alignment, not an automatic framework-only or interface alignment. Record missing-residue exclusions consistently. |
| Structural completeness | Expected chain sequences, chain pairing, atom mapping, missing coordinates, local confidence, and clashes. | Require a valid paired structure and residue correspondence for the chosen metric. A mapping failure leaves the structural evaluation unresolved. |
| Predictor coverage | Completed ABB2, ABB3, embedding-variant, and ESMFold runs with versions/checkpoints. | ABB2 satisfies the initial structural branch. The full predictor comparison remains incomplete until its declared additional branches execute. |
| Native-baseline replay | Newly calculated native-parent metrics versus the reference values below. | Report differences with tool version, atom mapping, and input changes. Non-native published designs are held out. |
| Binding evidence | Released experimental KD and binder labels, kept separate from structural metrics. | Do not convert scRMSD, confidence, or generation score into KD or binding success. |

For the initial task, shortlist eligibility requires a non-native unique candidate, a passing sequence/backbone audit, and a completed ABB2 structural assessment with valid mappings. No paper-supported universal scRMSD binding cutoff is asserted. Rank by increasing ABB2 **H3 scRMSD** for IG-H3 and **HCDR123 scRMSD** for IG-H123, then Fv scRMSD and candidate ID. This is a structural-consistency ranking and does not establish affinity improvement.

The following rounded native-parent values provide a structural baseline. Published designed sequences, their mutation identities, and links to their sequence tables are omitted. Only the native loop sequences already required as inputs are retained.

| Control | HCDR1 / HCDR2 / HCDR3 | H3 scRMSD ABB2 / ABB3 / ESMFold, Å | Fv scRMSD ABB2, Å | Experimental KD, nM |
| --- | --- | --- | --- | --- |
| Native | `GYTFTSSY` / `INPVSGST` / `ARGGWFDY` | 0.298792 / 0.877217 / 0.576831 | 0.435010 | 1.907143 |

Treat native-sequence regeneration as recovery, not a novel improved design. Freeze current-run outputs and rankings before any evaluator compares them with held-out published designs.

## Expected Output

**Format:** `antibody_design_bundle`\
**Directory:** `08_results/igdesign_fixed_framework_design/`

- `designed_sequences.fasta`: eligible paired VH/VL candidates, with case/candidate and chain identifiers.
- `metrics.json`: candidate and control sequences/hashes, checkpoint identities, parameters, reconstruction audits, predictor-specific measurements, decisions, exclusions, provenance, and stop reason.
- `shortlist.csv`: ordered `rank,candidate_id,sequence_sha256,case_id` rows, ranked independently for IG-H3 and IG-H123.
- `report.md`: generation counts, framework preservation, control replay, structural comparisons, predictor coverage, selection rationale, and unresolved evidence.
- `runs/IG-H3/`, `runs/IG-H123/`, and `controls/`: original inputs/hashes, residue maps, design masks, resolved YAMLs, generated CSVs, reconstruction manifests, full sequences, prediction PDBs, atom maps, confidence outputs, normalized `metrics.csv`, and logs.
- Supporting artifacts must have relative paths and SHA-256 hashes. Retain failed predictions and rejected sequence records.

Keep the native control in evaluation records and out of the generated shortlist; native recovery remains ineligible. Report missing inputs as `NEEDS_INPUT` and absent required evaluation definitions as `PROTOCOL_REQUIRED`. State whether the result is `evaluation_incomplete` or `complete_for_declared_profile`, including the completed predictor branches.

## Important Instructions

- Article: [Shanehsazzadeh et al., *IgDesign: In vitro validated antibody design against multiple therapeutic antigens using inverse folding*](../articles_sequence_pages_removed/igdesign_article_reviewed.pdf), DOI `10.1101/2023.12.08.570889`. Use the local page-filtered copy; Appendix A.4 and Appendix C remain available.
- Use [the redacted runbook](../ANTIBODY_STRUCTURAL_CASE_STUDY_RUNBOOK.md) for source-checked commands and the runnable ABB2 native baseline. Actual generated sequences must also be folded.
- During the design phase, do not read published output-sequence datasets, historical variant files, unedited papers, repository example outputs, or evaluator backups. Use source code, checkpoints, native structural inputs, and the local page-filtered article. An evaluator may unblind only after outputs and rankings are frozen.
- The repository's HER2 example is a separate demo. Do not transfer the paper's ACVR2B results or eight-target experimental claims to that demo.
- Freeze structural selection rules before inspecting experimental binder labels or KD. Use experimental data only in a subsequent reference assessment.
- Record actual tools, versions, source/model hashes, seeds, sequences, units, alignment definition, missing residues, hardware, and execution date.
- A fixed-backbone design can receive an unfavorable independent prediction. Preserve and report both artifacts rather than replacing the reference backbone.
