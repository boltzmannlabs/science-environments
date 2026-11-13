# Benchmark: IL-36R: Reference-Conditioned CDR Redesign

**Task ID:** `task_015_il36r_igdesign_cdr_redesign`

**Task:** [IL-36R: Reference-Conditioned CDR Redesign](../../tasks/monoclonal_antibody_design/task_015_il36r_igdesign_cdr_redesign.md)

## Published Computational Metrics

**Source:** [IgDesign preprint, 2023](https://doi.org/10.1101/2023.12.08.570889), [ICLR GEM 2024 paper](https://openreview.net/pdf?id=awGfgUJdQY), and [released `Spesolimab-IL36R.csv`](https://raw.githubusercontent.com/AbSciBio/igdesign/70431eef0afaf0496d7d84e22dfdc1980ec9e70e/data/Spesolimab-IL36R.csv). Source code/data revision: [AbSciBio/igdesign @ `70431eef0afa`](https://github.com/AbSciBio/igdesign/tree/70431eef0afaf0496d7d84e22dfdc1980ec9e70e).

**Source CSV:** `Spesolimab-IL36R.csv`\
**SHA-256:** `5ee0782ad74cd0a5b955403ee5ee9fd374df6503be964f25a559a9c6670244ca`

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
| ABB2 | 0.6209 | 0.3009 | 0.6636 | 0.5699 | 0.3777 |
| ABB3 | 0.6263 | 0.3967 | 1.1363 | 0.8428 | 0.5498 |
| ABB3-LM | 1.1884 | 0.7102 | 1.2133 | 1.0856 | 0.6509 |
| ESMFold | 1.0185 | 0.6513 | 3.3469 | 2.2844 | 1.1768 |

## Evaluation Criteria

- Match the exact parent VH/VL pair and retain the source HCDR3-only or HCDR123 edit scope.
- Compare scRMSD using the same predictor, reference structure, atom selection, alignment and evaluated region.
- Report AAR for each CDR under the corresponding 1-shot or best-of-100 sampling rule.
- Retain source computational reference values separately from scores produced in a new run.
