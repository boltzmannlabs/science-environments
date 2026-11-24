# Task: fep_ag12_cycle_audit

## Description

Verify complex and solvent legs, endpoint identity, transformation direction, corrections, and thermodynamic-cycle closure.

## Dataset and inputs

- Leg result manifests, endpoint hashes, sign conventions, corrections, and cycle tolerance

## Tools to use

Graph/endpoint identity check, independent ΔΔG recomputation, units validator, and cycle residual calculator.

## Expected outputs

`cycle_report.json` with complete-leg table, closure residual, missing evidence, and decision.

## Acceptance and limitations

PASS requires a complete unit-consistent cycle. Missing or inconsistent legs are FAIL/REVIEW regardless of plausible numbers.
