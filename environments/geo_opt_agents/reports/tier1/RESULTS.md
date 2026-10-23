# GeoOpt-Bench Tier-1 live pilot

Backend: PySCF 2.12.1 B3LYP/6-31G* with analytic gradients and SciPy BFGS,
CPU execution. Convergence threshold: maximum gradient `< 1e-4`
Hartree/Bohr. These are engine results, not agent-arm comparisons.

| System | Converged | Energy (Hartree) | Max gradient (Ha/Bohr) | BFGS steps | SCF evaluations | Wall time (s) |
|---|---:|---:|---:|---:|---:|---:|
| Water | yes | -76.407024051098 | 2.587e-05 | 5 | 6 | 18.06 |
| Ammonia | yes | -56.546688813805 | 5.692e-05 | 5 | 6 | 18.41 |
| Methane | yes | -40.517660948244 | 9.315e-06 | 2 | 3 | 9.90 |
| Ethane | yes | -79.829016955544 | 3.499e-05 | 9 | 10 | 56.53 |

All four pilot systems converged (`4/4`) in a total of approximately `102.90`
seconds. Final coordinates, complete optimization histories, and software
metadata are stored in the adjacent JSON files.

This pilot does not yet establish reference accuracy, minimum verification,
failure recovery, specialist benefit, or reproducibility across repeats. Those
require frozen reference geometries and the three comparison arms described in
`../../benchmark_spec.md`.
