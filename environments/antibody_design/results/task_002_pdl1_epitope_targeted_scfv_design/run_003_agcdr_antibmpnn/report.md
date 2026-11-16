# PD-L1 / scFv — Backbone diversification and AntiBMPNN results

Run: `run_003_agcdr_antibmpnn`.

The completed workflow produced a paired-candidate evaluation with saved confidence, coverage and hotspot measurements.

## Methods

AgCDR-Diff supplied diversified backbones, followed by AntiBMPNN sequence design. Eight candidates received Boltz2 evaluation and the same epitope and hotspot analysis used for the sequence-design route. The task used the prepared human PD-L1 construct and paired-framework context.

## Candidate results

| Candidate | ipTM ↑ | Complex pLDDT | Epitope coverage | Hotspots recovered |
| --- | --- | --- | --- | --- |
| t002r1_agcdr1_c5 | 0.8383 | 0.8705 | 0.500 | 2 |
| t002r1_agcdr1_c2 | 0.7458 | 0.8545 | 0.536 | 1 |
| t002r1_agcdr1_c1 | 0.5429 | 0.8667 | 0.571 | 1 |
| t002r1_agcdr1_c4 | 0.5379 | 0.8516 | 0.607 | 2 |
| t002r1_agcdr1_c0 | 0.5292 | 0.8818 | 0.536 | 1 |
| t002r1_agcdr1_c6 | 0.4625 | 0.8525 | 0.500 | 0 |
| t002r1_agcdr1_c3 | 0.3751 | 0.8711 | 0.464 | 0 |
| t002r1_agcdr1_c7 | 0.3669 | 0.9083 | 0.357 | 0 |

## Findings

**t002r1_agcdr1_c5** has the highest ipTM in this run (**0.8383**). The evaluated set contains **5/8** hotspot-positive candidates. Epitope coverage spans **0.357–0.607**.

## Comparison context

The task-level comparison places these candidate scores alongside the other completed PD-L1 routes. H5 reconstruction uses a separate structural-control endpoint, while these tables report candidate confidence and model-derived epitope engagement.

## Saved outputs

[Configuration](run.json) · [Metrics](metrics.csv) · [Candidate inventory](candidates.csv) · [Shortlist](shortlist.csv) · [Sequences](sequences.fasta) · [Structures](structures) · [Task comparison](../../../benchmark/monoclonal_antibody_design/task_002_pdl1_epitope_targeted_scfv_design/comparison.md).
