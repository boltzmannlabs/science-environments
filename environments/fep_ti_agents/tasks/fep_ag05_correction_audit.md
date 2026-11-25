# Task: fep_ag05_correction_audit

## Description

Audit charge-changing electrostatic corrections, restraints, release terms, and standard-state conventions for all legs.

## Dataset and inputs

- Complex/solvent protocols, box and ionic conditions
- Charge difference, restraint definitions, correction equations, and reference volume

## Tools to use

Charge accounting, correction calculator, unit checker, and independent recomputation.

## Expected outputs

`correction_report.json` listing every term, units, assumptions, uncertainty, and PASS/REVIEW/FAIL decision.

## Acceptance and limitations

PASS requires documented applicable corrections and consistent leg treatment. Unsupported correction assumptions require REVIEW.
