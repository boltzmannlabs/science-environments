
**Task ID:** `task_007_huj3_gp120_fixed_framework_design`

**Task:** [huJ3 gp120 Fixed-Framework VHH Design](../../tasks/monoclonal_antibody_design/task_007_huj3_gp120_fixed_framework_design.md)

## Published Results

**Source:** [AntiBMPNN: Structure-Guided Graph Neural Networks for Precision Antibody Engineering, Advanced Science 12, e04278 (2025)](https://doi.org/10.1002/advs.202504278), Section 2.4 and Figure 2c, page 5 of 16; frequency-based scoring description in Experimental Section, page 13 of 16; and the authors' [released result parser](https://github.com/zeysun/AntiBMPNN/blob/7e6329ba3c317e7344c6b09add72dea2390af39a/helper_scripts/parsing_design_result.py).

The following values are reported for ten selected CDR3 clusters in Figure 2c. Each row describes the **full parent-position 94–110 segment**. Substitutions in this example are allowed at parent positions **97, 101, 103, 104, 105 and 106**. Row identifiers preserve the figure order; they are not a ranking by the three properties.

| Figure 2c row | Residue-volume descriptor, `PD1_volume` | Hydrophilicity descriptor, `PD2_hydro` | Net charge, `PD3_charge`, pH 7.4 |
| --- | ---: | ---: | ---: |
| 1 | **-0.4271** | **0.3253** | **0.9881** |
| 2 | **-0.3929** | **0.2118** | **0.9858** |
| 3 | **-0.4071** | **0.2376** | **-0.0140** |
| 4 | **-0.3429** | **0.1753** | **1.9879** |
| 5 | **-0.4129** | **0.2994** | **1.9879** |
| 6 | **-0.4918** | **0.1876** | **0.9858** |
| 7 | **-0.3229** | **0.0876** | **0.9858** |
| 8 | **-0.4618** | **0.2194** | **0.9858** |
| 9 | **-0.4759** | **0.2453** | **-0.0140** |
| 10 | **-0.4118** | **0.1829** | **1.9879** |

`PD1_volume` and `PD2_hydro` are signed physical-descriptor components on their native descriptor scales. `PD1_volume` is not a geometric molecular volume in Å³; `PD2_hydro` retains the article's hydrophilicity definition. `PD3_charge` is segment net charge in elementary-charge units under the stated pH and ionization convention. These segment results must remain separate from whole-VHH properties.

Provenance: Figure 2c, values reported to four decimal places. The authors' result parser at revision `7e6329ba3c317e7344c6b09add72dea2390af39a` uses `peptides.Peptide(segment).physical_descriptors()` for the descriptor components and `peptides.Peptide(segment).charge(pH=7.4)` for charge. Exact numerical reproduction requires matched coefficient tables, dependency version, normalization, pKa model and terminal-group defaults. The original `peptides` version is not established by the inspected article.

These are selected individual reference observations, not population means or universal acceptance thresholds. Generated candidates must not be paired with figure rows solely by output order or ranking.

Published native-parent descriptor triplets and CDR1 values for positions **26–33** have not been verified from the inspected article. They remain unavailable as published numerical anchors rather than being reported as zero or inferred from CDR3 values. Fresh parent controls must be calculated under the same conditions as new candidates.

## Evaluation Criteria

| Criterion | Comparison requirement | Acceptance boundary |
| --- | --- | --- |
| Residue-volume descriptor | Match `PD1_volume` amino-acid coefficients, normalization, aggregation rule and segment boundaries. Report CDR1 positions 26–33 and full CDR3 positions 94–110 separately. | Use the native descriptor scale and a declared design objective. Neither a higher nor a lower value is universally preferable; published rows are references, not pass thresholds. |
| Hydrophilicity descriptor | Match the `PD2_hydro` definition and calculation conditions for parent and candidates. Keep alternative hydropathy scales explicitly separate. | Compare like-for-like descriptor values; do not substitute a Kyte–Doolittle score or reverse the sign convention under the same column name. |
| Net charge | Match pH **7.4**, ionization constants, terminal-group treatment, segment boundaries and charge units. | Compare candidate-minus-parent charge under the same protocol. No universal favorable charge or acceptance cutoff is established by Figure 2c. |
| Parent comparison | Calculate fresh parent and candidate properties with identical implementations and report their differences. | Missing published parent values remain unavailable. A change is favorable only relative to the declared property objective. |
| Allowed changes and structure | Preserve the supplied **121-residue** parent outside the permitted edit masks, including protected positions **98–100**, and preserve the canonical backbone. | A favorable descriptor cannot compensate for an unauthorized substitution, length change, or violated backbone/framework constraint. |
| Published endpoint comparison | Match the exact sequence or cluster representative, segment definition, method and provenance before comparing to a Figure 2c row. Keep mask-only and full-segment calculations separate. | Output order is not an identity mapping. Unmatched definitions or unavailable sequence identities must be labelled non-comparable rather than treated as an exact reproduction. |
