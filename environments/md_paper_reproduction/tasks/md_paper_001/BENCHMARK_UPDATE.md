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
records. The input validator therefore returns `REVIEW` and identifies the
missing ligand structure/topology. This is an intentional evidence gate; no
ligand or topology is fabricated.

Current evidence is parameter extraction and configuration fault detection.
The next MD milestone is to pin the permitted CS3 structure/topology from the
paper archive, then generate an executable short setup smoke test before any
long production claim.
