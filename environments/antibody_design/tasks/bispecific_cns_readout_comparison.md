# Task: bispecific_cns_readout_comparison

**Competency:** Discovery-stage translational de-risking  
**Decision type:** Comparative assessment  
**Evidence source:** Biodistribution and imaging measurements  
**Assay modality:** Whole-brain concentration, vascular/parenchymal fractionation, and tissue imaging  
**Data source:** Real study data supplied with the task  
**Grader type:** `all_of`  
**Task variant:** tool-neutral

## Description

Compare two non-targeted bispecific IgG shuttle candidates carrying the same antibody payload. The candidates differ in the cerebrovascular transport target engaged by the shuttle arm. Determine which candidate, if either, is supported for the stated brain-delivery objective and name the readout that governs the comparison.

The supplied example task profile compares `CD98hc_shuttle` with `TfR1_shuttle`. The target and construct identifiers must be bound to the run manifest; do not infer that a specific target or candidate performed better.

## Required input data

The task package must contain:

- candidate and payload identities, shuttle target, format, dose, route, and species context;
- the primary whole-brain concentration table with method, units, timepoints, replicate values, and final reported timepoint;
- the vascular/parenchymal fractionation measurements and sampling time;
- the microscopy data, spatial labels, quantification method, and timepoints;
- label identity, chemistry, stability, and evidence for whether the signal tracks intact antibody;
- the declared program objective: total brain exposure, parenchymal entry, cell-type delivery, or another specific endpoint.

## Required assessment

1. Verify that the payloads and study conditions are comparable and that each readout measures the intended analyte and tissue compartment.
2. Compute the proof-of-work fold change from the primary whole-brain quantification at the final timepoint: higher candidate's reported value divided by lower candidate's reported value. State the input values, units, and replicate aggregation in the analysis artifact.
3. Select the governing readout that directly addresses the declared objective. Explain why the other two readouts cannot settle that objective alone.
4. Interpret bulk whole-brain concentration as total brain-associated signal; it does not by itself distinguish vascular retention from parenchymal delivery.
5. Interpret capillary depletion as a compartment estimate for vascular versus parenchymal material, subject to fraction purity and processing limits.
6. Interpret microscopy as spatial evidence, subject to sampling, image quantification, and label-detection limits; do not treat representative images alone as a quantitative tissue concentration.
7. State whether the selected readout and study design justify a candidate recommendation. If not, return `INDETERMINATE` and state the missing evidence in the sidecar analysis.

## Expected response format

The machine-readable answer is exactly the following object inside the tags. The run bundle's `report.md` must also retain the short explanation required in assessment steps 3–7; it must not add fields to this response object.

```text
<EVAL_ANSWER>
{"construct":"<CD98hc_shuttle|TfR1_shuttle|INDETERMINATE>","governing_readout":"<whole_brain_signal|capillary_depletion|microscopy>","brain_concentration_fold_change":<computed number>}
</EVAL_ANSWER>
```

If the supplied input data do not support a candidate choice or the primary timepoint value is unavailable, the run status must be `NEEDS_INPUT` or `INDETERMINATE` according to the failure contract; do not invent the fold change.

## Important instructions

- No named software is prescribed.
- Calculate the fold change from the supplied data, using the specified primary measurement and final timepoint.
- Whole-brain signal, parenchymal exposure, target engagement, and pharmacological effect are different claims.
- Do not infer a dosing interval from this comparison unless a separate PK/PD task supplies the required evidence.
