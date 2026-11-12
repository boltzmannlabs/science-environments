# Task 004 source package

Task: `task_004_lcat_reference_fab_cdrh3_reconstruction`
Target: human LCAT (PDB 5BV7 L4F/N5D) in complex with an agonistic Fab. Any inherited DENV-2 wording is a stale identity conflict documented in SOURCES.md and is not used to relabel this package.
Run record: `runs/20261111_lcat_cdrh3_multworkflow/`

This directory is the source-side record for the executed reconstruction work. It separates planning, implementation, inputs, execution status, and scientific results.

## Package layout

```text
src/task_004_lcat_reference_fab_cdrh3_reconstruction/
├── README.md
├── approaches.md
├── workflow.md
├── SOURCES.md
├── code/
│   ├── boltzmann/
│   │   ├── preparation/   # PDB/sequence preparation and CDR mapping
│   │   ├── analysis/      # AAR, CAAR, RMSD/TM, developability
│   │   └── interface/     # epitope and interface-contact analysis
│   └── open_source/       # prior ProteinMPNN/Boltz2 analysis scripts
└── runs/
    └── 20261111_lcat_cdrh3_multworkflow/
        ├── execution.md
        ├── provenance.json
        ├── inputs/
        ├── configs/
        └── logs/
```

Scientific outputs are in the canonical run directory:

```text
results/task_004_lcat_reference_fab_cdrh3_reconstruction/20261111_lcat_cdrh3_multworkflow/
```

The benchmark comparison remains in:

```text
benchmark/monoclonal_antibody_design/task_004_lcat_reference_fab_cdrh3_reconstruction/
```

The detailed results report is `results/task_004_lcat_reference_fab_cdrh3_reconstruction/20261111_lcat_cdrh3_multworkflow/report.md`.

## Reference definition

- Native CDR-H3: `AREGAAVRSFYYSYYGMDV`.
- VH sequence slice: positions 96–114, 1-based; Python slice `[95:114]`.
- Corresponding PDB mapping used in the structural work: chain C residues 97–115.
- Native contact positions used for CAAR: VH 102–108 / PDB 103–109.

## Executed workflow summary

1. Prepare the 5BV7 reference PDB and VH/VL records.
2. Run Boltzmann target-aware AgCDR-Diff backbone generation: 24 backbones.
3. Run AntiBMPNN sequence design on those backbones: 240 sequences, 10 per backbone.
4. Run Boltzmann CDR_Generator/EvoDiff baseline: 24 HCDR3 sequences.
5. Score sequence recovery with AAR and CAAR.
6. Score structure recovery with CDR-H3 CA RMSD and TM-score.
7. Score interface preservation with heavy-atom contacts and minimum distance.
8. Compute lightweight developability metrics for the EvoDiff sequences.
9. Compare with the retained open-source ProteinMPNN + Boltz2 baseline: 20 designs, 3 structured candidates.
10. Package candidates, sequences, structures, evidence, benchmark comparison, provenance and status.

## Main finding

The retained open-source ProteinMPNN + Boltz2 workflow was the strongest complete workflow for this reconstruction: AAR 0.4737, CAAR 0.5714, and best framework-aligned CDR-H3 RMSD 6.456 Å for `task004_sample9`. Among the Boltzmann-platform workflows, CDR_Generator had the best sequence AAR (0.2632), while AgCDR-Diff had the best loop-aligned RMSD (7.448 Å) but failed to preserve the antigen interface.

## Important status distinctions

- IG-Design: attempted and failed with internal `KeyError: 'aa_regions'`.
- Epitope AbGen: no output produced; pending, not treated as completed.
- Stability-Binding DDG: not run; no result is claimed.
- The W1 and W5 RMSD values use different alignment protocols and are not directly interchangeable.
- The source code copies preserve the implementation used or recovered from the task run; the exact platform submission payloads are not available as local Python files.
