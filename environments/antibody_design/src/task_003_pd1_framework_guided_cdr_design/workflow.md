# Task 003 selected workflow

## Objective
Design paired monoclonal-antibody VH/VL candidates against the human PD-1
ligand-binding surface while preserving the study-provided humanized IGHV3-23/IGKV1-5
framework and IGHJ4/IGKJ1 assignments.

## Protected and editable regions

Protected framework regions are the eight sequences in `sources/framework_table1.fasta`.
Editable Chothia CDR lengths are:

- H1: exactly 7 residues
- H2: exactly 6 residues
- H3: 7–18 residues
- L1: exactly 11 residues
- L2: exactly 7 residues
- L3: 9–11 residues

Framework identity is a hard gate; no framework substitution is accepted.

## Ordered workflow

1. Verify study framework sequences from PMC12815924 Table 1.
2. Verify PD-1 construct from PDB 4ZQK chain B and derive the PD-1/PD-L1 contact epitope.
3. Build the framework-only and target PDB inputs with
   `code/stage0_prepare_framework_pd1.py`.
4. Primary generation: Boltzmann `rfdiffusion_proteinmpnn`, antibody mode,
   target-aware paired CDR backbone plus sequence generation.
5. Comparison generation: Boltzmann `epitope_abgen` PDB branch with the 28-residue
   PD-1 ligand-binding epitope, followed by backbone-to-sequence generation.
6. Apply sequence validity, framework-preservation, CDR-length, pairing, duplication,
   cysteine and developability gates.
7. Predict candidate structures with Boltzmann `Boltz2`; evaluate interface confidence
   with `ipsae-protein`.
8. Evaluate sequence properties with `Antibody_Prediction`; use raw
   `stability-binding-ddg` values only as ranking evidence.
9. Validate shortlisted candidates locally and sequentially with Boltz-2 v2.2.1,
   Prodigy and structural contact/interface calculations.
10. Compare candidates with H965 as a control and report published aggregate benchmarks
    separately from candidate-level predictions.

## Ranking rules

Hard gates precede ranking. Among eligible candidates, retain diverse VH/VL pairs and
CDR lengths. Rank using orthogonal evidence: interface confidence, epitope contact,
fold confidence, sequence novelty and developability. No computational result is
reported as measured affinity, blockade or neutralization.

## Current execution status

Stage 0 input preparation is complete. The Boltzmann upload is pending explicit approval
for partial validation; no design job has been submitted. See
`workflow/execution_status.md` and the run record under `runs/`.
