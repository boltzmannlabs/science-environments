# Benchmark: Bispecific CNS Delivery Assessment

**Task:** [Bispecific CNS delivery assessment](../../tasks/bispecific_assessment/bispecific_cns_delivery_assessment.md)

## Benchmark Type

Study-specific comparative delivery benchmark. Assesses whether matched-payload antibody shuttles meet a declared CNS-delivery objective and whether the evidence supports candidate advancement.

## Metrics and Reference Values

This task has no fixed study dataset or published numerical baseline. Reference values must come from the supplied candidate and control measurements.

| Metric | Reference value | Benchmark context |
| --- | --- | --- |
| Tissue exposure | Study-specific | Per-candidate measurements and summaries at matched tissue and timepoint, with source units. |
| Relative exposure | Study-specific | Requested difference or fold change against a named comparator. |
| Replication and uncertainty | Study-specific | Independent sample counts, variability and uncertainty under the declared analysis protocol. |
| Compartment-specific delivery | Study-specific | Fractionation or spatial evidence relevant to the stated delivery objective. |
| Intact-analyte exposure | Study-specific | Evidence that the measured signal represents intact antibody or payload. |
| Candidate recommendation | Candidate identity or `INDETERMINATE` | Determined by the supplied advancement criteria. |
| Dosing conclusion | `SUPPORTED`, `NOT_SUPPORTED` or `NEEDS_MORE_EVIDENCE` | Evaluated separately from candidate selection. |

## Benchmark Interpretation

Compare candidates under matched study conditions and retain individual observations, units, timepoints and controls. Define the numerical tolerances and reference decision for that study before evaluating an agent.

Whole-brain signal, compartment-specific delivery and intact-antibody exposure answer different questions. Values from another shuttle study are not baseline answers for this task. In particular, the related 5.85-fold comparison and three 7-day exposure means belong to the distinct tasks linked below.

**Related benchmarks:** [CNS readout comparison](bispecific_cns_readout_comparison.md); [CNS shuttle integrated gate](bispecific_cns_shuttle_integrated_gate.md).
