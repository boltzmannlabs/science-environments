# LCAT / 5BV7 — multi-CDR AbFlow reconstruction

Run: `run_004_abflow_multi_cdr`.

The completed multi-CDR track reports one candidate with sequence, structural and per-CDR recovery measurements.

## Methods

The released multi-CDR AbFlow model generated one 5BV7 candidate from the masked input. Candidate ordering was frozen before the authors' evaluator assessed the held-out native structure. The evaluation recorded sequence recovery, whole-structure agreement and per-CDR Kabsch Cα RMSD.

## Candidate measurements

| Endpoint | 5BV7 value |
| --- | --- |
| AAR H3 | 0.4211 |
| CAAR H3 | 0.2500 |
| TMscore | 0.9593 |
| LDDT | 0.7686 |
| RMSD(CA) CDRH3 | 19.8398 |
| RMSD(CA) CDRH3 aligned | 2.6302 |
| DockQ | 0.3450 |

## Per-CDR Kabsch RMSD comparison

| CDR RMSD Å ↓ | 5BV7 result | Published Table 2 mean |
| --- | --- | --- |
| H1 Kabsch | 0.6063 | 0.6300 |
| H2 Kabsch | 0.5307 | 0.5500 |
| H3 Kabsch | 2.6302 | 1.8300 |
| L1 Kabsch | 0.7824 | 0.6400 |
| L2 Kabsch | 0.1248 | 0.2500 |
| L3 Kabsch | 2.0849 | 0.6500 |

## Comparison context

The single-case H1, H2 and L2 Kabsch RMSDs are numerically lower than their published Table 2 means; H3, L1 and L3 are higher. Whole-structure TM-score, lDDT and DockQ are **0.9593/0.7686/0.3450**, alongside published full-atom aggregate values **0.9707/0.8151/0.4310**. In-place H3 placement and locally aligned H3 RMSD retain their separate definitions.

## Saved outputs

[Configuration](run.json) · [Metrics](metrics.csv) · [Candidate inventory](candidates.csv) · [Shortlist](shortlist.csv) · [Sequences](sequences.fasta) · [Structures](structures) · [Task comparison](../../../benchmark/monoclonal_antibody_design/task_004_lcat_reference_fab_cdrh3_reconstruction/comparison.md).
