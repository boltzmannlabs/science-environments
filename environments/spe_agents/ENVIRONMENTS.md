# SPE Environment Index

| ID | Environment | Group | Intended adapter(s) | Status |
|---:|---|---|---|---|
| 01 | Small-Molecule SPE | Core | `boltzmann-spe-api` | unverified |
| 02 | Drug-Like Molecule SPE | Core | `boltzmann-spe-api` | unverified |
| 03 | Conformer-Energy Comparison | Core | `boltzmann-spe-api` | unverified |
| 04 | Charged Molecule and Ion SPE | Core | `boltzmann-spe-api` | unverified |
| 05 | Open-Shell and Radical SPE | Core | SPE and orbital adapters | unverified |
| 06 | DFT Method Comparison | Method | `boltzmann-spe-api` | unverified |
| 07 | Basis-Set Convergence | Method | `boltzmann-spe-api` | unverified |
| 08 | Electronic-State and Orbital Analysis | Method | SPE and orbital adapters | unverified |
| 09 | Electron-Density and Electrostatic Property | Method | SPE and property adapters | unverified |
| 10 | Dispersion and Noncovalent Interaction | Method | SPE and property adapters | unverified |
| 11 | Hydrogen-Bonded Cluster SPE | Chemistry | `boltzmann-spe-api` | unverified |
| 12 | Metal-Ligand Coordination SPE | Chemistry | SPE and orbital adapters | unverified |
| 14 | Reaction-Energy and Intermediate SPE | Chemistry | `boltzmann-spe-api` | unverified |
| 15 | QM/MM Single-Point Energy | Chemistry | `boltzmann-qmmm-api` | unverified |
| 17 | Solvation-Cluster SPE | Drug discovery | `boltzmann-spe-api` | unverified |
| 18 | Molecular Strain-Energy Analysis | Drug discovery | `boltzmann-spe-api` | unverified |
| 19 | MLIP Reference Energy | Advanced | MLIP and SPE adapters | unverified |
| 20 | SPE Quality Control and Recovery | Quality control | audit across declared adapters | unverified |

## Recommended implementation order

1. Implement and validate 01, 02, 03, 06, 07, and 20.
2. Add 08 and 09 after wavefunction and property artifacts have stable schemas.
3. Add 10, 11, 17, and 18 after fragment/reference bookkeeping is tested.
4. Add 12 after metal/ECP/spin-state support is demonstrated.
5. Add 15 only after a prepared-system QM/MM adapter and partition validation exist.
6. Add 19 after a reliable, compatible QM reference dataset and model-domain metadata exist.

## Promotion gate

An environment moves from `unverified` to `prototype` or `validated` only with recorded evidence for adapter availability and version, input translation, valid and invalid fixtures, engine failure and malformed-output behavior, every acceptance criterion, bounded retry behavior, and reproducible provenance. The environments describe workflows and validation roles; they are not 18 distinct quantum calculations. IDs 13 and 16 are retired and intentionally not reused.
