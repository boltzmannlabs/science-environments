**Task ID:** `task_002_sars_cov2_mpro_hit_prioritisation`

**Task:** [SARS-CoV-2 Mpro hit prioritisation](../tasks/task_002_sars_cov2_mpro_hit_prioritisation.md)

## Published Results

**Source:** [El Aissouq A, Chedadi O, Bouachrine M, Ouammou A, *Identification of Novel SARS-CoV-2 Inhibitors: A Structure-Based Virtual Screening Approach*, Journal of Chemistry 2021, 1901484 (2021)](https://doi.org/10.1155/2021/1901484), Table 1, Figures 1–6; [author data set](https://github.com/ELAISS-OUQ/SARS-CoV-2-inhibitors).

| Published metric | Reported value or outcome | Scope and interpretation |
| --- | --- | --- |
| Reference controls | **Ritonavir −7.4; remdesivir −8.3 kcal/mol** | Table 1, Vina. |
| Top-20 binding scores | **−8.1 to −9.6 kcal/mol** | Table 1: 16 DrugBank, 4 literature compounds. |
| Strongest hits | **Lifirafenib, dihydroergocornine and DB11913, each −9.6 kcal/mol** | Table 1. |
| Second screen, AutoDock 4.2 | **−7.69 to −10.08 kcal/mol**; best **PF-03715455** | Table 1. |
| Final three compounds | **PF-03715455, lifirafenib and Mol181** | Selected after the AutoDock 4.2 screen. |
| H-bond residues | PF-03715455: **GLU166, CYS145, LEU141**. Lifirafenib: **ALA191, THR190, GLU166**. Mol181: **CYS145, HIS41** | Section 3.2, Figures 2–4. Catalytic dyad: CYS145, HIS41. |
| Docking settings | **PyRx 0.8 AutoDock Vina; centre (−9.63, 11.33, 70.50) Å; size (13.24, 20.25, 13.21) Å; exhaustiveness 8** | Section 2.3. |

No re-docking validation, score uncertainty or experimental affinity is reported. Deposited Vina outputs: [deposited scores](task_002_deposited_docking_scores.csv); [Table 1](task_002_published_table1.csv).

## Evaluation Criteria

| Criterion | Comparison requirement | Acceptance boundary |
| --- | --- | --- |
| Reference controls | Dock remdesivir and ritonavir in the same run as the candidates. | −8.3 and −7.4 kcal/mol; references, not thresholds. |
| Docking comparability | Match engine, receptor, box and ligand preparation, or declare each difference. | PyRx 0.8, exhaustiveness 8, 13.24 × 20.25 × 13.21 Å box; other settings are an adapted reproduction. |
| Shortlist recovery | Compare identifiers with the 20 Table 1 compounds; report the rank of each. | 18 of the 20 are in the supplied library. |
| Priority selection | Compare the three priorities with PF-03715455, lifirafenib and Mol181. | The published three follow an AutoDock 4.2 re-score and interaction analysis. |
| Interaction residues | Name the catalytic residues and contact criterion; measure them from the pose. | Catalytic dyad: **CYS145, HIS41**. |

## Agent Results

Result files: [`results/task_002_sars_cov2_mpro_hit_prioritisation/`](../results/task_002_sars_cov2_mpro_hit_prioritisation/report.md).

| Stage | Agent execution | Outcome |
| --- | --- | --- |
| Docking | Platform Vina; 397 candidates and 2 controls; exhaustiveness 16 (agent-stated) | 390/397 scored; 7 failed |
| Reference controls | Same run | Remdesivir −7.664; ritonavir −7.239 kcal/mol |
| Active-site engagement | Per-pose pocket contacts; dyad qualifier CYS145/HIS164 | All 20 poses in the N3 pocket, each within 4 Å of HIS41 or CYS145 |
| Shortlist | 20 lowest Vina scores | DB12457, DB03363, DB12318, DB14773, DB00696, DB13345, DB11878, DB000320, DB11913, DB04023, DB06455, DB02498, DB14859, DB00303, DB00673, DB00402, DB00203, DB01232, DB06590, DB12760 |
| Final priorities | Score, catalytic engagement, pocket contacts, H-bonds | DB03363, DB04023, DB00303 |

**Overlap with the paper: shortlist 5/18, priorities 0/3.**

**Scores for the paper's 20 top hits**

| Compound | Paper Vina (kcal/mol) | Agent Vina (kcal/mol) | Agent rank |
| --- | ---: | ---: | ---: |
| Lifirafenib (DB14773) | −9.6 | −8.951 | 4 |
| DB11913 | −9.6 | −8.561 | 9 |
| Dihydroergocornine (DB11273) | −9.6 | −7.665 | 75 |
| Dihydroergocristine (DB13345) | −9.5 | −8.824 | 6 |
| Relacorilant (DB14976) | −9.5 | — | not in library |
| Irinotecan (DB00762) | −9.2 | −8.219 | 26 |
| Ergotamine (DB00696) | −9.1 | −8.928 | 5 |
| Mol181 | −9.1 | −7.581 | 86 |
| Mol187 | −9.0 | −8.283 | 22 |
| Laniquidar (DB12799) | −8.9 | −8.020 | 35 |
| Dihydro-alpha-ergocryptine (DB11274) | −8.9 | −8.258 | 23 |
| Saquinavir (DB01232) | −8.9 | −8.362 | 18 |
| Fostemsavir (DB11796) | −8.8 | −7.355 | 136 |
| Imatinib (DB00619) | −8.8 | −8.159 | 29 |
| PF-03715455 (DB12138) | −8.8 | −7.599 | 85 |
| Fenebrutinib (DB14785) | −8.7 | −7.833 | 52 |
| Simeprevir (DB06290) | −8.7 | −7.830 | 53 |
| Umbralisib (DB14989) | −8.7 | — | not in library |
| Mol184 | −8.2 | −7.517 | 95 |
| Mol188 | −8.1 | −7.280 | 158 |

Agent rank is the position among the 390 scored candidates; — = not in the supplied library.

Agreement (Spearman ρ): 0.60 (n = 243, deposited scores); 0.65 (n = 18, Table 1).
