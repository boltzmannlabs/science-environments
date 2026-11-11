# FEP02 — SAMPL6 host–guest paper-protocol reconstruction

**Task family:** FEP/TI paper benchmark  
**System:** octa-acid host, OA-G3 → OA-G6  
**Reference:** SAMPL6 host–guest challenge

## Objective

Evaluate extraction of the SAMPL6 host–guest alchemical protocol and generation
of a valid complex/solvent setup. The frozen source manifest is
`../sampl6/manifest.json`.

## Required outputs

- OA-G3 and OA-G6 structures and endpoint identities.
- Transformation mapping and charge treatment.
- Reported/inferred/not-reported parameter table.
- Lambda schedule, equilibration, production and estimator configuration.
- Independent input and provenance validation.

The task returns `REVIEW` when the source manifest lacks a complete topology,
trajectory or reproducible estimator bundle. It must not substitute guessed
production parameters.
