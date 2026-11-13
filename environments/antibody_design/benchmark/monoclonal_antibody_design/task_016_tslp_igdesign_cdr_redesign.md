# Benchmark: TSLP: Reference-Conditioned CDR Redesign

**Task ID:** `task_016_tslp_igdesign_cdr_redesign`

**Task:** [TSLP: Reference-Conditioned CDR Redesign](../../tasks/monoclonal_antibody_design/task_016_tslp_igdesign_cdr_redesign.md)

## Published Computational Metrics

**Source:** [IgDesign preprint, 2023](https://doi.org/10.1101/2023.12.08.570889), [ICLR GEM 2024 paper](https://openreview.net/pdf?id=awGfgUJdQY), and [released `Tezepelumab-TSLP.csv`](https://raw.githubusercontent.com/AbSciBio/igdesign/70431eef0afaf0496d7d84e22dfdc1980ec9e70e/data/Tezepelumab-TSLP.csv). Source code/data revision: [AbSciBio/igdesign @ `70431eef0afa`](https://github.com/AbSciBio/igdesign/tree/70431eef0afaf0496d7d84e22dfdc1980ec9e70e).

**Source CSV:** `Tezepelumab-TSLP.csv`\
**SHA-256:** `2cc6eaac6b6c97211549cb91d34b51056c448e0f4680b740e3b2a724fddc1ef0`

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
| ABB2 | 0.3149 | 0.5185 | 0.5838 | 0.5098 | 0.3738 |
| ABB3 | 0.6294 | 0.6500 | 2.2169 | 1.6091 | 0.7503 |
| ABB3-LM | 0.8363 | 0.6691 | 2.3307 | 1.7101 | 0.7559 |
| ESMFold | 0.7065 | 1.1262 | 4.6754 | 3.3217 | 1.3585 |

## Evaluation Criteria

- Match the exact parent VH/VL pair and retain the source HCDR3-only or HCDR123 edit scope.
- Compare scRMSD using the same predictor, reference structure, atom selection, alignment and evaluated region.
- Report AAR for each CDR under the corresponding 1-shot or best-of-100 sampling rule.
- Retain source computational reference values separately from scores produced in a new run.
