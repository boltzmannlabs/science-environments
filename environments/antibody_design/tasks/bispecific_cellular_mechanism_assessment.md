# Task: bispecific_cellular_mechanism_assessment

## Description

Determine whether an image-classification readout supports the proposed cellular mechanism of a bispecific antibody. Assess whether classifier labels and performance remain valid when the stimulus or antibody condition differs from the training condition.

## Target

**Assessment Subject:** The supplied bispecific candidate and its stated cellular mechanism\
**Readout:** Imaging-based cell-contact or synapse classification\
**Required Data:** Image-level predictions, class definitions, training/validation conditions, and decision-condition panels\
**Reference Evidence:** Independent held-out annotations, individual rater labels, consensus method, and annotation provenance\
**Study Metadata:** Donor/batch, biological replicates, antibody/stimulus conditions, sample selection, exclusions, and missing data

## Data Analysis Tool Capabilities

Use verified capabilities supplied by the execution environment in the following order. Record unavailable capabilities and leave their required evidence unresolved.

| Stage | Capability | Expected Evidence |
| --- | --- | --- |
| 1. Audit inputs and splits | Check image/label identifiers, conditions, donors, exclusions, and held-out status. | Matched records and leakage/missingness audit. |
| 2. Compare annotations | Retain individual rater labels and apply the declared consensus method. | Rater agreement, disagreements, and reference-label provenance. |
| 3. Evaluate classifier outputs | Calculate confusion counts and class-wise performance on each condition. | Precision, recall, F1, class support, and macro summaries. |
| 4. Assess uncertainty and condition shift | Compare performance and class prevalence while respecting biological replicates. | Condition-level estimates, uncertainty, and evidence of measurement drift. |
| 5. Interpret and report | Judge whether measurement validity supports the proposed mechanism comparison. | Supported validity category, evidence-source selections, and limitations. |

## Evaluation Metrics

| Criterion | Measurements and Evidence | Evaluation Rule |
| --- | --- | --- |
| Dataset independence | Held-out image count; donor/batch overlap; missing labels and exclusions by condition. | Avoid training/test overlap and do not count correlated images as independent biological replicates. |
| Reference-label reliability | Individual-rater agreement, class-wise disagreements, and the declared consensus procedure. | Model agreement with one reviewer is not an independent multi-rater reference standard. |
| Class-wise performance | Confusion counts, precision, recall, F1, and support for every class. | State undefined metrics explicitly; aggregate scores must not hide rare-class failure. |
| Aggregate performance | Macro-F1 alongside class prevalence and relevant per-class results. | Interpret differences against class imbalance and the biological decision, not a universal threshold. |
| Generalization | Condition-specific performance changes on independent annotations, with uncertainty. | Distinguish confirmed degradation from insufficient evidence; training-condition success is not cross-condition validity. |
| Biological comparison | Class-frequency estimates, differences, donor/replicate variation, and uncertainty. | Separate classifier error from biological variation before interpreting a mechanism effect. |

Use the supplied decision rule and uncertainty method. Keep undefined or unmeasurable metrics unresolved; do not replace them with favorable scores. Report detailed measurements in the report without changing the fixed benchmark answer fields.

## Expected Output

**Required Files:** `mechanism_assessment.json` and `report.md`

The report must include per-condition sample sizes, class metrics, rater agreement, uncertainty, cross-condition source identifiers, and the evidence supporting the validity judgment.

Return the benchmark answer in this format:

```text
<EVAL_ANSWER>
{"validity_assessment":"<sufficient_confirms_generalization|insufficient_confirmed_mechanism_driven_degradation|insufficient_underpowered_single_rater_check>","same_mechanism_baseline_sources":["<first identifier>","<second identifier>"]}
</EVAL_ANSWER>
```

Select exactly two distinct `same_mechanism_baseline_sources` from:

- `class_frequency_source_data_fig2ef`
- `supplementary_annotation_crosscheck_dataset`
- `appendix_scoring_verification_series`
- `half_manual_annotation_time_reduction_experiment`
- `cd19tcb_manual_check_figure`
- `teplizumab_scoring_summary_entry`
- `leave_one_donor_out_generalization_check`
- `shap_feature_importance_comparison`

## Important Instructions

- Return `NEEDS_INPUT` when required data or annotations are missing; do not invent a judgment or source selection.
- Agreement with one reviewer or performance on training-condition images alone does not establish cross-condition generalization.
- An aggregate score must not conceal poor performance in a biologically important class.
- Failed or underpowered validation leaves mechanism evidence unresolved; it does not prove that the antibody lacks the mechanism.
- Make every reported count and metric reproducible from supplied data and documented filters.
