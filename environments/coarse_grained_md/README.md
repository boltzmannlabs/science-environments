# Coarse-Grained Molecular Dynamics Environment

**Status: Specification with a toy executable profile.** This environment
defines reusable contracts for multiple coarse-grained (CG) resolutions and
engines. It does not claim that all CG force fields, membranes, phase
separation systems, or parameterization workflows are qualified.

## Environment families

The task registry covers mapping/preparation, biomolecular CG MD, membranes,
liquid-liquid phase separation, polymers/soft matter, colloids, lipid
nanoparticles, atomistic-to-CG validation, force-field development, and
trajectory qualification.

## Executable profile

`scripts/run_toy_cg.py` runs a deliberately small bead-spring chain with
OpenMM using custom harmonic bonds and a repulsive nonbonded interaction. It
tests that the adapter can build, minimize, run, and validate a CG system. It
is not a protein, membrane, LLPS, or production force-field qualification.

The executable `scripts/run_agent_harness.py` invokes all 20 deterministic
specialist checks against three OpenMM CUDA smoke systems: a bead-chain
protein proxy, a membrane-patch proxy, and a polymer/LLPS proxy. Results are
stored under `results/agent_harness/`. Family-specific checks pass only when
the corresponding proxy is present; reference-dependent checks remain REVIEW.

## Evidence rules

Every real CG result must record resolution, mapping, force-field/model and
version, topology and parameter hashes, engine/platform, seed, replicas,
observables, reference conditions, and limitations. CG and atomistic results
must not be compared across incompatible thermodynamic states or observables.
