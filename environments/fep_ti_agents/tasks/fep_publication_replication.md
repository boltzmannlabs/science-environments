# Task: fep_publication_replication

**Task family:** FEP/TI
**Status:** implemented setup benchmark; production free-energy qualification requires trajectories and references.

## Objective

Reconstruct one published host–guest relative free-energy protocol, beginning
with SAMPL6 OA-G3 → OA-G6, and compare a reported-configuration record with a
shortened controlled variant.

## Inputs and acceptance

Use `../../benchmark/publication_replication/manifest.json` case
`FEP-PUB-001` and the pinned SAMPL6 manifest. Validate endpoint identity,
protocol metadata, and provenance. A missing alchemical topology, trajectory,
overlap matrix, or independent uncertainty analysis must return `REVIEW`.
