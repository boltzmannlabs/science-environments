# SPE Agents — Environment Specification

**Environment ID:** `spe-agents`  
**Status:** Implemented/validated evidence package

## Objective

Evaluate specialist workflows for molecular single-point energies across
neutral, charged, open-shell, conformer, method/basis, non-covalent,
metal-ligand, QM/MM, MLIP and quality-control cases.

## Inputs and outputs

Inputs include a structure, atom ordering, charge, multiplicity, method, basis
or model, numerical settings, constraints and a declared reference protocol.
Outputs include energy and units, convergence and warnings, provenance hashes,
runtime, failure category and the specialist decision trace.

## Acceptance

An output passes only when the evaluator independently verifies finite values,
compatible settings, required convergence/evidence, correct units and complete
provenance. Unsupported or incomplete calculations must be reported rather than
silently converted into a pass.

## Benchmark arms

The frozen benchmark compares a fixed workflow, general workflow and
specialist-assisted workflow using identical cases, repeats, scoring rules and
resource limits. Pass rate is reported with wall time, token cost, failure
categories and reproducibility.

## Limitations

Backend availability and production qualification are task-specific. Absolute
energies from incompatible methods or basis sets are not interchangeable.
