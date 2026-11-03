# Task: bispecific_cns_delivery_assessment

## Description

Compare bispecific CNS-delivery candidates carrying the same payload and determine whether the supplied evidence supports advancing a candidate. Distinguish total-tissue signal, delivery to the intended compartment, intact-antibody exposure, and biological activity.

## Target

**Candidates:** Supplied shuttle/target identities, payload, molecular formats, species context, and matched control\
**Objective:** Declared tissue compartment, delivery endpoint, advancement criteria, and dosing-interval question\
**Required Data:** Individual-animal tissue measurements, serum exposure where available, units, sampling timepoints, and replicate identifiers\
**Study Metadata:** Dose, route, formulation, processing, calibration, normalization, exclusions, and missing-data handling\
**Supporting Evidence:** Label chemistry/stability, analyte integrity, tissue fractionation, microscopy, and any supplied target-engagement or pharmacodynamic data

## Data Analysis Tool Capabilities

Use verified capabilities supplied by the execution environment in the following order. Record unavailable capabilities and leave their required evidence unresolved.

| Stage | Capability | Expected Evidence |
| --- | --- | --- |
| 1. Validate study records | Check candidate/control identity, payload, units, dose/route comparability, and sample metadata. | Audited study table and documented exclusions. |
| 2. Calculate observed readouts | Aggregate the requested tissue measurements at the correct experimental-unit level. | Individual observations, replicate counts, means, and uncertainty. |
| 3. Compare tissue compartments | Integrate bulk measurements, fractionation, and spatial imaging where supplied. | Compartment-specific findings and measurement limitations. |
| 4. Assess label and analyte validity | Review label stability, degradation, processing, and intact-molecule evidence. | Supported interpretation of the measured signal. |
| 5. Compare candidates and exposure evidence | Evaluate effect sizes, controls, variability, and supplied exposure/response information. | Candidate comparison and the evidence supporting or limiting a dosing conclusion. |
| 6. Decide and report | Apply the declared objective and decision rule. | Candidate decision, governing readout, calculations, uncertainty, and missing evidence. |

## Evaluation Metrics

| Criterion | Measurements and Evidence | Evaluation Rule |
| --- | --- | --- |
| Data comparability | Units, tissue, timepoint, dose/route, normalization, exclusions, and independent replicate count. | Compare like-for-like measurements; do not silently pool incompatible studies. |
| Observed exposure | Per-candidate/control values, arithmetic means or specified summaries, and variability. | Retain individual observations and distinguish biological from technical replicates. |
| Relative difference | Requested absolute differences and fold changes, with explicit numerator and denominator. | Use the prescribed readout and aggregation; a zero denominator makes the ratio undefined. |
| Compartment evidence | Bulk tissue signal, vascular/parenchymal fractionation, and quantitative spatial evidence where available. | Report fraction purity, sampling limits, and processing uncertainty; total tissue signal alone cannot establish parenchymal delivery. |
| Analyte integrity | Evidence that label or assay signal tracks intact antibody or payload. | Account for label behavior and degradation; signal persistence need not mean intact-molecule persistence. |
| Decision confidence | Effect size, biological variability, uncertainty, controls, and the predeclared meaningful difference. | Do not select a winner from a small unexplained difference; report indeterminate comparisons. |
| Dosing evidence | Supplied exposure, target engagement, pharmacodynamic duration, and repeat-dose evidence. | Keep a delivery comparison separate from support for a repeat-dose interval. |

Use the supplied study protocol for aggregation, uncertainty, and decisions. Do not infer missing measurements or extrapolate beyond the observed study without an explicitly qualified model.

## Expected Output

**Required Files:** `bispecific_delivery_assessment.json` and `report.md`

Include:

- Candidate decision or `INDETERMINATE`, governing readout, and rationale.
- Per-candidate observations with units, source data, filters, timepoints, and replicate counts.
- Requested fold-change calculations with an explicit comparison basis.
- Dosing-interval conclusion: `SUPPORTED`, `NOT_SUPPORTED`, or `NEEDS_MORE_EVIDENCE`, with its evidence basis.
- Uncertainty, limitations, and missing follow-up evidence.

The report must compare all candidates and explain why the recommendation follows from the supplied data.

## Important Instructions

- Return `NEEDS_INPUT` when source tables or required metadata are absent; do not derive measured values from narrative text.
- Whole-brain signal does not by itself establish parenchymal delivery, target engagement, or pharmacological effect.
- Do not assume a reporter label tracks intact therapeutic antibody without supporting evidence.
- Use `INDETERMINATE` when the data do not distinguish candidates. A single-dose tissue signal does not establish a safe or effective repeat-dose interval.
