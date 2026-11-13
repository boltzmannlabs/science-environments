# Task 005 executed workflow

## Objective

Refine a BDBV-43-derived antibody interface against human Gal-3BP/LGALS3BP while preserving the paired antibody framework and assessing accessibility near the glycan-free E1 region.

## Stage graph

1. Input and source verification.
   - PDB 7KEW chains G/J supplied BDBV-43 VH/VL.
   - UniProt Q08380 supplied full-length LGALS3BP and the BACK-domain/glycosylation context.
   - The study-specific E1 mapping, mature construct, glycan model and Mut1 sequence were unavailable.
2. Reference preparation.
   - Prepare the BDBV-43 Fab with antigen chain C for sequence-based complex prediction.
   - Preserve the paired VH/VL arrangement.
3. Candidate generation.
   - Design only VH CDR-H3; keep VH framework, VH CDR-H1/H2 and the entire VL fixed.
   - Local ProteinMPNN generated 20 designs, 17 unique CDR-H3 sequences.
   - Three top unique designs were carried forward: cand11, cand7 and cand17.
4. Sequence-level filtering.
   - Remove duplicate CDR-H3 sequences and retain the parent/reference control.
   - Check that the framework and VL are unchanged in the prepared FASTAs.
5. Structure prediction.
   - Predict complexes for the reference and three candidates with full-length LGALS3BP.
   - Retain model-0 PDBs and confidence JSON files.
6. Interface scoring.
   - Interface residue pair: antibody/antigen Cα distance < 8.0 Å.
   - vdW atom pair: heavy-atom distance < 4.5 Å.
   - H-bond proxy: N/O heavy-atom pair < 3.5 Å; no explicit hydrogens in the PDBs.
   - Record ipTM, pLDDT, pDE, interface extent, antigen-residue count and contact counts.
7. Glycan-aware accessibility.
   - Approximate E1 as the BACK-domain solvent surface, residues 260-360.
   - Add a simplified 12-sugar representative glycan at Asn362.
   - Compare BACK-domain SASA with and without the glycan and count glycan-antibody clashes.
8. Independent open-source validation.
   - Run Prodigy on chains A/B (antibody) versus C (LGALS3BP) for the reference and candidates.
9. Consolidation and ranking.
   - Produce candidates.csv, metrics.json, benchmark_comparison.csv and supporting JSON files.
   - Rank cand17 first by combined Prodigy/interface evidence, cand11 second by Boltz2 ipTM/interface extent, and cand7 third as a lower-confidence comparison.

## Planned but not completed

- Platform AntiBMPNN submission: approval prompt timed out; no platform job was submitted.
- Antibody_Prediction developability/thermal-stability stage: not executed.
- Heated-MD interface stability: not executed; current MDS contract did not cleanly support this antibody-antigen use case.
- Like-for-like published benchmark reproduction: not possible without the study-specific inputs.

Experimental validation remains the ground truth.
