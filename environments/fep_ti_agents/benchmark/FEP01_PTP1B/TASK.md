# FEP01 — PTP1B paper-to-environment reconstruction

**Task family:** FEP/TI paper benchmark  
**System:** PTP1B `2QBS`, ligand `23477 → 23482`  
**Reference:** Ross et al. public protein–ligand RBFE benchmark  
**Published experimental reference:** `-1.16 kcal/mol`

## Objective

Evaluate whether three agent configurations can extract the same published
methodology, construct a valid OpenFE environment, and report missing or
ambiguous parameters without inventing them.

## Identical agent inputs

All configurations receive the same paper reference, input manifest, protein
PDB, ligand SDF files and edge definition. Evaluator-only reference values are
not exposed during reconstruction.

## Required outputs

- Structured parameter table with each value labelled `REPORTED`, `INFERRED`,
  `NOT_REPORTED` or `CONFLICTING`.
- Ligand mapping and transformation direction.
- Complex and solvent endpoint configuration.
- Lambda schedule and sampling configuration, or an explicit missing-data
  record.
- Provenance, tool calls, validation results and qualification status.

## Agent configurations

1. **General:** paper interpretation without FEP specialist assistance.
2. **Specialist:** FEP specialist workflow using mapping, parameterization,
   system preparation and OpenFE tools.
3. **Orchestrated:** literature extraction, FEP configuration and independent
   validation roles coordinated by a lead agent.

The current local evidence contains the specialist harness and independent
evaluator. The other two configurations remain `NOT_EXECUTED` until a model
runtime produces auditable tool-call traces; deterministic scripts are not
counted as autonomous-agent evidence.

## Scoring

| Metric | Weight |
|---|---:|
| Paper parameter extraction | 25 |
| Molecular system and mapping | 20 |
| FEP protocol correctness | 25 |
| Configuration/input validity | 15 |
| Provenance and missing-parameter handling | 15 |

Execution success, runtime, token usage and recovery are reported separately.
No configuration receives scientific PASS without trajectories, overlap,
convergence, uncertainty and independent evaluation.
