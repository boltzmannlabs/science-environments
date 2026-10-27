# Task: bispecific_cns_shuttle_integrated_gate

**Competency:** Discovery-stage translational de-risking  
**Decision type:** Integrated advancement gate  
**Evidence source:** Biodistribution and pharmacokinetic measurements  
**Assay modality:** Organ time-course concentrations with a tissue-associated label  
**Data source:** Real study data supplied with the task  
**Grader type:** `all_of`  
**Task variant:** tool-neutral

## Description

Compare three independently engineered bispecific CNS-shuttle candidates carrying the same declared payload. Select one candidate only if the supplied data support a comparative brain-durability advantage. Also decide whether the data support committing to the requested dosing interval.

The study package must define each shuttle's two binding specificities, molecular format, species cross-reactivity, payload equivalence, and the relevant target expression in brain endothelium and peripheral tissues. Candidate labels in the answer are `Shuttle-1`, `Shuttle-2`, and `Shuttle-3`; the control is not an eligible advancement pick.

## Required input data

The task input package must contain the individual animal measurements and metadata for each candidate and control, including:

- organ, timepoint, animal/replicate ID, measured value, units, and any exclusion flag;
- dose, route, label identity and chemistry, sample processing, quantification method, and assay calibration;
- intact-antibody or label-stability evidence across the study interval;
- target expression and species-cross-reactivity context;
- the prespecified definition of “brain durability” and decision rule for a dosing interval.

The expected brain readout is each shuttle's observed mean at the 7-day Brain timepoint in `%ID/g`. Compute it from the delivered individual-level data after applying only documented filters. Do not infer it from the study description or use another timepoint, control, or organ as a substitute.

## Required assessment

1. Verify candidate-to-arm identity, common payload, dose, route, label comparability, tissue/timepoint definitions, and replicate counts.
2. For each shuttle, select Brain records at 7 days, report the exact replicate count and calculate the arithmetic mean `%ID/g` from the delivered values. Preserve individual observations in the analysis artifact.
3. Compare the three means alongside individual-animal values and uncertainty. Do not call the largest mean a defensible winner if the study's variability or prespecified decision rule does not distinguish it.
4. Evaluate whether the label tracks intact shuttle or payload. If label catabolism or non-residualizing behavior can change signal independently of intact antibody retention, state how that limits a durability claim.
5. Assess whether the sampling window, target-mediated uptake, brain compartment, serum exposure, and pharmacodynamic evidence are sufficient for a weekly or longer interval commitment.
6. Separate a comparative advancement hypothesis from evidence for repeat-dose exposure, target engagement, pharmacodynamic persistence, safety, and clinical dosing.

## Expected response format

Return the specified JSON inside the tags below. Numeric fields must be computed from the supplied data; do not fill them from a narrative or fabricate missing observations.

```text
<EVAL_ANSWER>
{"recommendation":{"recommended_shuttle":"<Shuttle-1|Shuttle-2|Shuttle-3|INDETERMINATE>","dosing_interval_supported":"<WEEKLY|LONGER_THAN_WEEKLY|NOT_SUPPORTED>"},"limiting_factor":"<NON_RESIDUALIZING_LABEL_BIAS|SMALL_SAMPLE_SIZE_AND_BIOLOGICAL_VARIABILITY|NONE_IDENTIFIED>","brain_7d_shuttle1_pct_id_g":<observed mean>,"brain_7d_shuttle2_pct_id_g":<observed mean>,"brain_7d_shuttle3_pct_id_g":<observed mean>}
</EVAL_ANSWER>
```

`INDETERMINATE` is appropriate when the data do not distinguish the candidates. Use `NOT_SUPPORTED` when the data do not establish a dosing interval. Choose the limiting factor only when supported by the labeling method and replicate-level evidence.

## Important instructions

- No named software is prescribed.
- Report the three requested readouts even when no candidate qualifies.
- A single-dose tissue signal does not by itself establish intact-molecule brain retention or a repeat-dose interval.
- If the input table is absent, return `NEEDS_INPUT` in the run status and do not emit invented numeric fields.
