# Benchmark input execution

Backend: Boltzmann Geo-Opt module using GPU4PySCF + SciPy BFGS, B3LYP/6-31G*.

| Input | Outcome | Energy (Hartree) | Max gradient (Ha/Bohr) | Runtime |
|---|---|---:|---:|---:|
| GEO-001 water | converged | -76.407023582300 | 3.581e-05 | 27.23 s |
| GEO-002 methane | converged | -40.517660948043 | 1.036e-05 | 23.02 s |
| GEO-003 ethanol | converged | -155.030874809079 | 9.579e-05 | 361.32 s |
| GEO-004 malformed XYZ | rejected before engine | — | — | 0.0001 s |
| GEO-005 distorted water | review before engine | — | — | 0.0001 s |
| GEO-005 repaired water | converged after bounded repair | -76.407023582300 Ha | 3.581e-05 Ha/Bohr | 27.76 s |

The distorted case was intentionally not sent into an unbounded optimizer:
its 3.0 Angstrom O-H distance was classified for bounded repair. The malformed
case was rejected by the XYZ parser. The three valid molecular inputs produced
finite energies and converged gradients. Per-case JSON files preserve the
evidence. The repaired GEO-005 result preserves the original review status and
records the explicit 0.960 Å O–H repair before execution.
