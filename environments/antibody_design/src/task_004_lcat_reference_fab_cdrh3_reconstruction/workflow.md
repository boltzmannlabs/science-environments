# Task 004 executed workflow

## Ordered pipeline

```text
5BV7 reference PDB + VH/VL
        |
        v
[1] Input preparation and numbering map
        |
        +--> W1 AgCDR-Diff backbone generation (Boltzmann)
        |       |
        |       +--> 24 generated backbone PDBs
        |       +--> AntiBMPNN sequence design
        |               |
        |               +--> 240 designed sequences
        |
        +--> W2 CDR_Generator/EvoDiff sequence generation (Boltzmann)
        |       |
        |       +--> 24 HCDR3 sequences
        |
        +--> W3 IG-Design attempt -> failed
        |
        +--> W4 Epitope AbGen attempt -> no output
        |
        +--> W5 ProteinMPNN -> Boltz2 (open-source retained baseline)
                |
                +--> 20 designed variants; top 3 structured complexes

[2] Sequence filtering: AAR, CAAR
[3] Structural filtering: CDR-H3 CA RMSD, TM-score, Boltz2 confidence
[4] Interface filtering: heavy-atom contacts <5 Å, minimum distance
[5] Developability: GRAVY, instability, aromaticity, charge, hydrophobic fraction
[6] Benchmark comparison and shortlist
[7] Package results and provenance
```

## Exact source-side code map

### Preparation

- `code/boltzmann/preparation/prepare_v3.py`: creates a 5BV7 complex with SEQRES matching modeled ATOM records.
- `code/boltzmann/preparation/prepare_agcdr.py`: prepares antibody/antigen chain subsets with matching SEQRES.
- `code/boltzmann/preparation/prepare_full_pdb.py`: prepares the full reference complex for downstream modeling.
- `code/boltzmann/preparation/prepare_match_pdb.py`: prepares a numbering/chain-matched PDB.
- `code/boltzmann/preparation/prepare_pdbs.py`: prepares PDB inputs used by the task.
- `code/boltzmann/preparation/extract_sequences.py`: extracts chain sequences from the PDB.
- `code/boltzmann/preparation/map_cdrh3.py`: maps the VH CDR-H3 sequence to PDB residue numbering.

### Sequence and structure metrics

- `code/boltzmann/analysis/compute_aar.py`: AAR for CDR_Generator output against the native VH CDR-H3.
- `code/boltzmann/analysis/compute_antibmpnn_aar.py`: AAR for AntiBMPNN-designed VH sequences.
- `code/boltzmann/analysis/compute_caar.py`: contact-residue AAR using native CDR-H3/antigen contacts.
- `code/boltzmann/analysis/compute_rmsd.py`: Kabsch-aligned CDR-H3 CA RMSD and TM-score.
- `code/boltzmann/analysis/developability.py`: lightweight sequence-level GRAVY, instability, aromaticity, charge and hydrophobicity metrics.

### Interface and epitope analysis

- `code/boltzmann/interface/interface_contacts.py`: native/generated CDR-H3 heavy-atom contact and minimum-distance analysis.
- `code/boltzmann/interface/find_epitope.py`: CA-based antigen epitope search.
- `code/boltzmann/interface/find_epitope2.py`: heavy-atom antigen epitope search.

### Open-source comparison code

- `code/open_source/aar.py`: prior ProteinMPNN sequence recovery calculation.
- `code/open_source/struct_metrics.py`: prior Boltz2 CDR-H3 structural metrics.
- `code/open_source/prepare_struct.py`: prior Boltz2 FASTA preparation.

## Evaluation definitions

- AAR: exact amino-acid matches across all 19 CDR-H3 positions.
- CAAR: exact matches across the 7 native contact positions.
- W1 RMSD/TM: Kabsch alignment of the CDR-H3 CA atoms, PDB 97–115.
- W5 RMSD: framework-aligned CDR-H3 CA RMSD from the prior ProteinMPNN/Boltz2 evaluation.
- Interface contact: heavy-atom distance below 5 Å between CDR-H3 and antigen.

## Outputs

- Candidate inventory: `results/.../candidates.csv`.
- Full paired sequences: `results/.../sequences.fasta`.
- Structures: `results/.../structures/`.
- Raw/evaluated evidence: `results/.../evidence/`.
- Benchmark table: `benchmark/.../benchmark_comparison.csv`.
