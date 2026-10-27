# Task: base_editing_grna_001

## Description

Design and prioritize guide RNAs for CRISPR base editing of a user-specified genetic target. Generate compatible candidates, predict editing efficacy, assess bystander edits and rank guide–editor combinations using the available evidence.

## User-Specified Inputs

| Input                           | What to provide                                                                                    |
| ------------------------------- | -------------------------------------------------------------------------------------------------- |
| Project                         | Select an available tool project, such as `Demo`.                                                |
| Experiment name                 | User-defined name for this run.                                                                    |
| Organism                        | Supported species containing the target gene.                                                      |
| Gene ID                         | Identifier accepted by the CRISPR Base Editing tool.                                               |
| Reference genome                | Assembly/version matching genomic coordinates and the Bowtie index.                                |
| Transcript                      | Transcript accession/version; provide one or accept the tool's resolved transcript and record it.  |
| Editing mode                    | ABE or CBE.                                                                                        |
| Base editor                     | Supported editor subtype for efficacy and bystander prediction.                                    |
| Cell type                       | Supported prediction context, such as HEK293T.                                                     |
| Variant and desired change      | Required for variant-correction tasks; omit for general gene-level guide design.                   |
| Bowtie genome index             | Matching the selected organism and reference assembly; identify an available index or provide one. |
| Bowtie mismatch limit           | Search limit from 0 to 3; use 3 unless the user specifies another supported limit.                 |
| Shortlist size                  | Requested number of guide–editor combinations; if omitted, return all passing combinations.       |
| Additional rejection thresholds | Optional user-defined limits for bystanders or off-target matches; none apply by default.          |

## Design Constraints

- **Search Scope:** The current design tool scans exonic regions and NGG PAM sites. Report this scope with every run; a zero-result search applies only to this scope.
- **Guide:** 20-nt protospacer, as required by the current design and prediction input format. Use another length or PAM profile only if the tools explicitly support it.
- **Base Conversion:** ABE predicts A→G; CBE predicts C→T on the editable strand. Account for complementary-strand changes when mapping a desired variant correction.
- **Editing Window:** Use the selected editor's configured window. The tool interface specifies ABE positions 4–7 and CBE positions 4–8.
- **Prediction Input:** Each FASTA sequence must be exactly 50 nt: 19-nt upstream flank + 20-nt protospacer + 3-nt PAM + 8-nt downstream flank. Build the context in the orientation expected by the predictor; verify that the extracted guide and PAM match the design output.
- **FASTA Format:** A, C, G and T only; no gaps or ambiguous bases; unique record identifiers.
- **Off-Target Search:** Use Bowtie against an indexed genome matching the selected organism and reference assembly. Search for matches with 0–3 mismatches, exclude the intended locus using its genomic coordinates, and report the search settings.
- **Shortlist Size:** User-defined. If no cap is provided, report all candidates passing the design filters. Count guide–editor combinations separately from unique spacer sequences.
- **Unwanted-Edit Thresholds:** None are hard rejection rules by default. Report bystanders and Bowtie matches; rank them using declared criteria. Apply rejection cutoffs only if the user specifies them.

## Tools

| Tool                                    | Purpose                                                                | Inputs                                                                     |
| --------------------------------------- | ---------------------------------------------------------------------- | -------------------------------------------------------------------------- |
| CRISPR Base Editing                     | Enumerate exon-targeting guides and simulate eligible base conversions | Project, experiment name, gene ID, ABE/CBE mode                            |
| CRISPR Base Editing Efficacy Prediction | Predict the fraction of reads containing an editing event              | Project, experiment name, 50-nt FASTA, cell type, base editor, editor kind |
| CRISPR Bystander Effect Prediction      | Assess potential bystander edits and report available counts/positions | Project, experiment name, 50-nt FASTA, cell type, base editor, editor kind |
| Bowtie                                  | Search the reference genome for guide sequence matches                 | Guide sequence, matching genome index, mismatch limit (0–3)               |

## Workflow

