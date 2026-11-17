# LCAT / 5BV7 — DiffAb pose-conditioned H3 co-design

Run: `run_002_diffab_local`.

The completed workflow produced a 32-candidate library with frozen ordering and matched reference evaluation.

## Methods

DiffAb jointly sampled sequence and structure for H3 using the native-complex context. The workflow generated 32 unique 19-residue H3 sequences. Designed H3 blocks were mapped by sequence position onto the evaluation scaffold, with deterministic sample ordering frozen before the authors' evaluator was applied.

## Results

| Endpoint | 32-sample mean | Frozen rank-1 result |
| --- | --- | --- |
| AAR H3 | 0.2747 | 0.2105 |
| CAAR H3 | 0.1458 | 0.0833 |
| RMSD(CA) CDRH3 | 4.5504 | 4.8815 |
| RMSD(CA) CDRH3 aligned | 2.9005 | 3.1348 |
| TMscore | 0.9785 | 0.9779 |
| LDDT | 0.8956 | 0.8984 |
| DockQ | 0.5877 | 0.6150 |

## Interpretation

The pose-conditioned track has mean H3 in-place RMSD **4.5504 Å**, TM-score **0.9785**, lDDT **0.8956** and DockQ **0.5877**. The task comparison reports these 5BV7 sample means under the stated pose-conditioned protocol alongside the other tracks.

The frozen first-ranked candidate is **5bv7_diffab_g000**.

## Saved outputs

[Configuration](run.json) · [Metrics](metrics.csv) · [Candidate inventory](candidates.csv) · [Shortlist](shortlist.csv) · [Sequences](sequences.fasta) · [Structures](structures) · [Task comparison](../../../benchmark/monoclonal_antibody_design/task_004_lcat_reference_fab_cdrh3_reconstruction/comparison.md).
