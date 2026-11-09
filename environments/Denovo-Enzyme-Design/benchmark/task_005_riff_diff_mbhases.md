
**Task ID:** `task_005_riff_diff_mbhases`

**Task:** [Morita–Baylis–Hillman catalytic-array design](../tasks/task_005_riff_diff_mbhases.md)

## Published Results

**Source:** [Braun et al., *Computational enzyme design by catalytic motif scaffolding*, Nature 649, 237–245 (2026)](https://doi.org/10.1038/s41586-025-09747-9); [Supplementary Information](https://static-content.springer.com/esm/art%3A10.1038%2Fs41586-025-09747-9/MediaObjects/41586_2025_9747_MOESM1_ESM.docx), Supplementary Figure 12 and its caption.

| Published metric | Reported value or outcome | Scope and interpretation |
| --- | --- | --- |
| AlphaFold2 confidence | Mean per-residue pLDDT distributions, with individual designs and cohort medians. | Supplementary Figure 12. Keep the BH32.14-derived and BH1.8-derived active-site cohorts separate. Exact numerical medians and individual values are not tabulated in the caption. |
| Catalytic-array recovery | Catalytic-sidechain RMSD of **AttnPacker-repacked AlphaFold2 predictions** to the corresponding catalytic array. | Supplementary Figure 12. Exact numerical reference values are unavailable from the caption. |
| Surface aggregation propensity | **SAP divided by design residue count**. | Supplementary Figure 12, individual-design distributions and medians; exact numerical values are not tabulated in the caption. |
| Structural energy | **Rosetta total energy divided by design residue count**. | Supplementary Figure 12. This native score is not a measured free energy; exact individual values and medians are unavailable from the caption. |
| Facilitating glutamate pKa | **PROPKA-predicted pKa**, provided for the **BH1.8-derived** cohort. | Supplementary Figure 12. Use the candidate residue mapped from **array B Glu A26**. Glu B6 is a different residue. No exact numerical pKa target is established by the caption. |
| Product displacement | RMSD of the modeled MBH reaction product relative to the substrate representation in the catalytic array, provided for the **BH1.8-derived** cohort. | Supplementary Figure 12. Exact numerical RMSDs are not tabulated in the caption; the task requires a chemically valid common-heavy-atom map. |

The figure reports plotted distributions rather than a single numerical benchmark for both arrays. Histogram or scatter-plot positions must not be substituted for exact observations. Direct numerical grading of an individual design requires verified underlying values; the caption alone does not establish numerical acceptance thresholds.

## Evaluation Criteria

| Criterion | Comparison requirement | Acceptance boundary |
| --- | --- | --- |
| Cohort identity | Compare array A with BH32.14-derived references and array B with BH1.8-derived references. | Keep all candidate values, medians and rankings separate by array; no pooled acceptance threshold is established. |
| Confidence and catalytic recovery | Match predictor, native confidence scale, repacking, array-specific atoms, alignment and equivalent-atom handling. | Published distributions identify the metrics but the caption supplies no exact individual or median numerical cutoff. |
| Aggregation and structural energy | Retain SAP/residue and total structural energy/residue, with matched preparation, score functions and residue counts. | Native scales remain distinct. Do not substitute a different energy or hydrophobicity score under the published metric name. |
| Facilitating glutamate pKa | Map array-B Glu A26 to each candidate and preserve carboxyl-group identity and calculation conditions. | Applicable to array B only; Glu B6 is a distinct supporting residue. No exact pKa target is established by the caption. |
| Product displacement | Use the correct product chemistry, common-heavy-atom map and declared protein alignment. | Applicable to array B only; incompatible atom mappings remain unavailable, not zero RMSD. |
| Input and design validity | Preserve catalytic arrays, substrate/state connectivity, canonical/noncanonical chemistry where applicable and refinement lineage. | A favorable score cannot compensate for an altered catalytic identity or comparison to the wrong array family. |
