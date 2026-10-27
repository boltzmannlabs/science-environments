# Task: bispecific_cellular_mechanism_assessment

**Competency:** Cellular pharmacology and mechanism-of-action evidence  
**Decision type:** Mechanistic inference  
**Evidence source:** Assay quality-control and independent annotation analysis  
**Assay modality:** Imaging-based cell-contact or synapse classification  
**Data source:** Supplied experimental images, per-image calls, and human annotations  
**Status:** Tool-neutral task specification; no input data or result values are bundled here.

## Description

Determine whether an image-classification readout is reliable enough to support a mechanism-of-action conclusion for a bispecific antibody under the experimental conditions in the supplied task package.

The classifier may have been trained under one cellular stimulus and applied under a different stimulus or antibody condition. Assess whether the label definitions and measured class frequencies remain comparable after that change. Distinguish model-to-expert agreement from agreement against an independent, multi-rater reference standard. Treat the classifier output as an assay-derived measurement whose validity must be demonstrated for the domain in which the biological conclusion is made.

## Required inputs

The evaluation package must include:

- the classifier's training and validation conditions, label ontology, intended interpretation of each class, and the exact stimulus conditions used for the decision;
- image-level predictions and metadata for training-condition and decision-condition panels, including antibody condition, donor/batch, replicate, stimulus, and exclusion flags;
- independently produced annotations for held-out images, preserving each rater's labels, the consensus procedure, and annotation provenance;
- the panel sizes, class counts, missingness, image-selection method, and whether data are independent of training and model selection;
- the candidate bispecific's intended cellular mechanism, relevant target arms, and the specific biological claim being supported;
- the predeclared decision threshold and uncertainty method, if one exists.

Do not treat withheld or missing image files, labels, or replicate metadata as implicit evidence. If required inputs are unavailable, return `NEEDS_INPUT`.

## Required analysis

1. Compare the classifier with independent multi-rater labels on a held-out panel from the condition it was trained to interpret.
2. Quantify inter-rater agreement and uncertainty; report each class's prevalence and performance, not macro-F1 alone.
3. Evaluate the classifier against independently annotated images from each decision-condition stimulus and antibody condition. Do not score model predictions against themselves or use one reviewer's agreement with model calls as the only generalization test.
4. Test whether the same class definitions remain valid under the stimulus change. Report confusion by class, precision/recall, macro-F1, class frequency uncertainty, and any domain shift in image or biological conditions.
5. Compare class-frequency differences with biological replicate and donor variation. Do not attribute a class-frequency change to the antibody's mechanism unless the classifier and annotation process are valid for that condition.
6. State whether the evidence supports the intended mechanism-of-action claim, is insufficient because of confirmed measurement degradation, or is insufficient because the validation panel is too weak to establish generalization.

## Evaluation rules

- Independent annotations are the reference for assessing classifier generalization; model agreement with a single expert is a limited concordance check, not proof of transportability.
- Same-stimulus reliability and cross-stimulus reliability are separate questions. Performance on the training stimulus cannot establish validity under a mechanistically different stimulus.
- A strong aggregate score can hide poor performance in a rare but biologically important class. Include class-wise counts and uncertainty.
- Rater disagreements must be retained or resolved by a declared consensus rule; do not silently convert disagreement into ground truth.
- The two antibody conditions must be compared under the same image acquisition, annotation, and classifier procedures or documented differences must be modeled.
- A failed or underpowered validation makes mechanism evidence `UNRESOLVED`; it does not establish that the antibody lacks the mechanism.

## Expected output

**Format:** `mechanism_assessment.json` plus `report.md`

The report must state the validity judgment, which independent same-condition panels form the appropriate comparator, per-condition sample sizes, per-class performance, agreement among raters, uncertainty, class-frequency estimates, and the specific reason the evidence is or is not adequate for the program decision.

The structured result must contain:

- `validity_assessment`: `sufficient_confirms_generalization`, `insufficient_confirmed_mechanism_driven_degradation`, or `insufficient_underpowered_single_rater_check`;
- `same_mechanism_baseline_sources`: exactly two identifiers selected from the supplied closed list: `class_frequency_source_data_fig2ef`, `supplementary_annotation_crosscheck_dataset`, `appendix_scoring_verification_series`, `half_manual_annotation_time_reduction_experiment`, `cd19tcb_manual_check_figure`, `teplizumab_scoring_summary_entry`, `leave_one_donor_out_generalization_check`, `shap_feature_importance_comparison`;
- `cross_condition_sources`: identifiers of the actual independently annotated decision-condition panels, or an empty list when absent;
- per-condition confusion counts, class metrics, class prevalence, and uncertainty;
- `limitations`: a concise list of identified data, annotation, or validation constraints.

For the benchmark answer, return exactly:

```text
<EVAL_ANSWER>
{"validity_assessment":"<sufficient_confirms_generalization|insufficient_confirmed_mechanism_driven_degradation|insufficient_underpowered_single_rater_check>","same_mechanism_baseline_sources":["<first identifier>","<second identifier>"]}
</EVAL_ANSWER>
```

The two identifiers must be copied exactly from the closed list above and selected from evidence in the mounted package. Do not reproduce task-specific answer labels or numeric values without the supplied artifacts. All counts and metrics in the internal analysis artifact must be reproducible from the provided data and documented filtering steps.

## Important instructions

- No named software is prescribed.
- Preserve the distinction between classifier reliability, measured synapse-class frequency, and biological mechanism.
- Do not claim cross-condition generalization from agreement on training-condition images alone.
- Do not recommend advancing or rejecting a bispecific solely from an unvalidated image-class frequency.
