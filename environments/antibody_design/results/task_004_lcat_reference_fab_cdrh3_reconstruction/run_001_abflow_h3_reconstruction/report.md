# LCAT / 5BV7 — AbFlow H3 reconstruction

Run: `run_001_abflow_h3_reconstruction`.

The completed pose-blind workflow generated and evaluated one single sample plus a 32-structure pool.

## Methods and sample scope

AbFlow used the released paratope-centric model and the masked 5BV7 input. Pose-blind generation comprised one single-sample result and a separate 32-draw pool. Candidate ordering was frozen from the recorded model ranking before evaluation against the held-out native structure.

All 33 structures retained the declared framework and light-chain identities and the 19-residue H3 length. The authors' evaluator produced sequence recovery, structural agreement and H3-only docking measurements.

## Single-sample and pool results

| Endpoint | Single sample | 32-sample pool mean |
| --- | --- | --- |
| AAR H3 | 0.5263 | 0.5263 |
| CAAR H3 | 0.3333 | 0.3333 |
| TMscore | 0.9648 | 0.9653 |
| LDDT | 0.8105 | 0.8104 |
| RMSD(CA) CDRH3 | 14.4720 | 14.5787 |
| RMSD(CA) CDRH3 aligned | 2.0418 | 1.9862 |
| DockQ | 0.8890 | 0.8611 |

## Frozen selection and comparison

The frozen first-ranked entries are **5bv7_h3_000** for the single sample and **5bv7_h3_015** for the pool. The single-sample result has AAR **0.5263**, CAAR **0.3333** and DockQ **0.8890**. The task comparison presents these 5BV7 observations alongside the published 60-complex aggregate, retaining the separate single-sample and pool scopes. H3 in-place RMSD describes placement, while H3-aligned RMSD uses local Kabsch alignment.

## Saved outputs

[Configuration](run.json) · [Metrics](metrics.csv) · [Candidate inventory](candidates.csv) · [Shortlist](shortlist.csv) · [Sequences](sequences.fasta) · [Structures](structures) · [Task comparison](../../../benchmark/monoclonal_antibody_design/task_004_lcat_reference_fab_cdrh3_reconstruction/comparison.md).
