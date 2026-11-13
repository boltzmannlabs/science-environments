# Task: task_013_c5_igdesign_cdr_redesign

## Description

Design monoclonal antibody variants derived from Eculizumab against human complement C5. Redesign the permitted heavy-chain CDRs using the supplied reference backbone while preserving the framework and paired light chain. Improve computational sequence–structure compatibility, evaluate candidates alongside the unmodified reference, and return a ranked shortlist with actual recovery and structural-consistency scores.

## Target

**Target:** Human complement C5, exact supplied reference construct\
**Reference Antibody:** Eculizumab\
**Reference Structure:** Supplied antibody–antigen complex with verified chain and residue mapping\
**Antibody Format:** Paired VH/VL in the declared reference fragment or full-antibody context\
**Objective:** Reference-backbone-conditioned heavy-chain CDR redesign\
**Source Reference Record:** `Eculizumab-C5.csv`

## Design Constraints

- Verify the complete Eculizumab VH/VL pair, antigen sequence, reference structure and CDR numbering before design.
- Declare HCDR3-only or HCDR123 editing before generation. Preserve the entire VL and all protected VH residues; keep the two editing scopes separately labelled.
- Retain the supplied backbone conditioning and allowed loop lengths. In a masked native-reconstruction run, keep the native editable sequence in the evaluator.
- Evaluate reference and candidates with identical structural preparation, predictor settings, atom selection and alignment. Record candidate count, seeds and selection criteria.
- Retain the exact complement C5 construct and domain context represented by the reference structure.

## Evaluation Metrics

| Criterion | Measurements and Evidence | Evaluation Rule |
| --- | --- | --- |
| Sequence validity | Heavy-chain CDR edits, protected positions and VH/VL pairing | Reject edits outside the declared mask. |
| Native recovery | Per-CDR amino-acid recovery on a declared masked reconstruction | Record the native sequence, evaluated positions and sampling count in the evaluator. |
| Structural consistency | Predictor-specific HCDR1/HCDR2/HCDR3/HCDR123 and Fv scRMSD | Compare identical predictors, reference geometry, atoms, alignment and structural regions. |
| Candidate selection | Reference differences, geometry and sequence diversity | Rank distinct eligible pairs while preserving framework and light-chain constraints. |

Source references: [IgDesign preprint, 2023](https://doi.org/10.1101/2023.12.08.570889), [ICLR GEM 2024 paper](https://openreview.net/pdf?id=awGfgUJdQY), [released `Eculizumab-C5.csv`](https://raw.githubusercontent.com/AbSciBio/igdesign/70431eef0afaf0496d7d84e22dfdc1980ec9e70e/data/Eculizumab-C5.csv), [AbSciBio/igdesign @ `70431eef0afa`](https://github.com/AbSciBio/igdesign/tree/70431eef0afaf0496d7d84e22dfdc1980ec9e70e).

Computational reference: [task-specific benchmark](../../benchmark/monoclonal_antibody_design/task_013_c5_igdesign_cdr_redesign.md).

## Expected Output

**Format:** `antibody_design_bundle`\
**Directory:** `c5_results/`

- `designed_sequences.fasta`: complete candidate VH/VL or scFv sequences with unique identifiers and domain boundaries.
- `shortlist.csv`: ranked, nonduplicate candidates, changes from the reference and exclusion reasons.
- `metrics.json`: actual computational values, metric definitions, structural scope, units, candidate hashes and provenance.
- `benchmark_comparison.csv`: published computational reference values and executed results, with their respective scopes.
- `report.md`: scientific rationale, supported conclusions and candidate-specific evidence; include structures, chain/residue maps and raw scoring outputs.

## Important Instructions

- Select methods independently within the user's access and computational constraints; no particular workflow is required.
- Report missing essential inputs as `NEEDS_INPUT`. Record the exact target construct, reference sequence, editable regions or candidate panel, methods and evaluation settings used.
- Use source reference sequences as labelled controls and preserve the provenance of newly generated variants.
- Report 1-shot and best-of-100 AAR separately when those sample budgets are executed.
- Computational recovery and scRMSD do not establish experimental affinity or functional activity.
