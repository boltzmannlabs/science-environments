# Benchmark: huJ3 gp120 Fixed-Framework VHH Design

**Task ID:** `task_007_huj3_gp120_fixed_framework_design`

**Task:** [huJ3 gp120 Fixed-Framework VHH Design](../../tasks/monoclonal_antibody_design/task_007_huj3_gp120_fixed_framework_design.md)

**Published reference:** [Sun et al., *AntiBMPNN: Structure-Guided Graph Neural Networks for Precision Antibody Engineering*, *Advanced Science* (2025)](https://doi.org/10.1002/advs.202504278), Figure 2c and supplementary Table S1. Published and workflow numbers are labeled by method and candidate throughout.

## Published in-silico CDR3 descriptors

Figure 2c reports the full CDR3 segment (positions 94–110). Its first row is the published top cluster `ARSKSTYLSRDSSGYDY`.

| Figure 2c row | Published PD1_volume | Published PD2_hydro | Published PD3_charge, pH 7.4 |
|---|---:|---:|---:|
| 1, top cluster | −0.4271 | +0.3253 | +0.9881 |
| 2 | −0.3929 | +0.2118 | +0.9858 |
| 3 | −0.4071 | +0.2376 | −0.0140 |
| 4 | −0.3429 | +0.1753 | +1.9879 |
| 5 | −0.4129 | +0.2994 | +1.9879 |
| 6 | −0.4918 | +0.1876 | +0.9858 |
| 7 | −0.3229 | +0.0876 | +0.9858 |
| 8 | −0.4618 | +0.2194 | +0.9858 |
| 9 | −0.4759 | +0.2453 | −0.0140 |
| 10 | −0.4118 | +0.1829 | +1.9879 |

## Workflow descriptors alongside the published reference

Our CDR1 variants were generated with AntiBMPNN and our CDR3 variants with ProteinMPNN. We used `peptides==0.5.0` for PD1_volume, PD2_hydro and charge at pH 7.4. Parent and candidate values use the same segment definition; Δ in parentheses is candidate minus our parent, computed from displayed values. PD1 and PD2 are signed physical-descriptor components, not volume in Å³ or a Kyte–Doolittle sum. PD3 is a theoretical charge for the extracted peptide segment.

| CDR1 segment (26–33) | Our PD1_volume (Δ) | Our PD2_hydro (Δ) | Our PD3_charge (Δ) |
|---|---:|---:|---:|
| Parent `GSIFNQYA` | −0.5175 | −0.2162 | −0.0072 |
| `GFTFSDYA` / `u01` | −0.5275 (−0.0100) | −0.2812 (−0.0650) | −1.0070 (−0.9998) |
| `GFTFSNYA` / `u02` | −0.4975 (+0.0200) | −0.3362 (−0.1200) | −0.0072 (+0.0000) |
| `GFTFSSYA` / `u04` | −0.7075 (−0.1900) | −0.3875 (−0.1713) | −0.0072 (+0.0000) |
| `GFTFSTYA` / `u03` | −0.5612 (−0.0437) | −0.4000 (−0.1838) | −0.0072 (+0.0000) |

For CDR3, the published top-cluster values are repeated as a fixed reference alongside each of our selected candidates.

| Full CDR3 segment (94–110) | Paper top PD1 | Our PD1 (Δ vs parent) | Paper top PD2 | Our PD2 (Δ vs parent) | Paper top PD3 | Our PD3 (Δ vs parent) |
|---|---:|---:|---:|---:|---:|---:|
| Our parent `ARSKSTYISYNSNGYDY` | −0.4271 | −0.2947 | +0.3253 | +0.2406 | +0.9881 | +0.9858 |
| Our `s021` `ARSRSTYISKTDTGYDY` | −0.4271 | −0.2900 (+0.0047) | +0.3253 | +0.3182 (+0.0776) | +0.9881 | +0.9881 (+0.0023) |
| Our `s044` `ARSKSTYISYDQSGYDY` | −0.4271 | −0.2476 (+0.0471) | +0.3253 | +0.2841 (+0.0435) | +0.9881 | −0.0140 (−0.9998) |
| Our `s056` `ARSSSTYISNYMDGYDY` | −0.4271 | −0.3088 (−0.0141) | +0.3253 | +0.1106 (−0.1300) | +0.9881 | −1.0133 (−1.9991) |
| Our `s059` `ARSYSTYISKEDSGYDY` | −0.4271 | −0.2594 (+0.0353) | +0.3253 | +0.2953 (+0.0547) | +0.9881 | −1.0133 (−1.9991) |

## Structural model scores

The paper reports AF3 `ranking_score`; our run reports Boltz-2 `ipTM` and `pTM`. The CDR1 and CDR3 leads in the two columns are different sequences.

| Case | Paper: AF3 candidate | AF3 pLDDT | AF3 `ranking_score` | Our Boltz-2 candidate | Boltz-2 pLDDT | Boltz-2 `ipTM` | Boltz-2 `pTM` |
|---|---|---:|---:|---|---:|---:|---:|
| Parent | huJ3 | 91.75 | 0.9187 | huJ3 | 94.38 |  |  |
| CDR1 | 1-V1 | 92.41 | 0.9216 | `cdr1_u03` (`GFTFSTYA`) | 96.80 | 0.9564 | 0.9407 |
| CDR3 | 3-V1 | 90.87 | 0.9257 | `cdr3_s044` (`ARSKSTYISYDQSGYDY`) | 93.69 | 0.9569 | 0.9373 |

Additional paper AF3 references:

| Published candidate | AF3 pLDDT | AF3 `ranking_score` |
|---|---:|---:|
| S105P | 91.45 | 0.9179 |
| N106S | 92.03 | 0.9140 |
| Y103R | 91.50 | 0.9029 |
| 3-V10 | 91.44 | 0.2608 |

Other candidates assessed with Boltz-2 in our run:

| Our candidate | Boltz-2 mean pLDDT | Boltz-2 `ipTM` | Boltz-2 `pTM` |
|---|---:|---:|---:|
| `cdr1_u01` | 96.55 | 0.9559 | 0.9405 |
| `cdr1_u02` | 96.26 | 0.9480 | 0.9288 |
| `cdr1_u04` | 96.52 | 0.9549 | 0.9409 |
| `cdr3_s021` | 94.92 | 0.5398 | 0.8340 |
| `cdr3_s056` | 94.27 | 0.9502 | 0.9422 |
| `cdr3_s059` | 93.60 | 0.9442 | 0.9304 |

## Evaluation Criteria

| Criterion | Comparison requirement | Acceptance boundary |
|---|---|---|
| Fixed-framework validity | Preserve the 121-residue huJ3 parent outside CDR1 positions 26–33 or CDR3 positions 97, 101 and 103–106, including protected positions 98–100. | An out-of-mask sequence change or changed frozen backbone fails the task's design constraint. |
| Three physicochemical properties | Compare parent and candidate using the same PD1/PD2/PD3 implementation and region (CDR1 or full CDR3), with charge at pH 7.4. | Retain native descriptor scales and candidate-minus-parent differences. No favorable cutoff is specified for PD1, PD2 or PD3. |
| Published PD comparison | Match segment length, sequence identity and calculation conventions before assigning a Figure 2c value to a candidate. | The published top cluster and our variants are different sequences; juxtaposition alone is not matched replication. |
| Structure metrics | Preserve candidate identity, predictor and score definition for each structural result. | AF3 `ranking_score` is not a Boltz-2 `ipTM` or `pTM`; no numerical substitution between those endpoints. |
| Selection | Distinguish the original structural shortlist from later property recalculation. | The newly calculated PD values did not determine the earlier shortlist. |
