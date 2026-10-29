# Models and tools

SPE tasks are designed for a supported quantum-chemistry backend such as
PySCF, with method/basis availability checked before execution. Task packets
record charge, multiplicity, geometry, method, basis, convergence thresholds,
and reference protocol.

The evaluator checks finite energies, SCF convergence, electron/spin
consistency, units, method/basis matching, and reproducibility. A plausible
energy without these checks is not a qualified result.
