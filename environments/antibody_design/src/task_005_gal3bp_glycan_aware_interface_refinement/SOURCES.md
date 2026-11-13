# Task 005 sources and tool provenance

## Primary scientific sources

1. **RCSB PDB 7KEW**
   - Used for BDBV-43 Fab chain identities and paired VH/VL sequences.
   - Local retained copy: `runs/20261110_cdrh3_boltz2_glycan_prodigy/inputs/reference/7KEW.pdb`.
   - Relevant chains: G = VH; J = VL.
2. **UniProt Q08380, LGALS3BP**
   - Used for the 585-aa target sequence, BACK domain location and N-glycosylation annotations.
   - The prepared target sequence is retained as chain C in the prepared task FASTA files.
3. **Costa et al., Gal-3BP glycan-aware interface study**
   - DOI recorded in the task report: `10.1016/j.compbiomed.2026.111550`.
   - Used only for published benchmark anchors and task context.
   - Full paper inputs needed for exact reproduction were not available during execution; the repository/download endpoint timed out. Published values are therefore kept separate from local matched-condition measurements.

## Computational tools and local code

| Tool/code | Use in this task | Evidence/status |
|---|---|---|
| ProteinMPNN | CDR-H3-only candidate generation with fixed framework/VL | 20 designs, 17 unique; outputs retained in results evidence |
| Boltz2 | Reference and candidate antibody-LGALS3BP complex prediction | Four model-0 complexes and confidence files retained |
| Prodigy | Open-source PPI affinity/contact cross-check | Four structures evaluated; results in `evidence/prodigy_validation.json` |
| `03_design_cdrh3.py` | Fixed-position setup and ProteinMPNN invocation | Source copy in `code/` |
| `04_prepare_struct.py` | Select top unique designs and write Boltz2 FASTAs | Source copy in `code/` |
| `05_interface_metrics.py` | Parse Boltz2 confidence and compute matched interface metrics | Source copy in `code/` |
| `06_glycan_aware.py` | Approximate BACK-domain SASA change and glycan-antibody clashes | Source copy in `code/` |
| `07_prodigy_validate.py` | Run Prodigy and parse dG/Kd/contact output | Source copy in `code/` |
| `08_consolidate.py` | Build final CSV/JSON deliverables and ranking | Source copy in `code/` |

## Boltzmann workflow catalog references

The workflow design considered AntiBMPNN, RF-Antibody/rfdiffusion_proteinmpnn, agcdr_diff, epitope_abgen, Boltz2, Antibody_Prediction, stability-binding-ddg, Prodigy, MDS_openMM, Mol_Probity and tm_align. The task package records which were selected, executed, blocked or only considered; catalog availability is not treated as execution evidence.
