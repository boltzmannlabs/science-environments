# Task: task_008_egfr_scfv_design

## Description

Design scFv variants against human EGFR using the supplied reference antibody. Improve sequence–structure compatibility and the predicted antigen interface while retaining paired variable domains, the declared binding region and the scFv architecture. Evaluate the reference and every proposed variant under matched conditions, then return a ranked shortlist supported by actual computational outputs.

## Target

**Target:** Human epidermal growth factor receptor (EGFR), extracellular construct supplied for the task\
**Reference Antibody:** The selected released EGFR scFv, identified by its source record and exact sequence\
**Reference Collection:** 21 released EGFR scFv records from the [ProteinBase scFv catalog](https://proteinbase.com/proteins?proteinCategory=scfv)\
**Antibody Format:** scFv containing paired VH/VL domains and the declared linker\
**Objective:** Reference-guided scFv sequence and interface optimization

## Design Constraints

- Verify the EGFR construct, reference scFv sequence, VH/VL boundaries, domain order and linker before design. Retain source-to-prepared chain and residue mappings.
- Declare editable CDR and framework positions, protected residues, loop-length limits and candidate count before generation. Preserve VH/VL pairing, required disulfides and the declared linker.
- Keep the target construct and scoring preparation identical for the reference and candidates. Retain relevant extracellular-domain, glycosylation and assembly context when assessing accessibility.
- Assess whole-scFv folding, individual variable domains and the antigen interface separately. Inspect domain orientation, linker geometry, clashes and binding-region contacts.
- Use released reference sequences as identified controls. Attribute every new sequence to its actual parent and permitted edits.

## Evaluation Metrics

| Criterion | Measurements and Evidence | Evaluation Rule |
| --- | --- | --- |
| Reference preservation | VH/VL identity, CDR/framework edits, linker and domain order | Reject changes outside the declared design scope. |
| Sequence–structure compatibility | Original/candidate ProteinMPNN scores and sequence recovery | Use the same backbone preparation and score definition; retain the original numerical scale. |
| Structural quality | Whole-structure and domain-resolved ESMFold pLDDT, geometry and clashes | Assess variable-domain and linker quality separately from global confidence. |
| Target engagement | Mapped epitope contacts, interface geometry and full-target clashes | Evaluate the proposed binding region in the prepared EGFR context. |
| Candidate quality | Sequence liabilities, diversity and computational uncertainty | Rank eligible, nonduplicate scFvs with explicit reference differences. |

Source references: [ProteinBase scFv catalog](https://proteinbase.com/proteins?proteinCategory=scfv).

Computational reference: [task-specific benchmark](../../benchmark/monoclonal_antibody_design/task_008_egfr_scfv_design.md).

## Expected Output

**Format:** `antibody_design_bundle`\
**Directory:** `egfr_results/`

- `designed_sequences.fasta`: complete candidate VH/VL or scFv sequences with unique identifiers and domain boundaries.
- `shortlist.csv`: ranked, nonduplicate candidates, changes from the reference and exclusion reasons.
- `metrics.json`: actual computational values, metric definitions, structural scope, units, candidate hashes and provenance.
- `benchmark_comparison.csv`: published computational reference values and executed results, with their respective scopes.
- `report.md`: scientific rationale, supported conclusions and candidate-specific evidence; include structures, chain/residue maps and raw scoring outputs.
- `reference_comparison.csv`: matched reference/candidate computational scores, differences, sequence edits and structural scope.

## Important Instructions

- Select methods independently within the user's access and computational constraints; no particular workflow is required.
- Report missing essential inputs as `NEEDS_INPUT`. Record the exact target construct, reference sequence, editable regions or candidate panel, methods and evaluation settings used.
- Treat whole-structure confidence, domain scores and database-alignment scores according to their actual structural scope.
- Use published values as reference evidence; report the calculations performed for the current candidate separately.
- Computational compatibility and interface improvement do not establish experimental affinity or EGFR inhibition.
