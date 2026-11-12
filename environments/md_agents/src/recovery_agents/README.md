# MD Recovery and Problem-Solving Agents

**Status: Executable recovery-fixture qualification.** This package provides
10 deterministic troubleshooting agents reusable by atomistic and CG MD
workflows. They preserve original evidence, propose bounded changes, and
return REVIEW when a repair cannot be justified.

`REC-01` crash diagnosis, `REC-02` energy/NaN recovery, `REC-03` parameter
repair, `REC-04` molecular/CG structure repair, `REC-05` equilibration
recovery, `REC-06` checkpoint/restart recovery, `REC-07` sampling/convergence,
`REC-08` GPU/CPU/resource recovery, `REC-09` CG model failure diagnosis, and
`REC-10` false-success scientific validation.

The harness runs frozen synthetic failure fixtures and tests diagnosis,
bounded repair proposals, and independent verification. It does not claim
that a fixture pass qualifies a production GROMACS, OpenMM, AMBER, LAMMPS, or
CG workflow.
