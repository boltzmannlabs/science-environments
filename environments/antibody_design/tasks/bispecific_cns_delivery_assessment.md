# Task: bispecific_cns_delivery_assessment

**Competency:** Discovery-stage translational de-risking  
**Decision type:** Comparative assessment and integrated advancement gate  
**Evidence source:** Biodistribution, pharmacokinetic, tissue-fractionation, and imaging measurements  
**Assay modality:** Supplied concentration time courses and orthogonal tissue-localization assays  
**Data source:** Supplied experimental data  
**Status:** Tool-neutral task specification; no biodistribution data or numerical results are bundled here.

## Description

Compare bispecific delivery candidates that carry the same payload but differ in their target-binding shuttle arm or architecture. Decide which candidate, if any, is supported for further development on the stated tissue-delivery objective. State what the data support about tissue exposure and durability, and identify what cannot be concluded.

The task distinguishes total-organ signal from delivery to the intended tissue compartment and from biological activity at the site of action. It also distinguishes a comparative ranking from a dosing-interval commitment. A single-dose tissue time course does not, by itself, establish a safe or effective repeat-dose interval.

## Required inputs

The data package must include:

- the target and payload identity for every candidate, shuttle-target arm, construct format, species cross-reactivity, and control antibody;
- dose, route, formulation, sampling timepoints, animal characteristics, replicate counts, and randomization/blinding details;
- raw and processed organ measurements with units, individual-animal values, assay calibration, normalization method, and missing-data handling;
- label identity, conjugation chemistry, labeling yield, stability, and evidence that measured signal tracks intact antibody or payload over the study interval;
- where available, whole-tissue concentration, vascular/parenchymal fractionation, microscopy with spatial context, target engagement, pharmacodynamic readouts, and serum exposure;
- the prespecified advancement objective, minimum meaningful difference, uncertainty method, and any dosing-interval requirements.

If only summary text is present without the data table, do not derive or invent measured values. Return `NEEDS_INPUT` for the numeric comparison.

## Required analysis

1. Verify candidate identity, payload equivalence, labeling comparability, dose, route, tissue, timepoint, and units.
2. Calculate each candidate's requested readouts directly from the supplied individual-level data. Show replicate denominator, mean, and an uncertainty summary; preserve the raw observations.
3. Compare candidates at all reported timepoints and relevant organs. Include the matched control and distinguish absolute signal from candidate-to-candidate fold change.
4. Interpret whole-organ concentration alongside capillary depletion or equivalent compartment fractionation. Whole-brain signal alone cannot distinguish vascular retention from parenchymal delivery.
5. Use imaging as spatial corroboration, while reporting its sampling, quantification, and label-detection limitations. Explain what microscopy can and cannot establish relative to bulk concentration and fractionation.
6. Assess label behavior. Direct radioiodination can produce signal that does not track intact antibody after degradation; if analyte integrity or residualization is unresolved, downgrade claims about durable intact biologic in tissue.
7. Separate evidence for tissue entry, tissue retention, intact-molecule exposure, target engagement, and pharmacological effect.
8. State whether candidate variability and sample size support a stable rank order. Do not infer a clear winner from a small difference that is within observed variability.
9. State the longest dosing interval supported by the actual PK/PD evidence. If only one dose and limited timepoints are available without target engagement, pharmacodynamic durability, and repeat-dose evidence, do not commit to weekly or longer dosing.

## Decision rules

- Use the primary quantification readout specified in the supplied protocol for the required fold-change calculation; define numerator, denominator, final timepoint, units, and included replicates.
- Name the single readout that governs the advancement recommendation and explain why the other readouts are insufficient alone.
- If the intended decision is parenchymal exposure, a compartment-resolved result is more directly informative than total-brain concentration; use the supplied task protocol to determine whether it is the governing endpoint.
- Treat label instability, non-residualizing behavior, small sample size, and biological variability as distinct possible limitations. Select a limitation only when supported by the supplied data and methods.
- Do not infer human biodistribution, clinical safety, efficacy, or dose interval from a single-species single-dose study.
- If the data do not distinguish candidates, return `INDETERMINATE` and state the specific missing discriminator.

## Expected output

**Format:** `bispecific_delivery_assessment.json` plus `report.md`

The structured result must include:

- candidate decision or `INDETERMINATE`;
- the governing readout and why it addresses the intended tissue compartment;
- requested per-candidate observed values read from the supplied data, with units, filters, and replicate count;
- any required fold-change calculation with numerator/denominator and selected timepoint;
- dosing-interval conclusion (`SUPPORTED`, `NOT_SUPPORTED`, or `NEEDS_MORE_EVIDENCE`) and its evidence basis;
- key limitation, uncertainty, and missing follow-up evidence.

The report must compare all candidates, not just the selected one. Never fabricate an observed value when the source table is absent or ambiguous.

## Important instructions

- No named software is prescribed.
- Do not equate whole-organ concentration with parenchymal exposure or intact biologic concentration.
- Do not treat the reporter label as the therapeutic molecule unless the package validates that relationship.
- Do not make a repeat-dose commitment from tissue persistence alone; connect exposure to target engagement and pharmacodynamic duration.
- This task is an evidence assessment, not a wet-lab protocol or sequence-design procedure.
