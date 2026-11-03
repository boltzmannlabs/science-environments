# Task: rfantibody_fixed_framework_design

## Description

Design and structurally assess antigen-binding VHH candidates using the published **RFantibody** pipeline: **RFdiffusion → ProteinMPNN → antibody-tuned RoseTTAFold2 (RF2)**. Execute two independent cases: **RF-HA**, targeting influenza hemagglutinin, and **RF-RSV**, targeting respiratory syncytial virus site III. Preserve the supplied VHH framework sequence and internal framework backbone in every canonical design.

The objective is to test actual structure generation, constrained sequence design, structural prediction, and filtering. Run the molecular tools and retain their native outputs. Compare observed results with the appropriate published references without assigning historical experimental affinities to newly generated candidates.

## Target

**Targets:** Influenza hemagglutinin and RSV site III, in separate runs\
**Reference Antibody:** Bundled VHH scaffold `h-NbBCII10.pdb`\
**Binding Regions:** HA hotspots `B146,B170,B177`; RSV hotspots `T305,T456`, using the supplied input chain identifiers\
**Structure and Context:** RFantibody `scripts/examples/example_inputs/flu_HA.pdb` and `rsv_site3.pdb`; preserve input antigen sequences and record output chain mapping\
**Reference Inputs:** `scripts/examples/example_inputs/h-NbBCII10.pdb`, including its framework/CDR labels\
**Antibody Format:** Single-domain VHH; design H1, H2, and H3 without introducing a light chain\
**Objective:** Generate antigen-specific CDR designs, assess structural consistency and interfaces, and independently verify strict framework preservation

## Design Constraints

- Keep the framework amino-acid sequence unchanged. Permit CDR lengths `H1:7,H2:6,H3:5-13` and edits only within those loops.
- Keep framework N/CA/C/O coordinates unchanged up to whole-antibody rigid-body motion and the declared numerical tolerance. Use **0.01 Å** for both framework backbone RMSD and maximum aligned atom displacement in this task; this is a task-specific audit tolerance.
- Map framework residues using the HLT annotations and ordered framework correspondence. Variable loop lengths make raw PDB residue-number matching insufficient.
- Audit generated diffusion coordinates and subsequent canonical design artifacts. Framework conditioning alone does not prove exact coordinate preservation. Report `constraint_failed` if the actual generated framework violates the tolerance; do not overwrite coordinates to manufacture a pass.
- Keep independent RF2 predictions as evaluation artifacts. Their framework movement is a separate measurement from the canonical design constraint.
- Use distinct case/candidate IDs, sequence hashes, output directories, and antigen provenance. Do not reuse the HA designs as RSV designs.
- Return up to three eligible unique candidates per target after applying every mandatory criterion. A zero-candidate shortlist is an acceptable completed evaluation when all candidates fail.

## Computational Tool Capabilities

