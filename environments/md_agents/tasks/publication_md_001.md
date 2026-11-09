# Task: md_publication_replication

**Task family:** Molecular Dynamics
**Status:** implemented setup benchmark; outcome qualification requires paper-matched trajectories.

## Objective

Reconstruct the declared setup of a published MD study for a specific complex,
then run a bounded controlled variant. The agent must explain every parameter
difference and must not claim that a short local run reproduces a published
long-timescale observable.

## Inputs

Use the cases in `../../benchmarks/publication_replication/manifest.json`:
`MD-PUB-001` (1BRS barnase–barstar) and `MD-PUB-002` (1VII villin
headpiece). Inputs are the pinned PDB paths named by the manifest.

## Acceptance

The paper DOI, input hash, engine, force field, solvent, temperature,
pressure, electrostatics, box/ion information, and observable target must be
recorded. Missing paper settings produce `REVIEW`; they cannot be guessed.
