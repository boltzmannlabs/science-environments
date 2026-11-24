# Paper reference

- **Title:** The maximal and current accuracy of rigorous protein-ligand binding free energy calculations
- **DOI:** https://doi.org/10.1038/s42004-023-01019-9
- **Public source:** https://github.com/schrodinger/public_binding_free_energy_benchmark
- **Pinned source revision:** `a65d86b782a678c75388566ce00446e45283ee63`
- **Benchmark subset:** `jacs_set`
- **Protein:** PTP1B, reference PDB `2QBS`
- **Selected edge:** ligand `23477 -> 23482`
- **Published experimental ΔΔG:** `-1.16 kcal/mol` (edge CSV; direction 23477 to 23482)
- **Reference inputs:** PTP1B protein PDB, ligand SDF collection, perturbation-edge CSV

The publication and repository provide benchmark structures and experimental
relative affinities. They do not provide an open, edge-specific production
trajectory bundle that can be treated as a reproduced FEP result here. Exact
FEP+ settings, proprietary execution details and trajectories are therefore
recorded as unavailable rather than invented.
