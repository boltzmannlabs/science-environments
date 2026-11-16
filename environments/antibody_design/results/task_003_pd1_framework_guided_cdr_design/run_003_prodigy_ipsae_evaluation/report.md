# PD-1 — Prodigy and ipSAE follow-up

Run: `run_003_prodigy_ipsae_evaluation`.

The completed follow-up evaluates the same five candidates and H965 control used in the matched structural screen.

## Methods

Twelve Prodigy model evaluations and one ipSAE batch assessed the run_002_agcdr_antibmpnn Boltz2 models. Each candidate and the H965 control retain separate PD1:VH and PD1:VL records. Prodigy values use the raw returned score units; ipSAE is the PAE-weighted asymmetric interface score.

## Interface and energy results

| Record | VH Prodigy score ↓ | VL Prodigy score ↓ | VH ipSAE ↑ | VL ipSAE ↑ |
| --- | --- | --- | --- | --- |
| H965_control | -13.1 | -9.7 | 0.785058 | 0.269031 |
| PD1T3-011 | -12.4 | -8.9 | 0.891207 | 0.181306 |
| PD1T3-019 | -10.9 | -10.1 | 0.899311 | 0.815554 |
| PD1T3-038 | -12.6 | -13.7 | 0.726325 | 0.641322 |
| PD1T3-054 | -10.9 | -11.8 | 0.755745 | 0.390241 |
| PD1T3-069 | -7.9 | -10.9 | 0.317890 | 0.468605 |

## Candidate highlights

**PD1T3-019** leads the summed VH/VL ipSAE ranking, with scores **0.899311/0.815554**, compared with H965 **0.785058/0.269031**. **PD1T3-038** has the lowest candidate Prodigy scores on both pair records: **−12.6 VH** and **−13.7 VL**. Its control differences are **+0.5 VH** and **−4.0 VL** raw units, so the confidence and energy criteria identify complementary candidate strengths.

## Saved outputs

[Configuration](run.json) · [Metrics](metrics.csv) · [Candidate inventory](candidates.csv) · [Shortlist](shortlist.csv) · [Sequences](sequences.fasta) · [Task comparison](../../../benchmark/monoclonal_antibody_design/task_003_pd1_framework_guided_cdr_design/comparison.md).
