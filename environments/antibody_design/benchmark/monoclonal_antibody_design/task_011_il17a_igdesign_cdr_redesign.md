# Benchmark: IL-17A: Reference-Conditioned CDR Redesign

**Task ID:** `task_011_il17a_igdesign_cdr_redesign`

**Task:** [IL-17A: Reference-Conditioned CDR Redesign](../../tasks/monoclonal_antibody_design/task_011_il17a_igdesign_cdr_redesign.md)

## Published Computational Metrics

**Source:** [IgDesign preprint, 2023](https://doi.org/10.1101/2023.12.08.570889), [ICLR GEM 2024 paper](https://openreview.net/pdf?id=awGfgUJdQY), and [released `Afasevikumab-IL17A.csv`](https://raw.githubusercontent.com/AbSciBio/igdesign/70431eef0afaf0496d7d84e22dfdc1980ec9e70e/data/Afasevikumab-IL17A.csv). Source code/data revision: [AbSciBio/igdesign @ `70431eef0afa`](https://github.com/AbSciBio/igdesign/tree/70431eef0afaf0496d7d84e22dfdc1980ec9e70e).

**Source CSV:** `Afasevikumab-IL17A.csv`\
**SHA-256:** `71aeb8448410ddadd9ca65c126b7663399a5357eb51ffc80918c01071d24dd44`

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
| ABB2 | 0.4138 | 0.4536 | 0.5041 | 0.4705 | 0.4109 |
| ABB3 | 0.4568 | 0.3973 | 1.5672 | 1.1488 | 0.7100 |
| ABB3-LM | 0.5392 | 0.4715 | 1.1320 | 0.8769 | 0.6760 |
| ESMFold | 1.0242 | 2.6093 | 3.6162 | 2.9159 | 1.5575 |

## Evaluation Criteria

- Match the exact parent VH/VL pair and retain the source HCDR3-only or HCDR123 edit scope.
- Compare scRMSD using the same predictor, reference structure, atom selection, alignment and evaluated region.
- Report AAR for each CDR under the corresponding 1-shot or best-of-100 sampling rule.
- Retain source computational reference values separately from scores produced in a new run.
