# Benchmark: TREM2: Reference-Guided scFv Design

**Task ID:** `task_009_trem2_scfv_design`

**Task:** [TREM2: Reference-Guided scFv Design](../../tasks/monoclonal_antibody_design/task_009_trem2_scfv_design.md)

## Published Results

**Source:** [ProteinBase scFv catalog](https://proteinbase.com/proteins?proteinCategory=scfv); the TREM2 reference identified below. Values were retrieved from that record on 10 November 2026.

Only one strong-labeled scFv reference is included: [golden-gecko-stone](https://proteinbase.com/proteins/golden-gecko-stone). Minimum and maximum are therefore equal for each reported metric.

| Computational metric | Minimum | Maximum | Scope |
| --- | ---: | ---: | --- |
| Molecular weight (Da) | 26183.6857 | 26183.6857 | Sequence / general annotation |
| Isoelectric point (pH) | 8.75527401 | 8.75527401 | Sequence / general annotation |
| ESMFold pLDDT (0–100) | 84.24698318 | 84.24698318 | Whole ESMFold structure |
| ESMFold pLDDT (0–100) | 85.79458785 | 85.79458785 | Source-annotated domains |
| Original-sequence ProteinMPNN score | 1.2852 | 1.2852 | ESMFold prediction |
| Redesigned-sequence ProteinMPNN score | 0.76449 | 0.76449 | ESMFold prediction |
| ProteinMPNN sequence recovery (raw) | 0.58203 | 0.58203 | ESMFold prediction |
| TED confidence class | 2 | 2 | Source-annotated domains |
| ProteinTyper novelty class | 2 | 2 | Sequence / general annotation |
| Boltz2 pLDDT (raw) | 0.9233810306 | 0.9233810306 | Boltz2_Binder_SS |
| Boltz2 pTM | 0.9327809811 | 0.9327809811 | Boltz2_Binder_SS |
| Boltz2 ipTM | 0.9009589553 | 0.9009589553 | Boltz2_Binder_SS |
| Boltz2 complex pLDDT (raw) | 0.928986609 | 0.928986609 | Boltz2_Binder_SS |
| Boltz2 interface pLDDT (raw) | 0.9373155236 | 0.9373155236 | Boltz2_Binder_SS |
| Boltz2 complex predicted distance error (PDE) | 0.3970271945 | 0.3970271945 | Boltz2_Binder_SS |
| Boltz2-derived ipSAE, chain-pair maximum | 0.862584 | 0.862584 | Boltz2_Binder_SS |
| Boltz2-derived ipSAE, chain-pair minimum | 0.759702 | 0.759702 | Boltz2_Binder_SS |
| Boltz2-derived pDockQ | 0.0183 | 0.0183 | Boltz2_Binder_SS |
| Boltz2-derived pDockQ2 | 0.0073 | 0.0073 | Boltz2_Binder_SS |
| Boltz2-derived LIS | 0.6473 | 0.6473 | Boltz2_Binder_SS |
| Interface shape-complementarity score (raw) | 48.16170348 | 48.16170348 | Boltz2_Binder_SS |
| AFDB50 Sequence identity (%) | 78.4 | 78.4 | Source-domain database matches |
| AFDB50 E-value | 1.706e-16 | 1.706e-16 | Source-domain database matches |
| AFDB50 TM-score (raw) | 0.95759 | 0.95759 | Source-domain database matches |
| AFDB50 RMSD (Å) | 0.81 | 0.81 | Source-domain database matches |
| AFDB50 Aligned residues | 115 | 115 | Source-domain database matches |

ProteinMPNN recovery, TM-score, Boltz2 pLDDT-family values and shape complementarity retain the raw source scales. TED confidence and novelty values are categorical classes. Database-match RMSD and TM-score describe structural-search alignments, not accuracy against an experimentally resolved antibody–antigen complex.