1. Resolve the gene, reference genome and transcript. For variant correction, verify the reference and mutant alleles and intended change.
2. Run **CRISPR Base Editing** and retain guide, PAM, editable-position, coordinate and simulated-sequence outputs.
3. **Create the eligible shortlist:** retain each guide–editor combination only if its PAM is compatible and at least one relevant editable base falls within that editor's configured window. For variant correction, map the variant's genomic coordinate and alternate base to each guide's strand and position; retain only combinations that can perform the specified change. Record excluded combinations and reasons.
4. Prepare and validate the required 50-nt FASTA contexts, keeping mutant and reference contexts separate where relevant. Give each record a unique ID and retain a mapping from that ID to guide, allele, editor, transcript and genomic coordinates.
5. Run **CRISPR Base Editing Efficacy Prediction** and **CRISPR Bystander Effect Prediction** for supported editor/cell-type combinations.
6. Run **Bowtie** for each unique spacer against the matching genome index. Exclude the intended locus by coordinates, record 0–3 mismatch matches and apply the selected Cas enzyme's PAM rules when interpreting them.
7. **Rank and select final designs:** first require design compatibility and, for correction tasks, target-variant compatibility. Then sort by predicted editing-event fraction (higher first), number of additional editable bystander bases in the assessed window (lower first), Bowtie exact-match count (lower first), then 1-, 2- and 3-mismatch match counts (lower first), and guide ID for a stable tie-break. Exclude the intended locus from all off-target counts. The efficacy score is a general editing-event estimate, not necessarily the intended-correction rate. Report each metric separately; do not combine them into an unlabeled score. Return the user-requested number and report unique spacers separately from guide–editor combinations.

## Expected Output

**Format:** `design_bundle`

**Run status:** `COMPLETED_WITH_CANDIDATES`, `NO_COMPATIBLE_GUIDES`, `UNSUPPORTED_TARGET` or `BLOCKED`. Use `NO_COMPATIBLE_GUIDES` only after a complete search with supported inputs returns no candidate within the stated exonic/NGG/editor-window scope. Use `UNSUPPORTED_TARGET` when the organism, target, editor or model is outside tool support. Use `BLOCKED` when required data, indexes or tools are unavailable.

**Required Output Files:**

- `designed_sequences.fasta` — unique 20-nt guide spacers, written 5′→3′.
- `prediction_inputs.fasta` — validated 50-nt contexts submitted for prediction.
- `off_target_matches.tsv` — Bowtie matches with mismatch positions/counts, PAM/context, genomic coordinates and intended-site exclusion status.
- `record_map.tsv` — prediction FASTA record ID mapped to guide, allele, editor, transcript and genomic coordinates.
- `metrics.json` — project/experiment; target/reference/transcript; guide/editor combinations; PAMs, coordinates, editable-base counts and positions; original and simulated sequences; GC content; exon/protein annotations where available; efficacy and bystander outputs; Bowtie search settings and match counts; ranking components; tool versions and missing-data notes.

Report unique spacer counts separately from guide–editor combination counts.

## Constraints

- **Time Limit:** Set by the user before execution.
- **Tool Scope:** Use only supported organisms, editors, Cas variants, cell types and prediction contexts. Record the active PAM and target-region restrictions.
- **Off-Target Assessment:** Requires a Bowtie index for the selected reference genome. If unavailable, report specificity as not assessed and do not label candidates as specificity-screened.
- **Experimental Validation:** Outside the scope of this computational task.

## Important Instructions

- For variant correction, assess the mutant allele; do not rely on a reference-only prediction.
- The guide-design tool takes a gene ID. If a variant creates or removes a PAM or guide match, the standard gene-level enumeration may miss that allele-specific site; include it only if a supported custom-sequence design path is available, otherwise report this scope limitation.
- A simulated edited sequence does not mean all eligible bases will be edited together.
- The predicted fraction of reads with an editing event is not automatically the intended-correction rate.
- Interpret bystander counts within the reported editor/window scope; they do not prove no editing outside that scope.
- Keep each guide–editor–cell-type prediction as a separate result. Do not compare scores as calibrated probabilities across unsupported or differently configured models.
- Bowtie mismatch hits are sequence matches, not measured off-target editing. They do not establish zero off-target risk.
- Do not claim off-target safety, functional rescue or experimental validation from computational outputs.
- Use null for unavailable results and explain why. Return fewer designs when appropriate.
- Report “no compatible guides within the configured search scope,” rather than implying that no guide could exist under any editor, PAM or target-region profile.
