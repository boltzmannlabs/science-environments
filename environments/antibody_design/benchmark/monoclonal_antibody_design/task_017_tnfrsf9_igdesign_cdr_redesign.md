# Benchmark: TNFRSF9 / 4-1BB: Reference-Conditioned CDR Redesign

**Task ID:** `task_017_tnfrsf9_igdesign_cdr_redesign`

**Task:** [TNFRSF9 / 4-1BB: Reference-Conditioned CDR Redesign](../../tasks/monoclonal_antibody_design/task_017_tnfrsf9_igdesign_cdr_redesign.md)

## Published Computational Metrics

**Source:** [IgDesign preprint, 2023](https://doi.org/10.1101/2023.12.08.570889), [ICLR GEM 2024 paper](https://openreview.net/pdf?id=awGfgUJdQY), and [released `Utomilumab-TNFRSF9.csv`](https://raw.githubusercontent.com/AbSciBio/igdesign/70431eef0afaf0496d7d84e22dfdc1980ec9e70e/data/Utomilumab-TNFRSF9.csv). Source code/data revision: [AbSciBio/igdesign @ `70431eef0afa`](https://github.com/AbSciBio/igdesign/tree/70431eef0afaf0496d7d84e22dfdc1980ec9e70e).

**Source CSV:** `Utomilumab-TNFRSF9.csv`\
**SHA-256:** `5b805d1ee43902b4f0a8520085fb1c2921776f4d8620b70ff046789b4525619c`

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
| ABB2 | 0.2646 | 0.3260 | 0.4191 | 0.3459 | 0.3546 |
| ABB3 | 0.4546 | 0.3979 | 0.7384 | 0.5596 | 0.4268 |
| ABB3-LM | 0.4905 | 0.4455 | 0.8773 | 0.6462 | 0.4578 |
| ESMFold | 0.9242 | 0.7900 | 1.9720 | 1.3686 | 1.1179 |

## Evaluation Criteria

- Match the exact parent VH/VL pair and retain the source HCDR3-only or HCDR123 edit scope.
- Compare scRMSD using the same predictor, reference structure, atom selection, alignment and evaluated region.
- Report AAR for each CDR under the corresponding 1-shot or best-of-100 sampling rule.
- Retain source computational reference values separately from scores produced in a new run.
