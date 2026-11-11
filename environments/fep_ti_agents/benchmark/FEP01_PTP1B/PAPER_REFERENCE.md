# FEP01 paper reference

- **Study:** Ross et al., *The maximal and current accuracy of rigorous
  protein–ligand binding free energy calculations*.
- **System:** PTP1B, PDB `2QBS`.
- **Transformation:** ligand `23477 → 23482`.
- **Reference experimental ΔΔG:** `-1.16 kcal/mol`.
- **Local source record:** `case_studies/PTP1B_RBFE_001/` and
  `tasks/fep_paper_002/PAPER_REFERENCE.md`.

The publication/source benchmark does not provide a complete open trajectory
bundle for this edge. Missing lambda schedules, replica lengths and production
trajectories must therefore remain explicit rather than being filled with
defaults.
