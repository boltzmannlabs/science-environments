# Models and tools

## Engines and analysis

- OpenMM 8.2 with CUDA for bounded live execution.
- Amber14 force field for the documented real-system smoke runs.
- AmberTools GAFF2/AM1-BCC for the trypsin–benzamidine ligand.
- TIP3P water, PME, and explicit counterions where specified by the task.
- MDTraj and NumPy-based checks for trajectory and numerical validation.
- GROMACS 2024.2 CUDA build is available through the `gromacs-gpu` Conda
  environment, but has not yet been counted as a qualified production profile.

## Agent implementation

The runtime uses JSON task contracts, native adapter facades, independent
evaluators, bounded retry policies, and provenance-preserving result records.
Synthetic fixtures are diagnostic inputs only; they are never treated as
published scientific reference data.

## Reproducibility requirements

Every qualified result must record the engine/version, force field, parameters,
seed, hardware/backend, input hash, trajectory/log paths, and independent
acceptance checks.
