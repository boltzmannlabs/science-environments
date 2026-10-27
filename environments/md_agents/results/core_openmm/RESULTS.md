# Core OpenMM qualification case

## Case

`MD-CORE-001-water-box` uses the versioned `water_box.pdb` seed and request
with OpenMM 8.2, TIP3P, PME, LangevinMiddleIntegrator, 300 K, 1 fs, 250-step
minimization and 1,000 production steps. The run selected the CUDA platform.

## Observed repeats

| Repeat | Atoms | Frames | Wall time (s) | Final potential (kJ/mol) | Status |
|---:|---:|---:|---:|---:|---|
| 1 | 1482 | 10 | 10.749413 | -21389.130825 | PASS |
| 2 | 1482 | 10 | 13.001009 | -21470.591976 | PASS |

Each JSON result records input/structure/trajectory/log SHA-256 hashes, engine
version, platform, seed, energies and runtime. The two trajectories are not
expected to be byte-identical because independent stochastic trajectories were
run; reproducibility must therefore be assessed through declared observables,
not raw-file equality.

## Scope and limitations

This qualifies only the core water-box execution path, minimization,
short-timescale NVT stability and trajectory generation. It does not qualify
protein/ligand parameterization, long-timescale sampling, free energy,
enhanced sampling, learned potentials, or online resource retrieval.
