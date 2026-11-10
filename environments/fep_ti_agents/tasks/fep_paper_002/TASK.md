# Task: fep_paper_002

**Task family:** Free Energy Perturbation
**Module:** FEP/TI
**Status:** implemented / review

## Description

Reconstruct the setup for one published PTP1B relative-binding-free-energy
benchmark edge. The agent must identify the exact ligands, validate the source
structures and edge direction, generate a traceable configuration, and report
which production settings are explicitly available versus unresolved.

## Required inputs

- `inputs/ptp1b_2QBS_protein.pdb`
- `inputs/ligand_23477.sdf`
- `inputs/ligand_23482.sdf`
- `inputs/ptp1b_edges.csv`
- `PAPER_REFERENCE.md`

## Required execution

1. Verify source revision, file hashes and PDB identity.
2. Locate the selected edge and confirm the reported ΔΔG and direction.
3. Validate ligand elements, atom counts, bond graphs and stereochemistry.
4. Generate an atom-mapping candidate without reading evaluator outputs.
5. Record the selected force field, water model, lambda protocol and sampling
   values only when supported by the source.
6. Mark unavailable proprietary or trajectory requirements as REVIEW.
7. Independently evaluate input and provenance evidence.

## Expected outputs

- `evaluation/input_validation.json`
- `evaluation/edge_validation.json`
- `execution/generated_config.json`
- `expected_outputs/qualification.json`

## Acceptance

- Correctly identifies PTP1B/2QBS and edge `23477 -> 23482`.
- Confirms published edge value `-1.16 kcal/mol`.
- Validates both ligand files and protein hash.
- Does not claim a production FEP result without trajectories and estimator
  evidence.
