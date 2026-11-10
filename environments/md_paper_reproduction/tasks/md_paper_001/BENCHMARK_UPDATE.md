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
records. The RCSB CS3 ideal ligand structure is therefore pinned separately,
validated by hash and parameterized with bounded AmberTools GAFF2/AM1-BCC.
The generated MOL2 and FRCMOD files are recorded as setup evidence. The ideal
ligand does not provide the protein-bound pose, so complex assembly remains a
separate gate.

Current evidence is parameter extraction, configuration fault detection and
ligand parameterization. The next MD milestone is to obtain the paper-consistent
CS3 binding-pose coordinates/topology, assemble the complex and run a bounded
setup smoke test before any long production claim.
