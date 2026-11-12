# Task: md_publication_replication

**Task family:** Molecular Dynamics
**Status:** implemented setup benchmark; outcome qualification requires paper-matched trajectories.

## Objective

Reconstruct the declared setup of a published MD study for a specific complex,
then run a bounded controlled variant. The agent must explain every parameter
difference and must not claim that a short local run reproduces a published
long-timescale observable.

## Inputs

Use the paper packets in `../benchmark/paper_manifest.json` and protocol
targets in `../benchmark/protocol_targets.json`: `MD-PAPER-001` (1VII villin),
`MD-PAPER-002` (1BRS barnase–barstar), and `MD-PAPER-003` (DNA duplex).
Inputs are the pinned PDB paths named by the manifest.

## Acceptance

The paper DOI, input hash, engine, force field, solvent, temperature,
pressure, electrostatics, box/ion information, and observable target must be
recorded. Missing paper settings produce `REVIEW`; they cannot be guessed.

Run the three benchmark configurations (general, specialist, orchestrated) with
`python scripts/run_paper_benchmark.py`. Compare setup scores only; do not
interpret them as scientific accuracy without paper-matched trajectories and
independent uncertainty analysis.
