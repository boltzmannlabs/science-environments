# Task: cg_publication_replication

**Task family:** Coarse-grained molecular dynamics
**Status:** implemented model/setup benchmark; scientific outcome qualification requires a paper-specific system.

## Objective

Check whether the agent can identify the published Martini 3 model and keep a
controlled alternative model/configuration separate from it. Do not infer a
paper result from a generic CG toy system.

## Inputs and acceptance

Use case `CG-PUB-001` in `../../benchmarks/publication_replication/manifest.json`
and `config/environment.yaml`. The run must record model identity, input hash,
observable target, and the missing paper-specific reference system. Without
that reference, the result is `REVIEW`, not `PASS`.
