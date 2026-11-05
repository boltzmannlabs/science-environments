# Task: mab_her2_reference_optimization

## Description

Design monoclonal antibody variants derived from trastuzumab against human HER2. Improve the predicted antigen–antibody interaction while retaining the reference binding region, paired variable domains and acceptable structural quality. Evaluate the reference and every proposed variant under matched conditions, then return a ranked shortlist supported by actual computational outputs.

## Target

**Target:** Human HER2 (ERBB2), extracellular domain\
**Reference Antibody:** Trastuzumab\
**Reference Complex:** [PDB 1N8Z](https://www.rcsb.org/structure/1N8Z)\
**Antibody Format:** Paired heavy/light variable domains in the reference Fab context\
**Objective:** Reference-guided interaction optimization

## Design Constraints

- Verify antigen and antibody sequences, chain identities, unresolved residues and the biological assembly before design. Retain a mapping between deposited and prepared coordinates.
- Declare editable CDR positions and protected framework positions before generating candidates. Preserve heavy/light pairing and required disulfides.
- Evaluate candidates and the unmodified reference against the same HER2 construct and preparation. Keep framework integrity, clashes and interface plausibility in the selection criteria.
- Keep published optimized sequences as comparison controls. Do not return them as newly generated designs.

## Evaluation Metrics

| Criterion | Measurements and Evidence | Evaluation Rule |
| --- | --- | --- |
| Reference preservation | Paired-chain identity, CDR edits, protected-position changes | Reject changes outside the declared design scope. |
| Interaction improvement | Reference and candidate interaction scores; candidate-minus-reference difference | Compare identical score definitions and preparation conditions. |
| Structural quality | Local CDR confidence, geometry, clashes and interface uncertainty | Assess the binding loops and antigen interface separately from global fold quality. |
| Binding-region retention | Mapped contacts and pose agreement with the reference epitope | Explain any material change in binding orientation. |
| Candidate quality | Sequence liabilities, diversity and uncertainty | Rank eligible, nonduplicate pairs; report unresolved properties. |

Published comparison data: [HER2 Reference Antibody Optimization benchmark](../../benchmark/monoclonal_antibody_design/mab_her2_reference_optimization.md).

## Expected Output

**Format:** `antibody_design_bundle`\
**Directory:** `her2_results/`

- `designed_sequences.fasta`: proposed paired heavy/light sequences with unique identifiers.
- `metrics.json`: matched reference/candidate scores, units, sequence hashes and artifact provenance.
- `shortlist.csv`: ranked candidates, reference differences and exclusion reasons.
- `benchmark_comparison.csv`: published value, new result, comparison scope and comparability decision for each metric.
- `report.md`: design rationale, supported improvements and unresolved evidence; include supporting structures and raw scoring outputs.

## Important Instructions

- Select methods independently within the user's access constraints; no particular design workflow is required.
- Treat the reported best scores as comparison results, not universal acceptance thresholds.
- Report missing essential inputs as `NEEDS_INPUT`. Never copy published numbers into the new-run result fields.
- Computational interaction improvement does not establish experimental affinity or therapeutic activity.
