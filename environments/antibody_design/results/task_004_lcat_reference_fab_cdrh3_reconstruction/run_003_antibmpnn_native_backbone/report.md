# LCAT / 5BV7 — AntiBMPNN fixed-native-backbone sequence design

Run: `run_003_antibmpnn_native_backbone`.

The completed workflow produced a 32-candidate library with frozen ordering and matched reference evaluation.

## Methods

AntiBMPNN generated 32 H3 sequences on the supplied native backbone, with the H3 sequence masked during preparation. Sequence checks verified the declared framework/light-chain identities and the 19-residue loop length. The frozen ordering uses the model score, followed by sequence-recovery evaluation with the authors' evaluator.

## Results

| Endpoint | 32-sample mean | Frozen rank-1 result |
| --- | --- | --- |
| AAR H3 | 0.5526 | 0.5789 |
| CAAR H3 | 0.3542 | 0.3333 |

## Interpretation

The fixed-geometry sequence-design track has mean AAR **0.5526** and CAAR **0.3542**. The supplied backbone defines this track's conditioning; sequence recovery is its reported design endpoint.

The frozen first-ranked candidate is **5bv7_abmpnn_008**.

## Saved outputs

[Configuration](run.json) · [Metrics](metrics.csv) · [Candidate inventory](candidates.csv) · [Shortlist](shortlist.csv) · [Sequences](sequences.fasta) · [Structures](structures) · [Task comparison](../../../benchmark/monoclonal_antibody_design/task_004_lcat_reference_fab_cdrh3_reconstruction/comparison.md).
