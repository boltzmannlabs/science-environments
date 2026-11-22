# Workflow — run_2_s1

Task: `task_006_vhh_ha_rsv_fixed_framework_design`.

## Objective and inputs

Fixed-framework VHH design against influenza HA with RSV site-III crop comparison.

Prepared inputs, mappings and exact request files are saved in `inputs/`; implementations are saved in `code/`.

## Performed steps

| Stage | Purpose | Tools and execution source |
| --- | --- | --- |
| S0_prep | 3EAK chain A scaffold; HA 5VLI and RSV 7LUC A250-380 crops; fixed CDR masks | open_source |
| S1_backbone | HA-targeted CDR-backbone design, 10 designs | PPIFlow (boltzmann) |
| S2_sequence | CDR sequencing, 5 per backbone (50 total) | AntiBMPNN (boltzmann) |
| S3_verify | framework 95/95 preservation, CDR lengths, uniqueness | open_source |
| S4_structure | Boltz-2 HA and RSV-crop complexes for the two shortlisted candidates | Boltz-2 (boltzmann) |
| S5_affinity | PRODIGY affinity on HA and RSV crop | PRODIGY (boltzmann) |
| S6_properties | humanness 9-mer proxy, exposure-filtered surface KD, RMSD/PAE audit | code/ scripts (open_source) |
| S7_comparison | SI = dG(RSV crop) - dG(HA); retain lead run_2_s1 | open_source |

## Configuration and results

[run.json](../../../Results/task_006_vhh_ha_rsv_fixed_framework_design/run_2_s1/run.json) records the selected candidate, counts and output files. [report.md](../../../Results/task_006_vhh_ha_rsv_fixed_framework_design/run_2_s1/report.md) presents the methods, result tables and candidate details.

The source `logs/` folder contains the structural verification record and the evidence checksum manifest.
