# Benchmark: Complement C5: Reference-Conditioned CDR Redesign

**Task ID:** `task_013_c5_igdesign_cdr_redesign`

**Task:** [Complement C5: Reference-Conditioned CDR Redesign](../../tasks/monoclonal_antibody_design/task_013_c5_igdesign_cdr_redesign.md)

## Published Computational Metrics

**Source:** [IgDesign preprint, 2023](https://doi.org/10.1101/2023.12.08.570889), [ICLR GEM 2024 paper](https://openreview.net/pdf?id=awGfgUJdQY), and [released `Eculizumab-C5.csv`](https://raw.githubusercontent.com/AbSciBio/igdesign/70431eef0afaf0496d7d84e22dfdc1980ec9e70e/data/Eculizumab-C5.csv). Source code/data revision: [AbSciBio/igdesign @ `70431eef0afa`](https://github.com/AbSciBio/igdesign/tree/70431eef0afaf0496d7d84e22dfdc1980ec9e70e).

**Source CSV:** `Eculizumab-C5.csv`\
**SHA-256:** `787d440681730f7b50cd4885324bc2ea3e0b14bddafbf67b4354d8e535b065ad`

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
| ABB2 | 1.1479 | 1.0812 | 2.2289 | 1.7452 | 1.2950 |
| ABB3 | 1.3176 | 1.1441 | 2.3998 | 1.8901 | 1.3017 |
| ABB3-LM | 1.2023 | 1.1968 | 1.8354 | 1.5403 | 1.2441 |
| ESMFold | 0.8494 | 1.0668 | 1.6620 | 1.3477 | 1.2044 |

## Evaluation Criteria

- Match the exact parent VH/VL pair and retain the source HCDR3-only or HCDR123 edit scope.
- Compare scRMSD using the same predictor, reference structure, atom selection, alignment and evaluated region.
- Report AAR for each CDR under the corresponding 1-shot or best-of-100 sampling rule.
- Retain source computational reference values separately from scores produced in a new run.
