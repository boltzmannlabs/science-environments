# Task: task_010_chimera_epitope_conditioned_cdr_design

## Description

Design the CDR-H3 sequence and loop conformation of a paired monoclonal antibody against the supplied human protein epitope. Use the antigen and paired framework context while retaining the protected antibody regions. Generate distinct candidates and return a ranked shortlist supported by sequence recovery, loop geometry and antigen-interface evidence.

## Target

**Target:** Supplied human protein antigen and specified epitope\
**Starting Antibody:** Supplied paired VH/VL framework with CDR-H3 designated for design\
**Antibody Format:** Paired variable domains in the declared Fv or Fab context\
**Objective:** Epitope-conditioned CDR-H3 sequence/structure design

## Design Constraints

- Verify the antigen construct, paired antibody sequences, residue numbering, epitope map and editable CDR-H3 boundaries before generation.
- Preserve unedited framework and light-chain residues, required disulfides and declared loop-length limits. Treat multiple-CDR design as a separately specified scope.
- Record the structural conditioning supplied to the design method, including any bound framework pose. Keep native editable sequence and loop coordinates in the evaluator for masked reconstruction.
- Freeze candidate count and shortlist ordering before native-reference scoring. Evaluate all candidates under the same structural and contact definitions.

## Evaluation Metrics

| Criterion | Measurements and Evidence | Evaluation Rule |
| --- | --- | --- |
| Sequence recovery | CDR-H3 AAR and contact-residue AAR | Evaluate the declared masked residues and native contact mask. |
| Loop conformation | CDR-H3 Cα RMSD | Retain atom correspondence and the declared structural alignment. |
| Interface accuracy | Fnat, DockQ and epitope precision/recall/F1 | Use consistent chain mappings and the metric-specific contact definitions. |
| Design validity | Protected edits, loop geometry and steric clashes | Retain eligible, nonduplicate pairs within the declared edit scope. |

Source references: [CHIMERA-Bench paper, 2026](https://arxiv.org/abs/2603.13431), [data release](https://zenodo.org/records/20598827), [mansoor181/chimera-bench @ `c0ada2ff045e`](https://github.com/mansoor181/chimera-bench/tree/c0ada2ff045e1622ef39e4a25db34724813f378a).

Computational reference: [task-specific benchmark](../../benchmark/monoclonal_antibody_design/task_010_chimera_epitope_conditioned_cdr_design.md).

## Expected Output

**Format:** `antibody_design_bundle`\
**Directory:** `chimera_cdr_results/`

- `designed_sequences.fasta`: complete candidate VH/VL or scFv sequences with unique identifiers and domain boundaries.
- `shortlist.csv`: ranked, nonduplicate candidates, changes from the reference and exclusion reasons.
- `metrics.json`: actual computational values, metric definitions, structural scope, units, candidate hashes and provenance.
- `benchmark_comparison.csv`: published computational reference values and executed results, with their respective scopes.
- `report.md`: scientific rationale, supported conclusions and candidate-specific evidence; include structures, chain/residue maps and raw scoring outputs.

## Important Instructions

- Select methods independently within the user's access and computational constraints; no particular workflow is required.
- Report missing essential inputs as `NEEDS_INPUT`. Record the exact target construct, reference sequence, editable regions or candidate panel, methods and evaluation settings used.
- Report model-ranked candidates separately from retrospective best-of-K recovery summaries.
- Native recovery and pose agreement describe reconstruction quality; they do not establish experimental affinity.
