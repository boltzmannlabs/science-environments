# Benchmark: Factor XI CDR redesign

**Task:** [Factor XI: Reference-Conditioned CDR Redesign](../../../tasks/monoclonal_antibody_design/task_014_fxi_igdesign_cdr_redesign.md)

## Published computational reference

Sources: [IgDesign preprint](https://doi.org/10.1101/2023.12.08.570889), [ICLR GEM paper](https://openreview.net/pdf?id=awGfgUJdQY), and the released [Osocimab-FXI.csv](https://raw.githubusercontent.com/AbSciBio/igdesign/70431eef0afaf0496d7d84e22dfdc1980ec9e70e/data/Osocimab-FXI.csv) at data revision `70431eef0afa`. The table reproduces the released Osocimab positive-control row. All scRMSD values are in Å; lower indicates a closer structural match under the source evaluator.

| Predictor | HCDR1 | HCDR2 | HCDR3 | HCDR123 | Fv |
| --- | --- | --- | --- | --- | --- |
| ABB2 | 0.3017 | 0.4394 | 1.9335 | 1.3245 | 0.5759 |
| ABB3 | 0.5247 | 0.5213 | 2.1584 | 1.4964 | 0.6669 |
| ABB3-LM | 0.3971 | 0.3698 | 1.9120 | 1.3115 | 0.6241 |
| ESMFold | 0.7708 | 1.0993 | 3.5167 | 2.4578 | 1.1314 |

These are the released predictor-specific scores of the unmodified reference antibody. They are not scores of candidates generated in this task. A newly calculated scRMSD is directly comparable only when predictor, reference structure, atom selection, residue mapping and alignment agree.

## Reference sequence and reconstruction endpoint

The parent is Osocimab, with VH 120 residues and VL 107 residues in the prepared [6HHC](https://www.rcsb.org/structure/6HHC) Fv. Native heavy-chain CDR sequences from the positive-control row are:

| CDR | Native sequence | Length |
| --- | --- | --- |
| HCDR1 | `GFTFSQYG` | 8 |
| HCDR2 | `IGPSGGST` | 8 |
| HCDR3 | `TRGGPYYYYGMDV` | 13 |

Amino-acid recovery (AAR) is the fraction of position-aligned designed residues that match the native sequence (0–1; higher). A 1-shot result uses one generated sample. Best-of-100 uses the maximum over a separately specified 100-sample pool. Per-CDR maxima may belong to different sequences; joint recovery is length-weighted over all designed positions of one sequence. Protected framework or VL residues are excluded from the designed-scope denominator.

## Evaluation criteria

- Preserve the exact parent VH/VL pair and declared HCDR3-only or HCDR123 edit mask.
- Report sample counts, sequence constraints and the sampling rule beside AAR.
- State the structural comparator, fitted atoms and measured regions for each scRMSD table.
- Keep the released control scores and newly executed measurements separate.

[Completed workflows and calculated results](comparison.md).
