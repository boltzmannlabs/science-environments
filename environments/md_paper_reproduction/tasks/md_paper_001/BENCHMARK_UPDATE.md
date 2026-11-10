# Paper-based MD benchmark update

This task is the first MD companion to the CDK2 FEP pilot. It uses the
published CDK2–CS3 study and tests paper-to-configuration reconstruction, not
the ability to claim a 100 ns reproduction from a short smoke run.

The independent Config B reconstruction extracted the reported GROMACS
protocol: 2 fs timestep, PME, 10 Å cutoff, P-LINCS, 298 K, 1 bar, 100 ps NVT,
100 ps NPT and 100 ns NPT production. It does not read Config A or the frozen
reference answer.

The configuration matrix is evaluated separately from agent architecture:

- A reference: `REVIEW` until topology and scientific trajectory evidence exist.
- B agent-generated: `REVIEW` with independent provenance.
- C supported alternative: `REVIEW` because OpenMM/HBonds/short production is
  an explicit alternative, not paper reproduction.
- D perturbed: `FAIL` because its timestep and temperature violate the paper
  protocol.

The PDB input hash is valid, but the selected PDB contains no `CS3` ligand
records. The RCSB CS3 ideal ligand structure is pinned separately, validated by
hash and parameterized with bounded AmberTools GAFF2/AM1-BCC. The BSM-00027
archive was also retrieved and the CDK2-CS3 source preparation bundle was
pinned under `inputs/paper_source/cdk2_cs3/`; `gmx check` reads its 60,120-atom
minimized coordinate file successfully. The source bundle contains 50 LIG
molecules and references an unredistributed `amber99sb-ildn.ff` directory, so
it is not silently converted into a single-ligand production system.

Current evidence is parameter extraction, configuration fault detection,
ligand parameterization and source-coordinate integrity. Topology preprocessing,
single-ligand complex assembly and production dynamics remain REVIEW; no 100 ns
paper reproduction is claimed.
