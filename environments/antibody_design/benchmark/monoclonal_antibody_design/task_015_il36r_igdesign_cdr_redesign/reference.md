# Benchmark: IL-36R CDR redesign

**Task:** [IL-36R: Reference-Conditioned CDR Redesign](../../../tasks/monoclonal_antibody_design/task_015_il36r_igdesign_cdr_redesign.md)

## Published computational reference

Sources: [IgDesign preprint](https://doi.org/10.1101/2023.12.08.570889), [ICLR GEM paper](https://openreview.net/pdf?id=awGfgUJdQY), and the released [Spesolimab-IL36R.csv](https://raw.githubusercontent.com/AbSciBio/igdesign/70431eef0afaf0496d7d84e22dfdc1980ec9e70e/data/Spesolimab-IL36R.csv) at data revision `70431eef0afa`. The table reproduces the released Spesolimab positive-control row. All scRMSD values are in Å; lower indicates a closer structural match under the source evaluator.

| Predictor | HCDR1 | HCDR2 | HCDR3 | HCDR123 | Fv |
| --- | --- | --- | --- | --- | --- |
| ABB2 | 0.6209 | 0.3009 | 0.6636 | 0.5699 | 0.3777 |
| ABB3 | 0.6263 | 0.3967 | 1.1363 | 0.8428 | 0.5498 |
| ABB3-LM | 1.1884 | 0.7102 | 1.2133 | 1.0856 | 0.6509 |
| ESMFold | 1.0185 | 0.6513 | 3.3469 | 2.2844 | 1.1768 |

These are the released predictor-specific scores of the unmodified reference antibody. They are not scores of candidates generated in this task. A newly calculated scRMSD is directly comparable only when predictor, reference structure, atom selection, residue mapping and alignment agree.

## Reference sequence and reconstruction endpoint

The parent is Spesolimab, with VH 119 residues and VL 108 residues in the prepared [6U6U](https://www.rcsb.org/structure/6U6U) Fv. Native heavy-chain CDR sequences from the positive-control row are:

| CDR | Native sequence | Length |
| --- | --- | --- |
| HCDR1 | `GYSFTSSW` | 8 |
| HCDR2 | `INPGNVRT` | 8 |
| HCDR3 | `TVVFYGEPYFPY` | 12 |

Amino-acid recovery (AAR) is the fraction of position-aligned designed residues that match the native sequence (0–1; higher). A 1-shot result uses one generated sample. Best-of-100 uses the maximum over a separately specified 100-sample pool. Per-CDR maxima may belong to different sequences; joint recovery is length-weighted over all designed positions of one sequence. Protected framework or VL residues are excluded from the designed-scope denominator.

## Evaluation criteria

- Preserve the exact parent VH/VL pair and declared HCDR3-only or HCDR123 edit mask.
- Report sample counts, sequence constraints and the sampling rule beside AAR.
- State the structural comparator, fitted atoms and measured regions for each scRMSD table.
- Keep the released control scores and newly executed measurements separate.

[Completed workflows and calculated results](comparison.md).
