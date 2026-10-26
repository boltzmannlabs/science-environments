# Geo-Opt Agents — Environment Specification

**Environment ID:** `geo-opt-agents`  
**Status:** Implemented/validated evidence package

## Objective

Prepare, execute, troubleshoot and scientifically validate molecular geometry
optimisations using 18 specialist contracts, including input validation,
connectivity, convergence, stagnation, Hessian verification, conformers,
protein–ligand checks, resource recovery and orchestration.

## Required evidence

Each run records the input structure, charge, multiplicity, method, basis,
constraints, convergence metrics, final geometry, energy/gradient evidence,
engine/version, wall time, resource use and provenance hashes. A converged
geometry is not called a minimum without Hessian/frequency evidence.

## Acceptance and benchmarking

The evaluator independently checks finite coordinates/energies/gradients,
convergence criteria, constraints, stationary-point classification and output
provenance. Fixed, general-agent and specialist-assisted arms use identical
frozen tasks and scoring rules.

## Limitations

Production protein–ligand QM/MM and broad live-engine expansion remain
case-specific follow-up work. Existing protein–ligand evidence is explicitly
identified as qualification evidence or a demo fixture in its report.
