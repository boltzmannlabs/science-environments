# Benchmark: Bispecific CNS Readout Comparison

**Task:** [Bispecific CNS readout comparison](../../tasks/bispecific_assessment/bispecific_cns_readout_comparison.md)

## Benchmark Type

Quantitative readout-comparison benchmark. Assesses concentration-ratio calculation and selection of the evidence most relevant to the declared brain-delivery objective.

## Metrics and Reference Values

These values appear in released TxBench-Ab agent results. The original measurement data and official grades are not public; the values are reference observations, not verified expected answers.

| Metric | Reported value | Benchmark context |
| --- | --- | --- |
| CD98hc shuttle whole-brain concentration | 1.58 nM | Day-5 primary radiotracing readout, as reported by the agents. |
| TfR1 shuttle whole-brain concentration | 0.27 nM | Same timepoint and readout. |
| Higher/lower concentration ratio | 5.85-fold | 1.58 / 0.27 = 5.851851851851852 before rounding. |
| Governing readout | `microscopy` | Selected in the visible Claude and Codex results. |
| Candidate recommendation | `TfR1_shuttle` | Selected in those results; not an official accepted answer. |

## Benchmark Interpretation

Calculate the ratio from the primary whole-brain measurements at the final reported timepoint, with matching units and a nonzero denominator. Preserve the source values and aggregation method. The displayed rounding does not establish an acceptance tolerance.

Assess the candidate recommendation against the intended compartment using whole-brain, capillary-depletion and microscopy evidence. A larger bulk concentration does not itself establish better compartment-specific delivery. The local task permits `INDETERMINATE` when the evidence does not support a selection.

**References:** [TxBench-Ab task](https://github.com/latchbio/txbench-antibody-discovery/blob/main/evals/cd98hctessiershuttle_s8_tissue_biodistribution_imaging_0084/eval.json); [Claude result](https://github.com/latchbio/txbench-antibody-discovery/blob/b4a28e48202da521d6aeea82613c30fd4784e1ec/trajectories/cd98hctessiershuttle_s8_tissue_biodistribution_imaging_0084/claude-opus-5__claude-code__r1.json), [Codex result](https://github.com/latchbio/txbench-antibody-discovery/blob/b4a28e48202da521d6aeea82613c30fd4784e1ec/trajectories/cd98hctessiershuttle_s8_tissue_biodistribution_imaging_0084/gpt-5.6-sol__openai-codex__r1.json).
