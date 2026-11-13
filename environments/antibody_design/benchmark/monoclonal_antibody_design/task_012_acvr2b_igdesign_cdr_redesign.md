# Benchmark: ACVR2B: Reference-Conditioned CDR Redesign

**Task ID:** `task_012_acvr2b_igdesign_cdr_redesign`

**Task:** [ACVR2B: Reference-Conditioned CDR Redesign](../../tasks/monoclonal_antibody_design/task_012_acvr2b_igdesign_cdr_redesign.md)

## Published Computational Metrics

**Source:** [IgDesign preprint, 2023](https://doi.org/10.1101/2023.12.08.570889), [ICLR GEM 2024 paper](https://openreview.net/pdf?id=awGfgUJdQY), and [released `Bimagrumab-ACVR2B.csv`](https://raw.githubusercontent.com/AbSciBio/igdesign/70431eef0afaf0496d7d84e22dfdc1980ec9e70e/data/Bimagrumab-ACVR2B.csv). Source code/data revision: [AbSciBio/igdesign @ `70431eef0afa`](https://github.com/AbSciBio/igdesign/tree/70431eef0afaf0496d7d84e22dfdc1980ec9e70e).

**Source CSV:** `Bimagrumab-ACVR2B.csv`\
**SHA-256:** `5775fdfa2b23802aa4a295e7b98d3bbd52f4bd83440e33a3c9a0fca723dfcae9`

| Computational metric | Source scope | Direction |
| --- | --- | --- |
| Per-CDR amino-acid recovery (AAR) | Native-sequence recovery in the IgDesign reconstruction benchmark | Higher |
| 1-shot AAR | One generated sample per reference case | Higher |
| Best-of-100 AAR | Maximum recovery over 100 generated samples | Higher |
| CDR and Fv scRMSD (Å) | Predictor-specific structure consistency in the released CSV | Lower |

### Released Computational Reference Scores

The following values are the released positive-control row's precomputed scRMSD scores for the reference antibody. Values were transcribed from the hashed CSV on 10 November 2026 and are expressed in Å.

| Predictor | HCDR1 scRMSD | HCDR2 scRMSD | HCDR3 scRMSD | HCDR123 scRMSD | Fv scRMSD |
| --- | --- | --- | --- | --- | --- |
| ABB2 | 0.3593 | 0.3204 | 0.2988 | 0.3271 | 0.4350 |
| ABB3 | 0.3690 | 0.6996 | 0.8772 | 0.6819 | 0.7242 |
| ABB3-LM | 0.4611 | 0.6991 | 0.6228 | 0.6026 | 0.9211 |
| ESMFold | 0.4362 | 0.7643 | 0.5768 | 0.6075 | 1.1243 |

## Evaluation Criteria

- Match the exact parent VH/VL pair and retain the source HCDR3-only or HCDR123 edit scope.
- Compare scRMSD using the same predictor, reference structure, atom selection, alignment and evaluated region.
- Report AAR for each CDR under the corresponding 1-shot or best-of-100 sampling rule.
- Retain source computational reference values separately from scores produced in a new run.
