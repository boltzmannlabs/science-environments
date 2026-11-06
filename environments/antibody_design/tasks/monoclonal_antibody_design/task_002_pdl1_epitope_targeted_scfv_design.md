# Task: task_002_pdl1_epitope_targeted_scfv_design

## Description

Design paired-variable-domain monoclonal antibody candidates against the human PD-L1 epitope studied in the Germinal scFv example. Use the study's starting framework as the design reference and H5 as the published antibody comparator. Produce distinct candidates with credible epitope engagement and report their computational evidence against the published benchmark.

## Target

**Target:** Human PD-L1 (CD274), extracellular V-like domain\
**Reference Antibody:** Published anti-PD-L1 H5, for comparison\
**Design Input:** Study-provided paired framework and target construct, with verified sequence and residue mapping\
**Antibody Format:** scFv containing paired VH/VL domains; preserve the declared orientation and linker\
**Objective:** Framework-conditioned epitope-directed design

H5 is a final published design, not the original starting antibody. Recover the actual starting framework from the study resources. If it is unavailable, report the missing input rather than silently substituting H5 as the parent.

## Design Constraints

- Declare CDR edit boundaries, framework protection, linker sequence and domain order before design. The paper's framework bias does not imply every framework position was fixed.
- Verify the target construct, glycosylation context and residue numbering. Retain provenance for experimental coordinates and predictions separately.
- Keep the H5 experimental structure out of candidate generation when evaluating prospective structural prediction. Its coordinates are evaluation evidence.
- Preserve the full target context when assessing epitope accessibility and clashes. State any differences between this task's input structure and the paper's predicted antigen input.

## Evaluation Metrics

| Criterion | Measurements and Evidence | Evaluation Rule |
| --- | --- | --- |
| Paired-domain integrity | Framework edits, VH/VL arrangement, linker and local geometry | Enforce declared sequence and format constraints. |
| Interface confidence | ipTM, interface PAE and chain/CDR-resolved pLDDT when available | Report actual values, scope and model uncertainty. |
| Epitope engagement | Mapped contacts, interface area, hydrogen bonds and clashes | Assess intended epitope coverage and accessibility. |
| Structural agreement | Global Cα RMSD and per-CDR comparisons against an independent structure | Evaluate H5 reconstruction separately; H5 is not ground truth for different candidate sequences. |
| Novelty and liabilities | CDR identity, interface similarity, sequence liabilities | Report comparator database and search scope; novelty alone does not prove binding. |

Published comparison data: [PD-L1: Epitope-Targeted scFv Design benchmark](../../benchmark/monoclonal_antibody_design/task_002_pdl1_epitope_targeted_scfv_design.md).

## Expected Output

**Format:** Computational antibody design bundle\
**Directory:** `pdl1_results/`

- `designed_sequences.fasta`: full scFv sequences with VH, VL and linker boundaries recorded.
- `metrics.json`: candidate evidence, comparator records, input identities and artifact hashes.
- `shortlist.csv`: ranked candidates with eligibility and uncertainty.
- `benchmark_comparison.csv`: published values, new measurements and their comparison scope.
- `report.md`: epitope evidence, H5 comparison, design provenance and limitations, with structures and raw outputs.

## Important Instructions

- Choose methods independently; the paper defines the scientific example and benchmark, not a required workflow.
- Do not present a new sequence's similarity to H5 as experimentally established structural accuracy.
- Keep published results separate from executed results. Use `NEEDS_INPUT` for missing essential sequences or structures.
- The scFv output format is explicit; do not silently treat it as a full-length IgG or an independently paired Fab result.
