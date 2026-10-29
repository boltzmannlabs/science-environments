# MD Agents Status

**Lifecycle: In Progress — executable and partially scientifically validated.**

The environment has executable task packets, native adapters, recovery-agent
harnesses, bounded OpenMM/CUDA runs, and versioned evidence. It is not yet a
qualification of long-timescale production MD, converged free energies,
enhanced sampling, QM/MM, or learned-potential workflows.

## Current evidence

- 62 agent packets have been consumed by their declared adapters.
- 5 packets have independent `PASS` evidence: input validation,
  force-field selection, timestep validation, live OpenMM execution, and
  resource optimization.
- 57 packets remain `REVIEW`; they require domain-specific trajectory,
  sampling, recovery, reference, or provenance evidence.
- Bounded CUDA runs are recorded for villin, DNA, barnase–barstar, trypsin,
  and parameterized trypsin–benzamidine.

`Adapter PASS` means that the declared input was consumed successfully. It is
not a scientific qualification decision.

## Open qualification work

Long independent replicas, production-length trajectories, reference
observable comparisons, FEP uncertainty, recovery regression tests, and
online-resource reproduction remain required before those cases can move from
`REVIEW` to `PASS`.
