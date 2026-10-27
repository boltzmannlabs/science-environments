# Task: <agent_task_id>

## Description

Describe the QM/MM objective and the boundary, embedding, recovery, or validation decision.

## Dataset

Record coordinates, topology, QM region, link atoms, charge, multiplicity, embedding, engine versions, and reference artifacts.

## Tools to use

List the QM/MM engine adapter, topology/region validators, SCF and force checks, and independent evaluator.

## Expected Output Files

List region/topology reports, energies/forces, logs, restart artifacts, hashes, and typed PASS/REVIEW/FAIL status.

## Constraints

Preserve the QM region and coupling model, bound recovery, keep original evidence immutable, and distinguish component success from coupled validity.

## Acceptance Criteria

Define region, charge, boundary, force, convergence, reproducibility, and recovery checks. Both QM and MM finishing is not sufficient by itself.
