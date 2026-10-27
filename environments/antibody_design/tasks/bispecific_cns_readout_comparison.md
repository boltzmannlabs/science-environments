# Task: bispecific_cns_readout_comparison

## Description

Compare two bispecific IgG shuttle candidates carrying the same antibody payload. Determine which candidate, if either, is supported for the declared brain-delivery objective and identify the readout that governs the comparison.

## Target

**Candidates:** `CD98hc_shuttle` and `TfR1_shuttle`\
**Payload:** The same supplied antibody payload\
**Objective:** Declared total-brain exposure, parenchymal entry, cell-type delivery, or other specified endpoint\
**Required Data:** Primary whole-brain concentration table, capillary-depletion measurements, microscopy, and their sampling timepoints\
**Study Metadata:** Candidate identities, dose, route, species, units, individual replicates, label chemistry/stability, and analyte integrity

## Data Analysis Tool Capabilities

Use verified capabilities supplied by the execution environment in the following order. Record unavailable capabilities and leave their required evidence unresolved.

| Stage | Capability | Expected Evidence |
| --- | --- | --- |
| 1. Audit the comparison | Confirm common payload, comparable conditions, analyte identity, units, and final measurement timepoint. | Validated candidate/readout map. |
| 2. Calculate the required ratio | Extract and aggregate the primary whole-brain observations. | Both candidate values and higher/lower fold change. |
| 3. Evaluate readout relevance | Compare bulk signal, capillary depletion, and microscopy against the declared objective. | Governing readout and reasons the others are insufficient alone. |
| 4. Assess uncertainty | Review replicate variability, fraction purity, spatial sampling, and label limitations. | Decision uncertainty and unresolved evidence. |
| 5. Report the comparison | Apply the supplied decision rule to the relevant evidence. | Exact benchmark answer and supporting calculations/report. |

## Evaluation Metrics

| Criterion | Measurements and Evidence | Evaluation Rule |
| --- | --- | --- |
| Primary fold change | Higher divided by lower whole-brain value at the final reported timepoint, with source values and aggregation. | Use comparable units and a nonzero denominator; do not substitute an earlier timepoint or different readout. |
| Replication and uncertainty | Independent sample count, individual values, variability, exclusions, and uncertainty method. | The larger point estimate alone does not establish a reliable candidate advantage. |
| Readout relevance | Alignment of whole-brain signal, capillary depletion, or microscopy with the requested endpoint. | Select by objective and measurement validity; the readout used for the ratio need not govern the biological decision. |
| Compartment and label validity | Fraction purity, spatial localization, image quantification, label stability, and analyte identity. | Distinguish vascular retention, parenchymal signal, and intact-antibody exposure. |
| Recommendation support | Consistency of the selected readout, comparison conditions, and independent evidence. | Use `INDETERMINATE` when the evidence does not support a candidate choice. |

Keep all supporting statistics and limitations in the report. Preserve the three benchmark answer fields; do not fabricate a fold change when the required values are unavailable.

## Expected Output

**Required Report:** `report.md`, containing calculations, governing-readout rationale, uncertainty, and limitations.

Return the benchmark answer in this format, without additional fields:

```text
<EVAL_ANSWER>
{"construct":"<CD98hc_shuttle|TfR1_shuttle|INDETERMINATE>","governing_readout":"<whole_brain_signal|capillary_depletion|microscopy>","brain_concentration_fold_change":<computed number>}
</EVAL_ANSWER>
```

## Important Instructions

- Use only supplied data for the fold change. If a required value is missing or the ratio is undefined, report the missing requirement rather than invent a number.
- Return `INDETERMINATE` when the available evidence does not support a candidate choice; missing required inputs use `NEEDS_INPUT`.
- Keep whole-brain signal, parenchymal exposure, target engagement, and pharmacological effect distinct.
- Do not infer a dosing interval from this comparison.
