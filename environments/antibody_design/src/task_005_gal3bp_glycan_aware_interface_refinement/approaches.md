# Task 005 approaches and selection

Task: glycan-aware interface refinement for a Gal-3BP/LGALS3BP antibody design benchmark.

## Verified input state

- BDBV-43 paired Fab sequence: verified from PDB 7KEW, chains G (VH, 112 aa) and J (VL, 106 aa).
- LGALS3BP: full-length 585-aa sequence and domain/glycosylation annotations verified from UniProt Q08380.
- BACK domain used as the E1 proxy: residues 260-360.
- N-glycosylation sites used for context: 69, 125, 192, 362, 398, 551, 580.
- Boltz2 reference complex: generated and retained under the results package.
- Unavailable: exact paper E1 residue list, study glycan model, Mut1 sequence, mature construct, and heated-MD replicas.

## Compared workflows

| ID | Workflow | Main benefit | Main limitation | Status |
|---|---|---|---|---|
| W1 | AntiBMPNN CDR-H3 redesign, then structure/property/interface evaluation | Explicit protected framework and declared CDR edit boundary; paired-chain context | Does not sample new CDR backbone; platform approval gate blocked the submitted job | Selected; partially executed with prior local ProteinMPNN designs |
| W2 | RF-Antibody / rfdiffusion_proteinmpnn | Samples antibody backbone and sequence jointly | Higher framework/CDR drift risk; weaker control of the requested edit boundary | Considered, not run |
| W3 | AgCDR-Diff backbone sampling followed by ProteinMPNN | Samples CDR backbone while preserving framework and antigen | Two-stage workflow and local sequence-design handoff | Considered, not run |
| W4 | Epitope-conditioned epitope_abgen | Most direct E1-conditioned design | Exact E1 residue list unavailable; only coarse BACK-domain proxy possible | Blocked at paper-resolution E1 input |
| W5 | W1 plus heated MD | Closest route to published 5 Å interface-RMSD criterion | Current MDS contract is protein-ligand oriented; setup parameters unavailable | Blocked |

## Selection

W1 was selected because it best matches the task constraints: preserve the BDBV-43 paired framework, edit only declared CDR-H3 positions, and compare candidates under the same target and structural evaluation conditions. Glycan awareness was implemented as a local post-hoc accessibility/clash analysis because the exact paper E1 mapping and glycan model were unavailable.

The actual executed run is recorded in `runs/20261110_cdrh3_boltz2_glycan_prodigy/execution.md`. It used the already generated local ProteinMPNN designs because the platform AntiBMPNN partial-validation approval timed out and therefore was not an approved submission.
