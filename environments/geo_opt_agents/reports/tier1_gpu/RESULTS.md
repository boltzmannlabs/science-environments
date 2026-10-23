# GeoOpt-Bench Tier-1 GPU pilot

Backend: GPU4PySCF 1.7.0 with analytic gradients and SciPy BFGS. The same
frozen starting structures, B3LYP/6-31G* settings, and maximum-gradient
threshold (`< 1e-4 Ha/Bohr`) were used as the CPU pilot.

| System | Converged | Energy (Hartree) | Max gradient (Ha/Bohr) | BFGS steps | SCF evaluations | Wall time (s) |
|---|---:|---:|---:|---:|---:|---:|
| Water | yes | -76.407024051240 | 2.588e-05 | 5 | 6 | 45.87 |
| Ammonia | yes | -56.546688813963 | 5.692e-05 | 5 | 6 | 46.57 |
| Methane | yes | -40.517660948309 | 9.315e-06 | 2 | 3 | 23.53 |
| Ethane | yes | -79.829016955648 | 3.500e-05 | 9 | 10 | 97.90 |

All four systems converged (`4/4`) in approximately `213.87` seconds. The
GPU results agree with the CPU energies to the reported precision. This pilot
does not yet qualify specialist-agent decisions or establish a production GPU
speedup; GPU startup and small-system overhead made it slower than the CPU
pilot.
