# Benchmark: Bispecific CNS Shuttle Integrated Gate

**Task:** [Bispecific CNS shuttle integrated gate](../../tasks/bispecific_assessment/bispecific_cns_shuttle_integrated_gate.md)

## Benchmark Type

Exposure-calculation and integrated-decision benchmark. Assesses three shuttle-specific brain measurements, comparative durability and the evidence supporting a proposed dosing interval.

## Metrics and Reference Values

These values are reported in released TxBench-Ab agent results. They have not been independently verified against the original study data and are not official grading targets.

| Metric | Reported value | Benchmark context |
| --- | --- | --- |
| Shuttle-1 mean brain exposure | 0.38 %ID/g | Arithmetic mean at 7 days. |
| Shuttle-2 mean brain exposure | 0.58 %ID/g | Arithmetic mean at 7 days. |
| Shuttle-3 mean brain exposure | 0.4375 %ID/g | Arithmetic mean at 7 days. |
| Dosing-interval conclusion | `NOT_SUPPORTED` | Visible Claude and Codex results agree. |
| Principal limiting factor | `NON_RESIDUALIZING_LABEL_BIAS` | Interpretation reported by both agents. |
| Shuttle recommendation | Claude: `Shuttle-2`; Codex: `INDETERMINATE` | The results disagree; no official accepted recommendation is public. |

## Benchmark Interpretation

`%ID/g` means percentage of injected dose per gram of tissue. Calculate each mean from the eligible individual-animal Brain observations at 7 days, preserving sample counts and exclusions. Other organs, timepoints and controls are not substitutes for those observations.

Judge comparative durability and dosing support separately. The highest observed mean alone does not establish a reliable advantage, and label persistence does not necessarily represent intact-antibody persistence. Interpret the limiting factor using the supplied label chemistry and replicate evidence. Numerical tolerances must be defined for the evaluation; they are not supplied by these reported values.

**References:** [TxBench-Ab task](https://github.com/latchbio/txbench-antibody-discovery/blob/main/evals/cd98hccrossspeciesengineering_s8_pk_0035/eval.json); [Claude result](https://github.com/latchbio/txbench-antibody-discovery/blob/b4a28e48202da521d6aeea82613c30fd4784e1ec/trajectories/cd98hccrossspeciesengineering_s8_pk_0035/claude-opus-5__claude-code__r1.json), [Codex result](https://github.com/latchbio/txbench-antibody-discovery/blob/b4a28e48202da521d6aeea82613c30fd4784e1ec/trajectories/cd98hccrossspeciesengineering_s8_pk_0035/gpt-5.6-sol__openai-codex__r1.json).
