# PD-L1 / scFv — AntiBMPNN sequence-design results

Run: `run_001_antibmpnn_sequence_only`.

The completed workflow produced a paired-candidate evaluation with saved confidence, coverage and hotspot measurements.

## Methods

AntiBMPNN generated eight paired sequence designs from the prepared framework; the saved inventory also contains a recombination record. Five candidates received Boltz2 evaluation. The task used the prepared human PD-L1 construct and paired-framework context.

## Candidate results

| Candidate | ipTM ↑ | Complex pLDDT | Epitope coverage | Hotspots recovered |
| --- | --- | --- | --- | --- |
| t002r1_bmpnn_02 | 0.4559 | 0.8980 | 0.536 | 0 |
| t002r1_bmpnn_03 | 0.4427 | 0.8885 | 0.357 | 0 |
| t002r1_bmpnn_00 | 0.3213 | 0.8924 | 0.429 | 0 |
| t002r1_bmpnn_01 | 0.3195 | 0.9304 | 0.000 | 0 |
| t002r1_bmpnn_recomb23 | 0.2809 | 0.9240 | 0.000 | 0 |

## Findings

**t002r1_bmpnn_02** has the highest ipTM in this run (**0.4559**). The evaluated set contains **0/5** hotspot-positive candidates. Epitope coverage spans **0.000–0.536**.

## Comparison context

The task-level comparison places these candidate scores alongside the other completed PD-L1 routes. H5 reconstruction uses a separate structural-control endpoint, while these tables report candidate confidence and model-derived epitope engagement.

## Saved outputs

[Configuration](run.json) · [Metrics](metrics.csv) · [Candidate inventory](candidates.csv) · [Shortlist](shortlist.csv) · [Sequences](sequences.fasta) · [Structures](structures) · [Task comparison](../../../benchmark/monoclonal_antibody_design/task_002_pdl1_epitope_targeted_scfv_design/comparison.md).
