# Paper reference

- **Title:** Assessing the effect of forcefield parameter sets on the accuracy of relative binding free energy calculations
- **DOI:** https://doi.org/10.3389/fmolb.2022.972162
- **Code/data:** https://github.com/shansun7994/Alchaware_v5.0
- **Selected target:** CDK2, PDB 1H1Q
- **Engine:** OpenMM 7.2 with OpenMMTools Hamiltonian replica exchange
- **Ligand force field:** GAFF 2.11
- **Charge methods:** AM1-BCC and RESP (paper comparison arms)
- **Preparation:** local energy minimization for all states; ligand alignment by maximum common substructure
- **Legs:** ligand A→B in protein complex and in solvent

## Pinned transformation and source protocol

The selected public-code edge is **ligand 17 → ligand 1h1q** in the CDK2 pair
list (`TestCase/CDK2/pairs`, line 2). The direction is part of the benchmark
contract; it must not be reversed during setup. Both endpoints are reported as
neutral (`ligandNetCharge = 0`). The source repository revision is
`1ff4ea36bf354bb842b786fc6d18e482b6428edb`. The copied source inputs and their
hashes are listed in `inputs/source_cdk2/` and `inputs/transformation.json`.

The source `TestCase/CDK2/Alchaware.cfg` specifies the following protocol
values: OpenMM 7.2, OpenMMTools Hamiltonian replica exchange, AMBER ff14SB
protein XML, GAFF 2.11 ligand XML, TIP3P water, 0.15 M ionic strength,
0.9 nm box padding, five steric and five electrostatic windows, sterics
exponent 2.0, 4 fs timestep, 1,250 integration steps per exchange, 50
equilibration exchanges, 1,000 production exchanges, 1,000 extension exchanges,
and checkpoints every 100 exchanges. These are source-reported settings; the
4 fs timestep still requires stability verification for the generated system.

The endpoint structures and public source artifacts are now pinned. Complete
alchemical endpoint topologies, a generated atom map, solvent coordinates,
lambda-window trajectories, replicas, and publication-level free-energy
comparison remain unresolved until a supported parameterization/FEP engine is
available. The milestone therefore remains `REVIEW`, not production-qualified.