Use the following published tools in order. The complete checked command sequence is in [runbook Sections 3–4](../ANTIBODY_STRUCTURAL_CASE_STUDY_RUNBOOK.md#4-rfantibody-cases-rf-ha-and-rf-rsv); preserve the pinned command interface.

| Stage | Capability | Expected Evidence |
| --- | --- | --- |
| 1. Validate inputs and baseline | Parse scaffold, antigen chains, HLT/CDR annotations, hotspot identities, and framework atoms. | Input hashes, observed sequences, framework map, design mask, and verified hotspot residues. |
| 2. Generate CDR backbones | Run `uv run rfdiffusion` separately for HA and RSV using the scaffold and case-specific hotspots. | Backbone quivers, extracted PDBs, diffusion logs, candidate tags, and framework-coordinate audit. |
| 3. Design CDR sequences | Run `uv run proteinmpnn` on each backbone with only `H1,H2,H3` designable. | Sequence quivers, full-length sequences, sequence masks, and zero framework-sequence changes. |
| 4. Predict target complexes | Run `uv run rf2` on the actual generated sequences and backbone contexts. | RF2 prediction quivers, extracted structures, confidence values, and structural-consistency metrics. |
| 5. Extract and assess metrics | Run `qvscorefile`, `qvextract`, and `qvls`; inspect the actual sibling `.sc` score table. | Traceable backbone-to-sequence-to-prediction mapping, all native RMSD/pAE columns, and normalized metrics. |
| 6. Assess interfaces when enabled | Run an explicitly recorded Rosetta interface-analysis protocol on prediction copies. | Interface energy, buried area, score-function/protocol identity, and native scoring outputs. |
| 7. Select and report | Apply the declared framework and RF2 filters, then rank eligible unique candidates. | Per-target shortlist, exclusions, published-reference comparisons, and unresolved evidence. |

**Source:** [RFantibody](https://github.com/RosettaCommons/RFantibody), inspected commit `3e5a5bb1cb98befde9fc049ae3ff58cabb491f67`. Use `bash include/download_weights.sh` and `uv sync` in its own environment before execution. Resolve actual paths through `AGENT_AB_ROOT=/home/boltzmann12/Srivani/Agent_Sci_Ab`.

**Required initial execution profile:** Run **2 diffusion backbones × 2 MPNN sequences per backbone per target**, yielding four requested sequence draws per target. Use diffusion **50 steps**, MPNN temperature **0.2**, MPNN coordinate augmentation **0.0**, RF2 **10 recycles**, RF2 hotspot-show proportion **0.0**, deterministic generation flags where supported, and RF2 seed **1**. These small counts and explicit zero augmentation form the runbook's smoke/adaptation profile; record actual successful and unique counts.

**Larger comparison profile:** The repository HA pipeline requests **1,000 backbones × 4 sequences**. The article reports screens of **9,000 designs per target** in high-throughput campaigns. Do not equate these scales or claim exact historical reproduction from the initial profile. The RSV VHH-only loop specification is an adaptation of the repository's RSV example.

## Evaluation Metrics

| Criterion | Measurements and Evidence | Evaluation Rule |
| --- | --- | --- |
| Framework sequence | Residue identities outside annotated H1/H2/H3, framework correspondence, and candidate hashes. | Require zero framework substitutions and complete correspondence. |
| Canonical framework backbone | Framework N/CA/C/O RMSD and maximum displacement after proper framework-only Kabsch alignment. | Require both ≤ **0.01 Å**. Report a strict-constraint failure separately from prediction quality. |
| Interface confidence | RF2 `interaction_pae`, in Å. | Require **< 10 Å**, following the repository's pAE guidance. |
| Structural consistency | `target_aligned_antibody_rmsd`, `target_aligned_cdr_rmsd`, `framework_aligned_antibody_rmsd`, `framework_aligned_cdr_rmsd`, and per-loop equivalents, in Å. | Use `target_aligned_antibody_rmsd < 2 Å` as the task's explicit interpretation of the repository's generic RMSD filter. Retain every native RMSD column. |
| Pose and geometry | Antigen contacts, hotspot correspondence, missing coordinates, interface clashes, and uncertain loops. | Record findings and atom selections. Declare any additional acceptance thresholds before examining outcomes. |
| Rosetta interface assessment | Protocol-specific interface energy in REU and buried surface area in Å². | Optional for the initial profile. The repository mentions ddG < −20; apply that only when reproducing the same defined ddG protocol. Do not transfer it to another energy calculation. |
| Counts and selection | Requested draws, generated backbones, sequence outputs, unique sequences, prediction successes, and filter passes. | Keep all counts separate. Missing required metrics leave a candidate unresolved. |
| Published structural reference | A particular influenza design has CDR3 RMSD **0.8 Å** and VHH backbone RMSD **1.45 Å** versus cryo-EM. | Treat these as historical reference outcomes. An evaluator may compare the held-out design after outputs are frozen; the design agent must not recover its sequence. |
| Published experimental references | Influenza lead SPR KD **78 nM**; RSV site-III lead SPR KD **1.4 µM**. | Record as experimental references only. Do not attach either value to a newly generated candidate. |

Require the framework audit and both declared RF2 thresholds for shortlist eligibility. Rank passing candidates by increasing `interaction_pae`, then increasing `target_aligned_antibody_rmsd`, with candidate ID as a deterministic tie-breaker. This ranking is a task protocol, not a claim about the paper's historical selection algorithm.

## Expected Output

**Format:** `antibody_design_bundle`\
**Directory:** `08_results/rfantibody_fixed_framework_design/`

- `designed_sequences.fasta`: eligible full-length VHH sequences with case/candidate identifiers.
- `metrics.json`: all reference and candidate records; tool commits/checkpoint hashes; parameters; structural scores; framework audits; rule decisions; exclusions; and stop reason.
- `shortlist.csv`: ordered `rank,candidate_id,sequence_sha256,case_id` rows, with ranks evaluated separately for HA and RSV.
- `report.md`: per-target execution counts, structural-filter results, framework preservation, reference comparisons, ranking rationale, and unresolved evidence.
- `runs/RF-HA/` and `runs/RF-RSV/`: manifests, input copies/hashes, residue maps, design masks, resolved parameters, logs, quivers, extracted structures, `.sc` tables, normalized `metrics.csv`, and any Rosetta outputs.
- Supporting artifacts must have relative paths and SHA-256 hashes. Preserve failed candidates in evaluation records.

Keep the scaffold and historical leads out of the designed shortlist. Report missing molecular inputs as `NEEDS_INPUT`, missing required evaluation definitions as `PROTOCOL_REQUIRED`, and distinguish `constraint_failed`, `evaluation_incomplete`, and `complete_for_declared_profile`. Completion requires actual new outputs from all three molecular stages for both targets and a report of any unsuccessful stage.

## Important Instructions

- Article: [Bennett et al., *Atomically accurate de novo design of antibodies with RFdiffusion*](../articles_sequence_pages_removed/rfantibody_article_sequence_pages_removed.pdf), DOI `10.1038/s41586-025-09721-5`; online 2025, Nature volume 649, 2026. Use the local page-filtered article and [supplement](../articles_sequence_pages_removed/rfantibody_supplement_sequence_pages_removed.pdf).
- Read [runbook Sections 4 and 8.3–8.4](../ANTIBODY_STRUCTURAL_CASE_STUDY_RUNBOOK.md#4-rfantibody-cases-rf-ha-and-rf-rsv) before execution. The inspected Rosetta helper has an author-local XML path and an undefined filter reference; use an audited adapter or the explicitly labelled InterfaceAnalyzer recipe rather than assuming the helper is turnkey.
- During the design phase, do not read historical output-sequence datasets, deposited final-design sequences, unedited papers, output-bearing figure panels, or evaluator backups. Unblind only after freezing generated outputs and rankings.
- Record whether each setting is paper-reported, repository-default, smoke, or adaptation. Preserve differences between the current repository interface and the original article workflow.
- Keep historical lead rankings and experimental outcomes out of new-candidate selection; use them only for the frozen reference comparison.
- Record actual model/tool versions, checkpoint SHA-256 hashes, seeds, hardware, units, atom maps, and execution date. Missing observations remain missing.
- A high-confidence complex or favorable Rosetta score does not establish experimental affinity or neutralization.
