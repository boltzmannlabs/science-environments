# References — Small-Molecule Virtual Screening

## Selected papers (benchmark anchors)

### molecular-design-and-generation

1. CAII task_001 — Frontiers in Chemistry (2025). "Discovery of carbonic anhydrase II inhibitors…" doi:10.3389/fchem.2025.1627793 · PMC12528100 · https://pmc.ncbi.nlm.nih.gov/articles/PMC12528100/
2. ROCK2 task_002 — Alanzi AR, PLoS ONE (2025). doi:10.1371/journal.pone.0323781 · PMC12074392 · https://pmc.ncbi.nlm.nih.gov/articles/PMC12074392/
3. KHK-C task_003 — Frontiers in Pharmacology (2025). doi:10.3389/fphar.2025.1531512 · PMC12009819 · https://pmc.ncbi.nlm.nih.gov/articles/PMC12009819/
4. FoxM1 + Hsp70 task_004 — Research in Pharmaceutical Sciences (2023). doi:10.4103/1735-5362.359431 · PMC9872178 · https://pmc.ncbi.nlm.nih.gov/articles/PMC9872178/
5. FGFR2 task_005 — Scientific Reports (2024). doi:10.1038/s41598-024-69850-1 · PMC11339395 · https://pmc.ncbi.nlm.nih.gov/articles/PMC11339395/
6. GSK-3β task_006 — Scientific Reports (2026). doi:10.1038/s41598-026-56505-6 · PMC13396737 · https://pmc.ncbi.nlm.nih.gov/articles/PMC13396737/

### structure-based-discovery

7. EGFR task_001 — PLoS ONE (2024). doi:10.1371/journal.pone.0311527 · PMC11627428 · https://pmc.ncbi.nlm.nih.gov/articles/PMC11627428/
8. TrkB agonist task_002 — Bioinformatics and Biology Insights (2023). doi:10.1177/11779322231158254 · PMC9989394 · https://pmc.ncbi.nlm.nih.gov/articles/PMC9989394/
9. MMP-9 task_003 — PLoS ONE (2026). doi:10.1371/journal.pone.0346627 · PMC13175377 · https://pmc.ncbi.nlm.nih.gov/articles/PMC13175377/ · data: Figshare doi:10.6084/m9.figshare.31425299
10. PI5P4Kγ task_004 — Scientific Reports (2025). doi:10.1038/s41598-025-07480-x · PMC12485083 · https://pmc.ncbi.nlm.nih.gov/articles/PMC12485083/
11. PI3Kα task_005 — RSC Advances (2022). doi:10.1039/D2RA03451D · PMC9346375 · https://pmc.ncbi.nlm.nih.gov/articles/PMC9346375/
12. VEGFR-2 + c-Met task_006 — Frontiers in Pharmacology (2025). doi:10.3389/fphar.2025.1534707 · PMC11926154 · https://pmc.ncbi.nlm.nih.gov/articles/PMC11926154/
13. HKII task_007 — Tanbin S, Ahmad Fuad FA, Abdul Hamid AA. BioTech 2021, 10(1), 1 (published 28 December 2020). "Virtual Screening for Potential Inhibitors of Human Hexokinase II for the Development of Anti-Dengue Therapeutics." doi:10.3390/biotech10010001 · PMC9245486 · https://pmc.ncbi.nlm.nih.gov/articles/PMC9245486/ · [source audit](hkii-task007-source-audit-2026-11-06.json). Documentation-level addition; exact platform execution remains unverified.

## Retired papers (provenance records)

- CDK1 (retired task, structure-based-discovery) — Medical Oncology (2022), PDB 6GU7, AutoDock 4.2.6. Retired for workflow complexity; supplement was verifiably complete.
- H1 antihistamine pharmacophore (retired task, molecular-design-and-generation) — Russian Journal of Bioorganic Chemistry (2022), PDB 7DFL. Retired: no SMILES/IDs for hits anywhere (supplement = 2D depictions only).

## Datasets and structures

- RCSB Protein Data Bank — structures cited per task (3IGP, 7P6N, 6W0Z/8UG3/3NC9/8OME, 3G73/4IO8, 6LVK, 3GB2, 7AEI, 1WWB, 2OVX, 7QPN, 4JPS, 2OH4/3EFK). Headers retrieved from https://files.rcsb.org
- Compound libraries: ZINC, PubChem, ChEMBL, NCI — public access
- DUD-E decoys — used for pharmacophore validation sets where the task's Reference Policy permits
- MMP-9 full data bundle (poses, VS results, scripts): https://doi.org/10.6084/m9.figshare.31425299

## Methods and tooling

- Europe PMC REST API (full-text search, `fullTextXML`, `supplementaryFiles`): https://www.ebi.ac.uk/europepmc/webservices/rest/
- NCBI E-utilities / Europe PMC `EXT_ID:… AND SRC:MED` for PMC-ID resolution
- Boltzmann platform tools (task execution): `Vina_basic_docking`, `Diffdock`, `pharmacophoreHypothesis`, `Pharmacophore_Screening`, `Similarity_Screening`, `Property_Prediction`, `MDS_openMM`, `Binding_affinity_Prediction` — registry per environment in `environments/<env>/MODELS_AND_TOOLS.md`
- Reference task-format and repository-structure exemplars: boltzmannlabs/science-environments `antibody_design` environment and CONTRIBUTING.md
