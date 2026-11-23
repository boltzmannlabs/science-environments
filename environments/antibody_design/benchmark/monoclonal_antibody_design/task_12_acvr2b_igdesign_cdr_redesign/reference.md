# Benchmark: ACVR2B: Bimagrumab IgDesign CDR Redesign

**Task ID:** `task_12_acvr2b_igdesign_cdr_redesign`

**Task:** [ACVR2B: Bimagrumab IgDesign CDR Redesign](../../../tasks/monoclonal_antibody_design/task_012_acvr2b_igdesign_cdr_redesign.md)

## Published Results

**Source:** [IgDesign benchmark paper (bioRxiv 2023.12.08.570889v2)](https://www.biorxiv.org/content/10.1101/2023.12.08.570889v2) and the [released benchmark CSV](Bimagrumab-ACVR2B.csv) (SHA-256 `5775fdfa2b23802aa4a295e7b98d3bbd52f4bd83440e33a3c9a0fca723dfcae9`).

The following are native-reference C-alpha scRMSD values (A) for the Bimagrumab Fv against the 5NGV reference, reported by the released benchmark under four different structure predictors. Lower is better within each predictor's own protocol; these are native-reference predictions, not redesign endpoints.

| Predictor | HCDR1 | HCDR2 | HCDR3 | HCDR123 | Fv |
| --- | ---: | ---: | ---: | ---: | ---: |
| ABB2 | 0.3593 | 0.3204 | 0.2988 | 0.3271 | 0.4350 |
| ABB3 | 0.3690 | 0.6996 | 0.8772 | 0.6819 | 0.7242 |
| ABB3-LM | 0.4611 | 0.6991 | 0.6228 | 0.6026 | 0.9211 |
| ESMFold | 0.4362 | 0.7643 | 0.5768 | 0.6075 | 1.1243 |

Provenance: `Bimagrumab-ACVR2B.csv`, native-reference rows, as released with the benchmark paper. Per-case AAR values from the paper were not retrievable in this session (source fetch timed out), so AAR here is executed-only.

## Evaluation Criteria

| Criterion | Comparison requirement | Acceptance boundary |
| --- | --- | --- |
| Native-recovery AAR | Per-position identity vs the native CDR over generated samples (1-shot, best-of-100, mean). | Higher is better; report all three summaries. No universal pass threshold. |
| CDR scRMSD | Predict the native and each candidate Fv under an identical AlphaFold2-Multimer v3 protocol; whole-Fv Kabsch superposition; regional C-alpha RMSD for HCDR1/2/3/123. | Lower is better; a candidate must beat the native HCDR123 scRMSD (0.4434 A) within the same predictor to count as an improvement. |
| Fv integrity | Report Fv-wide (VH+VL) C-alpha scRMSD alongside regional values. | Fv should stay near the native 1.2140 A, i.e. the VH/VL assembly is essentially unperturbed by CDR edits. |
| Published endpoint comparison | Match the exact predictor and protocol provenance before comparing with a released row. | Rows from different predictors must be labelled non-comparable. |

## Saved workflow results

See [comparison.md](comparison.md) for the consolidated comparison across the saved run IDs.
