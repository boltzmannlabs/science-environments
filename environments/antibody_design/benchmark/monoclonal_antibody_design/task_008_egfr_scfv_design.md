# Benchmark: EGFR: Reference-Guided scFv Design

**Task ID:** `task_008_egfr_scfv_design`

**Task:** [EGFR: Reference-Guided scFv Design](../../tasks/monoclonal_antibody_design/task_008_egfr_scfv_design.md)

## Published Results

**Source:** [ProteinBase scFv catalog](https://proteinbase.com/proteins?proteinCategory=scfv); the **21 EGFR references** linked in the [reference index](PROTEINBASE_SCFV_INDEX.md). Values were retrieved from those records on 10 November 2026.

The table gives the observed minimum and maximum for each reported computational metric. Whole-structure scores and domain scores are separated. Domain ranges summarize all reported domain entries; database-match ranges summarize the reported hits in each database.

| Computational metric | Minimum | Maximum | Scope |
| --- | ---: | ---: | --- |
| Molecular weight (Da) | 25714.1494 | 25929.3209 | Sequence / general annotation |
| Isoelectric point (pH) | 4.969796944 | 7.80791111 | Sequence / general annotation |
| ESMFold pLDDT (0–100) | 82.39856752 | 83.71150302 | Whole ESMFold structure |
| ESMFold pLDDT (0–100) | 83.75149336 | 86.74728535 | Source-annotated domains |
| Original-sequence ProteinMPNN score | 1.4344 | 1.4958 | ESMFold prediction |
| Redesigned-sequence ProteinMPNN score | 0.7567 | 0.78516 | ESMFold prediction |
| ProteinMPNN sequence recovery (raw) | 0.49875 | 0.52987 | ESMFold prediction |
| TED confidence class | 2 | 2 | Source-annotated domains |
| AFDB50 Sequence identity (%) | 51.7 | 70.4 | Source-domain database matches |
| AFDB50 E-value | 3.671e-17 | 2.052e-12 | Source-domain database matches |
| AFDB50 TM-score (raw) | 0.91918 | 0.99157 | Source-domain database matches |
| AFDB50 RMSD (Å) | 0.35 | 1.19 | Source-domain database matches |
| AFDB50 Aligned residues | 97 | 115 | Source-domain database matches |
| CATH50 Sequence identity (%) | 43.3 | 61.4 | Source-domain database matches |
| CATH50 E-value | 1.298e-14 | 1.19e-12 | Source-domain database matches |
| CATH50 TM-score (raw) | 0.35471 | 0.98369 | Source-domain database matches |
| CATH50 RMSD (Å) | 0.47 | 4.93 | Source-domain database matches |
| CATH50 Aligned residues | 68 | 111 | Source-domain database matches |
| PDB100 Sequence identity (%) | 88.5 | 100 | Source-domain database matches |
| PDB100 E-value | 3.272e-21 | 5.552e-14 | Source-domain database matches |
| PDB100 TM-score (raw) | 0.29438 | 0.98262 | Source-domain database matches |
| PDB100 RMSD (Å) | 0.5 | 5.15 | Source-domain database matches |
| PDB100 Aligned residues | 61 | 103 | Source-domain database matches |

ProteinMPNN recovery and TM-score retain the raw source scales. TED confidence values are categorical classes. Database-match RMSD and TM-score describe structural-search alignments, not accuracy against an experimentally resolved antibody–antigen complex.
