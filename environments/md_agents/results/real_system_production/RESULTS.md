# Real-system MD execution results

## Protocol

The source structures are public RCSB PDB entries: 1YRF (villin headpiece),
1BNA (DNA duplex), 1BRS (barnase–barstar), and 3PTB (trypsin–benzamidine).
Original inputs are preserved in `inputs/real_systems/`. Derived repaired inputs
are written to `results/real_system_smoke/` using PDBFixer. OpenMM 8.2 with the
Amber14 force field and CUDA was used for bounded 100-step production smoke
runs after minimization.

| System | Atoms | Steps | Platform | Final energy (kJ/mol) | Status |
|---|---:|---:|---|---:|---|
| Villin headpiece | 762 | 100 | CUDA | -5291.23 | PASS |
| DNA duplex | 998 | 100 | CUDA | -15801.93 | PASS |
| Barnase–barstar | 11016 | 100 | CUDA | -86071.52 | PASS |
| Trypsin protein preparation | 3406 | 100 | CUDA | -17724.21 | PASS |

The trypsin–benzamidine complex was subsequently parameterized with AmberTools
GAFF2/AM1-BCC, solvated with TIP3P, neutralized with six chloride ions, and
rerun using PME. The resulting parameterized complex contains 26,245 atoms and
completed 100 CUDA steps with final energy -379738.88 kJ/mol.

## Limitations

These are bounded execution and preparation records, not production-length
sampling or FEP qualification. Longer independent replicas, trajectory
stability/statistical analysis, and free-energy reference comparisons remain
required. All warnings and repair provenance are retained in the JSON, log,
topology, coordinate, and trajectory artifacts in this directory.
