# Task: task_004_lcat_reference_fab_cdrh3_reconstruction

## Description

Design the CDR-H3 sequence and antibody structure for the human LCAT reference case in the released AbFlow RAbD benchmark. Use the supplied paired antibody context with CDR-H3 masked. Evaluate the completed designs against the held-out reference sequence and complex, and report how the single-case results relate to the paper's aggregate benchmarks.

## Target

**Target:** Human lecithin–cholesterol acyltransferase (LCAT), deposited L4F/N5D construct\
**Reference Antibody:** Agonistic anti-LCAT Fab in [PDB 5BV7](https://www.rcsb.org/structure/5BV7)\
**Benchmark Entry:** `5bv7` in the authors' `datasets/RAbD/test.json`\
**Dataset Chain Assignment:** Heavy C, light B, antigen A; IMGT numbering in the released entry\
**Antibody Format:** Paired heavy/light Fab variable domains\
**Objective:** Antigen-conditioned CDR-H3 sequence/structure reconstruction

Confirm dataset-to-deposition chain and residue mappings rather than assuming the prepared chain identifiers are native PDB identifiers. Retain the deposited target substitutions and distinguish this construct from wild-type LCAT.

## Design Constraints

- The evaluator supplies a masked design input. Withhold native CDR-H3 sequence, loop coordinates and native complex pose from the design agent; retain them for final scoring.
- Preserve unmasked antibody residues, paired-chain identity and declared CDR boundaries. Do not expand into six-CDR design without declaring a separate evaluation track.
- Record reference/template exposure and possible training overlap. Because the reference is public, this task is not inherently a blind benchmark.
- Freeze generated sequences and rankings before evaluating native recovery. A copied reference is not a new design.

## Evaluation Metrics

| Criterion | Measurements and Evidence | Evaluation Rule |
| --- | --- | --- |
| Sequence recovery | AAR and contact-residue AAR (CAAR) | Record masked positions and contact definition; higher is better. |
| Structural agreement | CDR-H3 RMSD, TM-score and lDDT | Specify atoms, correspondence, alignment and evaluated region. |
| Interface accuracy | DockQ, interface contacts and clashes | Use the held-out complex with an explicit chain mapping and metric version. |
| Constraint compliance | Changes outside the mask, pairing and geometry | Reject prohibited edits and invalid structures. |
| Evidence integrity | Raw artifacts, candidate hashes and reference exposure | Keep individual results separate from dataset summaries. |

Published comparison data: [LCAT: Reference Fab CDR-H3 Reconstruction benchmark](../../benchmark/monoclonal_antibody_design/task_004_lcat_reference_fab_cdrh3_reconstruction.md).

## Expected Output

**Format:** Computational antibody design bundle\
**Directory:** `lcat_results/`

- `designed_sequences.fasta`: completed heavy/light pairs with candidate identifiers.
- `metrics.json`: per-candidate recovery, structural and interface scores with definitions and provenance.
- `shortlist.csv`: frozen candidate ordering and eligibility.
- `benchmark_comparison.csv`: 5BV7 results alongside explicitly labelled aggregate reference values.
- `report.md`: mask definition, reference exposure, comparison limits and evidence, with full-atom structures and raw outputs.

## Important Instructions

- Choose methods independently; no prescribed generation workflow is required.
- Do not claim to reproduce a 60-case benchmark from this single task.
- Use `NEEDS_INPUT` if the masked input or reference mapping is unavailable.
- Reconstruction accuracy does not establish improved LCAT binding or agonist activity.
