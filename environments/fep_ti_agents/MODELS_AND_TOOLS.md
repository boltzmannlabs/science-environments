# Models and tools

This environment evaluates paper-to-FEP-environment reconstruction. Exact
versions, source revisions and hashes belong to each task manifest; the list
below describes supported roles, not a claim that every tool is available in
every run.

| Capability | Tool or evidence | Current state |
|---|---|---|
| Structure and mapping | RDKit, OpenFE/Lomap | Mapping artifact generated for FEP-PAPER-001 |
| Ligand parameterization | AmberTools antechamber/parmchk2, GAFF2/AM1-BCC | Executed for both endpoints |
| Endpoint construction | AmberTools tleap and OpenMM XML preparation | Endpoint artifacts present; readiness REVIEW |
| Lambda protocol | OpenMM/OpenMMTools protocol metadata | Frozen protocol present; windows not executed |
| Free-energy analysis | BAR/MBAR-compatible analysis layer | Required for qualification; no paper-task trajectories yet |
| Molecular dynamics | OpenMM or GROMACS adapters | Smoke/setup execution only |

Preparation and analysis scripts may validate real artifacts, hashes and
numerical data. They must not fabricate trajectories, free energies, overlap,
convergence or uncertainty. A successful process exit is execution evidence,
not scientific qualification.

## Evidence policy

Every paper task must retain the source DOI/repository/revision, exact input
paths and hashes, extracted parameters, generated configuration, raw logs,
tool/version information, evaluator output and limitations. Adapted methods
must be reported separately from exact-method reproduction.
