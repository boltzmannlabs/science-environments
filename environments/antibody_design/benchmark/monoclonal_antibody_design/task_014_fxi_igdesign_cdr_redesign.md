# Benchmark: Factor XI: Reference-Conditioned CDR Redesign

**Task ID:** `task_014_fxi_igdesign_cdr_redesign`

**Task:** [Factor XI: Reference-Conditioned CDR Redesign](../../tasks/monoclonal_antibody_design/task_014_fxi_igdesign_cdr_redesign.md)

## Published Computational Metrics

**Source:** [IgDesign preprint, 2023](https://doi.org/10.1101/2023.12.08.570889), [ICLR GEM 2024 paper](https://openreview.net/pdf?id=awGfgUJdQY), and [released `Osocimab-FXI.csv`](https://raw.githubusercontent.com/AbSciBio/igdesign/70431eef0afaf0496d7d84e22dfdc1980ec9e70e/data/Osocimab-FXI.csv). Source code/data revision: [AbSciBio/igdesign @ `70431eef0afa`](https://github.com/AbSciBio/igdesign/tree/70431eef0afaf0496d7d84e22dfdc1980ec9e70e).

**Source CSV:** `Osocimab-FXI.csv`\
**SHA-256:** `850552125e42524d2ff33e2ff003e4f9b4b413124db9eb69dc0623a24e50fd28`

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
| ABB2 | 0.3017 | 0.4394 | 1.9335 | 1.3245 | 0.5759 |
| ABB3 | 0.5247 | 0.5213 | 2.1584 | 1.4964 | 0.6669 |
| ABB3-LM | 0.3971 | 0.3698 | 1.9120 | 1.3115 | 0.6241 |
| ESMFold | 0.7708 | 1.0993 | 3.5167 | 2.4578 | 1.1314 |

## Evaluation Criteria

- Match the exact parent VH/VL pair and retain the source HCDR3-only or HCDR123 edit scope.
- Compare scRMSD using the same predictor, reference structure, atom selection, alignment and evaluated region.
- Report AAR for each CDR under the corresponding 1-shot or best-of-100 sampling rule.
- Retain source computational reference values separately from scores produced in a new run.
