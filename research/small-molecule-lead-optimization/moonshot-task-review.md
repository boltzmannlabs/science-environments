# Moonshot task feasibility review

**Reviewed: 28 October 2026. Status: preparation evidence only.** The [task dossier](../../environments/small-molecule-lead-optimization/tasks/covid-moonshot/README.md) remains pending. This review does not select a final cohort, scientific cutoff, or evaluation split.

## Primary sources actually inspected

| Source | Observation and inspection boundary |
| --- | --- |
| [Cleaned data README](https://github.com/asapdiscovery/COVID_moonshot_data_clean) | Identifies fluorescence inhibition measurements and two noncovalent datasets. The achiral/enantiopure file reduces mixture issues but the README warns that some single enantiomers have unknown absolute stereochemistry. It documents `Quant`, `Strong`, and `Weak` assay-range qualifiers and confidence-interval columns. These descriptions support a curation review; they do not certify a homogeneous final cohort. |
| [Actual CSV](https://raw.githubusercontent.com/asapdiscovery/COVID_moonshot_data_clean/main/cdd_achiral_enantiopure_dates_2023_10_18_filt.csv) | The header and source rows were inspected through web access. Its eight columns are `suspected_SMILES`, `Canonical_PostEra_ID`, `IC50_(µM)`, two IC50 confidence-interval bounds, `Hill_slope`, `CDD_curve_class`, and `Semiquant`. Source rows include inequality-qualified IC50 values, disconnected molecular forms, and extended molecular representations. No full-file parsing, chemical validation, duplicate audit, or eligible-cohort count was performed. |
| [Cleaned repository licence](https://github.com/asapdiscovery/COVID_moonshot_data_clean/blob/main/LICENSE) | The inspected file is MIT, copyright 2023 ASAP Discovery, with notice-retention conditions. Preserve the exact notice in any permitted redistributed material and review the provenance/terms of additional assets separately; this observation is not a licence for every external structure or dataset. No source dataset is redistributed here. |
| [Original submissions repository](https://github.com/postera-ai/COVID_moonshot_submissions) | Its README distinguishes registration from suspected compound identity and describes separate fluorescence/RapidFire measurements, chemical-series metadata, and structure links. It is a possible source for missing context, not a validated join to the cleaned CSV. Do not combine its assay families or join structures using names alone. |
| [Boby et al., primary paper record](https://pubmed.ncbi.nlm.nih.gov/37943932/) | *Open science discovery of potent noncovalent SARS-CoV-2 main protease inhibitors*, Science 382, eabo7201 (2023), [DOI](https://doi.org/10.1126/science.abo7201). The bibliographic/abstract record was accessible. Full methods retrieval through the publisher/preprint/PMC endpoints did not succeed during this review; assay conditions were not independently qualified from full methods. |

The cleaned README's dated coverage statement and its filename should not be treated as row-level chronology. The actual CSV header contains neither dates nor chemical-series membership. A temporal holdout or congeneric-series task therefore requires verified additional provenance and a documented join. No exact repository commit or raw-byte hash was verified in this browser-based review; moving `main` URLs are source pointers, not frozen task inputs.

## Feasibility assessment

The accessible data are a plausible basis for a retrospective measured-library selection task. They are insufficient on their own to declare a ready benchmark or to score arbitrary new designs. A conservative first candidate for review is a compatible quantitative subset, with censored records kept separately unless an interval-aware evaluator is deliberately specified. This is a proposed curation direction, not an adopted exclusion rule.

Baseline and candidate comparisons must concern the same reviewed assay endpoint. A future tool's NESSO score, predicted IC50, or docking output can help the agent search, but cannot be subtracted from a measured source IC50 as if it were an observed lead improvement. Where unit transformations or differences are used, retain the original values and validate the transformation against the declared endpoint and qualifiers.

The cleaned file does not by itself supply all possible preservation objectives. Adding a solubility or selectivity requirement would need its own compatible evidence and evaluation definition; absence of those columns is not evidence that a candidate satisfies the requirement.

## Conditions for a defensible first task

- Freeze source bytes and licence provenance before curation; identify which statements are dataset metadata and which were independently checked.
- Specify molecular identity/form handling, duplicate groups, assay compatibility, qualifier treatment, and source-to-task mappings before running either agent.
- Choose a justified starting lead and cohort, and keep visible development information separate from final evaluation.
- Predeclare scoring and observable resource accounting. Do not imply equal internal work from equal remote submission counts.
- Verify actual evaluator access restrictions and frozen submission handling. Public sources and pretrained-model exposure remain limitations even when local label files are inaccessible.

Neither cohort selection nor metric design has been completed. No chemical structures, assay values, or evaluation answers from these public sources are copied into the tested-agent task directory by this review. The task is pending until these conditions and a reviewer-approved protocol are satisfied.
