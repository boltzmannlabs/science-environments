# Workflow — run_20261109_001

Task: `task_007_huj3_gp120_fixed_framework_design`.

## Objective and inputs

Fixed-framework huJ3 CDR redesign against C1086 gp120 (PDB 7RI1).

Prepared inputs, mappings and exact request files are saved in `inputs/`; implementations are saved in `code/`.

## Performed steps

| Stage | Purpose | Tools and execution source |
| --- | --- | --- |
| S0_prep | huJ3 parent, gp120 mapping from 7RI1, Boltz-2 monomer fixed backbone | Boltz-2 (boltzmann) |
| S1_cdr1 | CDR1 positions 26-33 sequence design | AntiBMPNN (boltzmann) |
| S2_cdr3 | CDR3 positions 97, 101, 103-106 sequence design | ProteinMPNN (boltzmann) |
| S3_verify | mask preservation, lengths, unique variants | open_source |
| S4_properties | PD1/PD2/PD3 for parent and saved CDR1/CDR3 segments | peptides==0.5.0 (code/calc_properties.py) |
| S5_structure | monomer pLDDT and gp120 complex ipTM/pTM | Boltz-2 (boltzmann) |
| S6_comparison | parent-versus-candidate and paper-reference comparison | open_source |

## Configuration and results

[run.json](../../../Results/task_007_huj3_gp120_fixed_framework_design/run_20261109_001/run.json) records the run, counts and output files. [report.md](../../../Results/task_007_huj3_gp120_fixed_framework_design/run_20261109_001/report.md) presents the end-to-end workflow, descriptor tables and structure scores.

The source `logs/` folder contains the ProteinMPNN CDR3 execution logs.
