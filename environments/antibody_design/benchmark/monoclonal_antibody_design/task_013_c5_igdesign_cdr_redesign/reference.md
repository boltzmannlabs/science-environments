# Benchmark: Complement C5 CDR redesign

**Task:** [Complement C5: Reference-Conditioned CDR Redesign](../../../tasks/monoclonal_antibody_design/task_013_c5_igdesign_cdr_redesign.md)

## Published computational reference

Sources: [IgDesign preprint](https://doi.org/10.1101/2023.12.08.570889), [ICLR GEM paper](https://openreview.net/pdf?id=awGfgUJdQY), and the released [Eculizumab-C5.csv](https://raw.githubusercontent.com/AbSciBio/igdesign/70431eef0afaf0496d7d84e22dfdc1980ec9e70e/data/Eculizumab-C5.csv) at data revision `70431eef0afa`. The table reproduces the released Eculizumab positive-control row. All scRMSD values are in Å; lower indicates a closer structural match under the source evaluator.

| Predictor | HCDR1 | HCDR2 | HCDR3 | HCDR123 | Fv |
| --- | --- | --- | --- | --- | --- |
| ABB2 | 1.1479 | 1.0812 | 2.2289 | 1.7452 | 1.2950 |
| ABB3 | 1.3176 | 1.1441 | 2.3998 | 1.8901 | 1.3017 |
| ABB3-LM | 1.2023 | 1.1968 | 1.8354 | 1.5403 | 1.2441 |
| ESMFold | 0.8494 | 1.0668 | 1.6620 | 1.3477 | 1.2044 |

These are the released predictor-specific scores of the unmodified reference antibody. They are not scores of candidates generated in this task. A newly calculated scRMSD is directly comparable only when predictor, reference structure, atom selection, residue mapping and alignment agree.

## Reference sequence and reconstruction endpoint

The parent is Eculizumab, with VH 122 residues and VL 107 residues in the prepared [5I5K](https://www.rcsb.org/structure/5I5K) Fv. Native heavy-chain CDR sequences from the positive-control row are:

| CDR | Native sequence | Length |
| --- | --- | --- |
| HCDR1 | `GYIFSNYW` | 8 |
| HCDR2 | `ILPGSGST` | 8 |
| HCDR3 | `ARYFFGSSPNWYFDV` | 15 |

Amino-acid recovery (AAR) is the fraction of position-aligned designed residues that match the native sequence (0–1; higher). A 1-shot result uses one generated sample. Best-of-100 uses the maximum over a separately specified 100-sample pool. Per-CDR maxima may belong to different sequences; joint recovery is length-weighted over all designed positions of one sequence. Protected framework or VL residues are excluded from the designed-scope denominator.

## Evaluation criteria

- Preserve the exact parent VH/VL pair and declared HCDR3-only or HCDR123 edit mask.
- Report sample counts, sequence constraints and the sampling rule beside AAR.
- State the structural comparator, fitted atoms and measured regions for each scRMSD table.
- Keep the released control scores and newly executed measurements separate.

[Completed workflows and calculated results](comparison.md).
