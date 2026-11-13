# Missing-metric benchmark report — Task 004

Benchmark selected: the task-specific AbFlow KDD 2026 RAbD benchmark, 60-case aggregate, with 5BV7 as the local case. Published Table 1 anchors: AAR 0.4234±0.1334, CAAR 0.2824±0.2037, TM-score 0.9736±0.0090, lDDT 0.8522±0.0216, RMSD 8.25±4.55 Å and DockQ 0.423±0.161. Table 2 is a separate multi-CDR/full-atom evaluation and is not merged with Table 1.

## Independently recovered missing metric

DockQ was run with the open-source `DockQ.py` implementation from the AbFlow repository. Native: PDB 5BV7, antigen chain A plus Fab chains B+C. Models: task004 candidate structures with model chain A as antigen and B+C as Fab. `-no_needle` was used because EMBOSS `needle` is unavailable and the prepared model/native sequences are known to be identical for the mapped chains.

| Candidate | DockQ | Fnat | iRMS (Å) | LRMS (Å) | Fnonnat | Published AbFlow mean±SD | Difference from mean | Verdict |
|---|---:|---:|---:|---:|---:|---:|---:|---|
| task004_sample9 | 0.537 | 0.764 | 1.203 | 15.219 | 0.311 | 0.423±0.161 | +0.114 | Above aggregate mean; single-case comparison only |
| task004_sample1 | 0.539 | 0.745 | 1.427 | 11.647 | 0.339 | 0.423±0.161 | +0.116 | Above aggregate mean; single-case comparison only |
| task004_sample6 | 0.506 | 0.800 | 1.473 | 16.516 | 0.312 | 0.423±0.161 | +0.083 | Above aggregate mean; single-case comparison only |

## Remaining missing metrics

| Metric | Why missing | Comparison |
|---|---|---|
| Exact 5BV7-specific AbFlow benchmark values | Paper reports aggregate statistics, not a published per-case 5BV7 score | Cannot claim exact case-level superiority. |
| lDDT under AbFlow definition | Existing retained values are Boltz-2 confidence/lDDT-like outputs, not a verified reference-comparison lDDT implementation matched to AbFlow | Not reproduced. pLDDT is not lDDT. |
| TM-score under the same AbFlow protocol | Retained short-loop TM-score values use task-specific protocols; AbFlow's alignment/atom definition is not fully available | Not directly comparable. |
| Full-atom RMSD and multi-CDR Table 2 metrics | This task evaluates CDR-H3 reconstruction, not the separate multi-CDR/full-atom Table 2 protocol | Not applicable to the current task scope. |

Identity check: PDB 5BV7 is human LCAT L4F/N5D, not DENV-2. The DENV-2 wording was stale inherited text and was not used for scoring.
