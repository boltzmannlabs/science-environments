# Task: fep_ag11_estimator_audit

## Description

Audit estimator choice, derivative signs, energy units, reduced potentials, correlations, and uncertainty calculations.

## Dataset and inputs

- Per-sample energies/derivatives, temperature, lambda direction, estimator configuration, and raw units

## Tools to use

Independent TI/BAR/MBAR arithmetic where supported, unit conversion, finite-value checks, and uncertainty recomputation.

## Expected outputs

`estimator_report.json` with recomputed values, unit/sign checks, assumptions, and discrepancies.

## Acceptance and limitations

PASS requires independently reproducible arithmetic. Agreement of two scripts is insufficient if raw sampling is inadequate.
