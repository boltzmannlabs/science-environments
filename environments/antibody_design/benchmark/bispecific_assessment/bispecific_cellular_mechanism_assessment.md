# Benchmark: Bispecific Cellular Mechanism Assessment

**Task:** [Bispecific cellular mechanism assessment](../../tasks/bispecific_assessment/bispecific_cellular_mechanism_assessment.md)

## Benchmark Type

Classifier-validity and evidence-interpretation benchmark. Assesses whether an imaging-based readout supports a bispecific antibody mechanism comparison across conditions.

## Metrics and Reference Values

The numerical values below are supplied in the TxBench-Ab task description. They describe the underlying classifier study, not agent accuracy or minimum passing scores.

| Metric | Reference value | Benchmark context |
| --- | --- | --- |
| First-condition macro-F1 | 0.86 | Evaluated on 396 images. |
| Second-condition macro-F1 | 0.85 | Evaluated on 227 images. |
| Independent raters in the first original-condition panel | 4 | Model predictions are available for comparison. |
| Independent raters in the second original-condition panel | 5 | Model predictions are absent; this panel cannot provide model F1. |
| Baseline evidence selection | Exactly 2 distinct source identifiers | Required answer format; the accepted source pair is not public. |
| Validity judgment | 1 of the 3 categories defined in the task | No official accepted category or task-level agent score is released. |

## Benchmark Interpretation

Compare condition-specific confusion counts, class-wise F1, macro-F1, class support and rater agreement. Macro-F1 averages F1 across the declared class set; report undefined class scores explicitly. Interpret uncertainty at the biological-replicate level.

The central assessment is whether the evidence establishes generalization, demonstrates degradation, or remains insufficient. Similar aggregate F1 values alone do not settle that question. Released agent responses disagree on the baseline-source pair, so they cannot supply a verified answer key.

**References:** [TxBench-Ab task](https://github.com/latchbio/txbench-antibody-discovery/blob/main/evals/tcellengagerengineering_s6_imaging_flow_cytometry_0100/eval.json); [Claude result](https://github.com/latchbio/txbench-antibody-discovery/blob/b4a28e48202da521d6aeea82613c30fd4784e1ec/trajectories/tcellengagerengineering_s6_imaging_flow_cytometry_0100/claude-opus-5__claude-code__r1.json), [Codex result](https://github.com/latchbio/txbench-antibody-discovery/blob/b4a28e48202da521d6aeea82613c30fd4784e1ec/trajectories/tcellengagerengineering_s6_imaging_flow_cytometry_0100/gpt-5.6-sol__openai-codex__r1.json).
