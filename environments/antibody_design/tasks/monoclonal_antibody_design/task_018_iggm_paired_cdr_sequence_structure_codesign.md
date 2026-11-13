# Task: task_018_iggm_paired_cdr_sequence_structure_codesign

## Description

Design all six CDR sequences and the antigen-bound conformation of a paired monoclonal antibody against the supplied human protein epitope. Preserve the chosen VH/VL framework while generating distinct candidate sequence pairs and complex structures. Return a ranked shortlist with CDR-resolved recovery and backbone-geometry evidence.

## Target

**Target:** Supplied human protein antigen and specified epitope\
**Starting Framework:** Verified paired VH/VL framework sequences\
**Antibody Format:** Paired variable domains in the declared Fv or Fab context\
**Editable Regions:** H1, H2, H3, L1, L2 and L3\
**Objective:** Joint six-CDR sequence and antibody–antigen structure design

## Design Constraints

- Verify the antigen, framework sequences, CDR numbering, loop lengths and epitope mapping before generation.
- Protect all framework positions and required disulfides. Preserve chain pairing and the declared six-CDR design scope.
- Keep native editable sequences and reference complex coordinates in the evaluator for reconstruction assessments. Record antigen, epitope and initialization information supplied to the design method.
- Freeze sampling count, initialization settings and shortlist selection before reference scoring. Keep independently initialized conditions separately identified.

## Evaluation Metrics

| Criterion | Measurements and Evidence | Evaluation Rule |
| --- | --- | --- |
| Sequence recovery | AAR for H1/H2/H3/L1/L2/L3 | Evaluate each loop separately on the declared editable residues. |
| Loop conformation | Backbone RMSD for all six CDRs | Use documented atom correspondence and alignment for every loop. |
| Framework integrity | Protected-position changes, chain pairing and disulfides | Reject violations of the specified antibody architecture. |
| Candidate quality | Loop geometry, antigen clashes and sequence diversity | Rank complete, eligible VH/VL designs with supporting complex structures. |

Source references: [IgGM, ICLR 2025 paper](https://proceedings.iclr.cc/paper_files/paper/2025/file/fa5b423e24b442180bcd4e13ae75a27f-Paper-Conference.pdf), [author results page](https://iggm.rubo.wang/), [TencentAI4S/IgGM @ `06abc563b3fc`](https://github.com/TencentAI4S/IgGM/tree/06abc563b3fc8c7ea020543add16b69b6f8a1c8d).

Computational reference: [task-specific benchmark](../../benchmark/monoclonal_antibody_design/task_018_iggm_paired_cdr_sequence_structure_codesign.md).

## Expected Output

**Format:** `antibody_design_bundle`\
**Directory:** `six_cdr_results/`

- `designed_sequences.fasta`: complete candidate VH/VL or scFv sequences with unique identifiers and domain boundaries.
- `shortlist.csv`: ranked, nonduplicate candidates, changes from the reference and exclusion reasons.
- `metrics.json`: actual computational values, metric definitions, structural scope, units, candidate hashes and provenance.
- `benchmark_comparison.csv`: published computational reference values and executed results, with their respective scopes.
- `report.md`: scientific rationale, supported conclusions and candidate-specific evidence; include structures, chain/residue maps and raw scoring outputs.

## Important Instructions

- Select methods independently within the user's access and computational constraints; no particular workflow is required.
- Report missing essential inputs as `NEEDS_INPUT`. Record the exact target construct, reference sequence, editable regions or candidate panel, methods and evaluation settings used.
- Report sequence/structure design results separately from known-sequence structure prediction.
- Native recovery and backbone agreement do not establish experimental affinity or therapeutic activity.
