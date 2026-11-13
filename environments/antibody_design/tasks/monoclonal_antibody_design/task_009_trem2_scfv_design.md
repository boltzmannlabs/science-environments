# Task: task_009_trem2_scfv_design

## Description

Design scFv variants derived from the supplied anti-TREM2 reference against human TREM2. Improve predicted sequence–structure compatibility and antigen engagement while retaining the reference variable-domain pairing and scFv architecture. Evaluate reference and candidate structures under matched conditions, then return a ranked shortlist with folding, interface and sequence evidence.

## Target

**Target:** Human triggering receptor expressed on myeloid cells 2 (TREM2), extracellular construct supplied for the task\
**Reference Antibody:** Released scFv [golden-gecko-stone](https://proteinbase.com/proteins/golden-gecko-stone)\
**Reference Identity:** Exact released scFv sequence with verified VH, VL and linker boundaries\
**Antibody Format:** scFv containing paired VH/VL domains and the declared linker\
**Objective:** Reference-guided scFv sequence and interface optimization

## Design Constraints

- Verify the reference sequence, VH/VL order, linker, TREM2 construct and source structural models before design. Preserve chain and residue mappings.
- Declare editable CDR/framework positions, protected residues, loop-length limits and candidate count. Preserve paired-domain identity, required disulfides and the declared molecular format.
- Evaluate the unmodified reference and all candidates with the same target preparation, structural prediction settings and scoring definitions.
- Identify the chains and domain regions represented by each structure and score. Retain raw confidence scales and assess whole-scFv, variable-domain and interface evidence separately.
- Inspect the proposed binding surface in the relevant extracellular and glycosylation context. Preserve the declared reference binding region and explain material pose changes.

## Evaluation Metrics

| Criterion | Measurements and Evidence | Evaluation Rule |
| --- | --- | --- |
| Reference preservation | Permitted sequence edits, domain order, linker and paired-variable identity | Reject changes outside the declared design scope. |
| Sequence–structure compatibility | ProteinMPNN score and sequence recovery | Compare the reference and variants under identical backbone/scoring conditions. |
| Folding confidence | ESMFold pLDDT; Boltz2 pLDDT and pTM | Retain raw scales and specify the chains or domains summarized by each score. |
| Interface confidence | Boltz2 ipTM, interface pLDDT, PDE, ipSAE, pDockQ, pDockQ2 and LIS | Use matched complex preparation and chain-pair assignments; report each metric separately. |
| Interface geometry | Shape complementarity, target contacts and clashes | Retain the source score scale and inspect accessibility in the full target context. |
| Candidate quality | Sequence liabilities, diversity and uncertainty | Rank eligible scFvs using consistent reference differences and supporting structures. |

Source references: [ProteinBase scFv catalog](https://proteinbase.com/proteins?proteinCategory=scfv).

Computational reference: [task-specific benchmark](../../benchmark/monoclonal_antibody_design/task_009_trem2_scfv_design.md).

## Expected Output

**Format:** `antibody_design_bundle`\
**Directory:** `trem2_results/`

- `designed_sequences.fasta`: complete candidate VH/VL or scFv sequences with unique identifiers and domain boundaries.
- `shortlist.csv`: ranked, nonduplicate candidates, changes from the reference and exclusion reasons.
- `metrics.json`: actual computational values, metric definitions, structural scope, units, candidate hashes and provenance.
- `benchmark_comparison.csv`: published computational reference values and executed results, with their respective scopes.
- `report.md`: scientific rationale, supported conclusions and candidate-specific evidence; include structures, chain/residue maps and raw scoring outputs.
- `reference_comparison.csv`: matched folding/interface scores, candidate-minus-reference differences and sequence edits.

## Important Instructions

- Select methods independently within the user's access and computational constraints; no particular workflow is required.
- Report missing essential inputs as `NEEDS_INPUT`. Record the exact target construct, reference sequence, editable regions or candidate panel, methods and evaluation settings used.
- Retain the supplied source record as the parent; attribute every proposed edit to that reference.
- Use interface metrics only for the chain pairs and structural models from which they were calculated.
- Computational scores do not establish experimental affinity, TREM2 agonism, antagonism or cellular activity.
