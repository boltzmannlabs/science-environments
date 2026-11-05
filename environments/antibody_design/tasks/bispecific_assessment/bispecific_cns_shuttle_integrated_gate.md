# Task: bispecific_cns_shuttle_integrated_gate

## Description

Compare three bispecific CNS-shuttle candidates carrying the same payload. Determine whether the supplied data support a comparative brain-durability advantage and whether they justify the requested dosing-interval commitment.

## Target

**Candidates:** `Shuttle-1`, `Shuttle-2`, and `Shuttle-3`; the control is not an eligible selection\
**Required Readout:** Each shuttle's observed arithmetic mean at the 7-day Brain timepoint, in `%ID/g`\
**Required Data:** Individual-animal organ measurements, timepoints, replicate identifiers, units, and documented exclusions\
**Study Metadata:** Binding specificities, molecular formats, payload equivalence, species cross-reactivity, target expression, dose, route, label chemistry, processing, and calibration\
**Decision Criteria:** Supplied brain-durability definition and dosing-interval rule, with relevant exposure and pharmacodynamic evidence

## Data Analysis Tool Capabilities

Use verified capabilities supplied by the execution environment in the following order. Record unavailable capabilities and leave their required evidence unresolved.

| Stage | Capability | Expected Evidence |
| --- | --- | --- |
| 1. Audit records | Verify shuttle/control identity, Brain labels, 7-day observations, units, and exclusions. | Correctly matched candidate–sample records. |
| 2. Calculate the three means | Aggregate eligible individual-animal Brain measurements for each shuttle. | Arithmetic mean `%ID/g`, independent sample count, and retained observations. |
| 3. Compare uncertainty | Assess variability and differences under the supplied decision rule. | Candidate comparison without an assumed winner. |
| 4. Review durability evidence | Assess label/analyte integrity and the relevance of measured tissue signal. | Supported durability interpretation and limiting factors. |
| 5. Assess the interval conclusion | Review supplied exposure, target-engagement, and pharmacodynamic evidence. | Evidence for or against the requested interval commitment. |
| 6. Report the decision | Separate advancement recommendation from dosing support. | Exact benchmark answer and reproducible analysis report. |

## Evaluation Metrics

| Criterion | Measurements and Evidence | Evaluation Rule |
| --- | --- | --- |
| Required observed means | Arithmetic mean `%ID/g` for each shuttle’s Brain observations at 7 days. | Use only documented filters; preserve every included observation and its replicate identity. |
| Variability and comparison | Independent sample counts, within-group variability, between-candidate differences, and uncertainty. | Apply the prespecified rule; the highest sample mean is not automatically a defensible winner. |
| Label-related limitation | Supplied evidence for label stability, catabolism, and whether signal tracks intact molecule. | Select label bias only when supported; do not infer it from candidate ranking. |
| Biological limitation | Sample size, biological variation, control behavior, and study comparability. | Keep uncertainty from limited data distinct from a demonstrated absence of benefit. |
| Dosing support | Exposure duration, compartment relevance, target engagement, pharmacodynamics, and repeat-dose evidence. | Use `NOT_SUPPORTED` when the evidence cannot justify weekly or longer dosing. |
| Integrated recommendation | Consistency of the requested means, decision rule, limitations, and interval conclusion. | The control is not a candidate; permit `INDETERMINATE` even when all three means are available. |

Keep the existing candidate names, answer fields, units, and 7-day observation requirement. Detailed statistics belong in the report; missing observations must not be replaced with zeros or inferred values.

Published reference evidence and evaluation details: [benchmark](../../benchmark/bispecific_assessment/bispecific_cns_shuttle_integrated_gate.md).

## Expected Output

**Required Report:** `report.md`, containing the three calculations, candidate comparison, recommendation rationale, and limitations.

Return the benchmark answer in this format, without additional fields:

```text
<EVAL_ANSWER>
{"recommendation":{"recommended_shuttle":"<Shuttle-1|Shuttle-2|Shuttle-3|INDETERMINATE>","dosing_interval_supported":"<WEEKLY|LONGER_THAN_WEEKLY|NOT_SUPPORTED>"},"limiting_factor":"<NON_RESIDUALIZING_LABEL_BIAS|SMALL_SAMPLE_SIZE_AND_BIOLOGICAL_VARIABILITY|NONE_IDENTIFIED>","brain_7d_shuttle1_pct_id_g":<observed mean>,"brain_7d_shuttle2_pct_id_g":<observed mean>,"brain_7d_shuttle3_pct_id_g":<observed mean>}
</EVAL_ANSWER>
```

## Important Instructions

- Compute all three means from the supplied Brain observations; do not substitute another organ, timepoint, control, or narrative estimate.
- Return `NEEDS_INPUT` when required tables are absent. Do not fabricate numeric fields.
- Use `INDETERMINATE` when candidates cannot be distinguished and `NOT_SUPPORTED` when dosing evidence is insufficient.
- Select the limiting factor from the actual label and replicate evidence. Report the three observed means even when no candidate is selected, provided the data support their calculation.
- Single-dose tissue persistence alone does not establish intact-molecule retention, repeat-dose efficacy, or clinical dosing.
