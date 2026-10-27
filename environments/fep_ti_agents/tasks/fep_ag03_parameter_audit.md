# Task: fep_ag03_parameter_audit

## Description

Audit atom types, charges, bonded terms, nonbonded terms, virtual sites, and engine compatibility for every endpoint and alchemical state.

## Dataset and inputs

- SAMPL6 endpoint topology/parameter manifests
- Transformation map and engine/version declaration

## Tools to use

Topology parser, force-field availability checker, charge-sum validator, and independent parameter completeness test.

## Expected outputs

`parameter_report.json` with unresolved terms, compatibility findings, source/licence metadata, and stop/retry decision.

## Acceptance and limitations

PASS requires zero unresolved required parameters and valid charge totals. A successful parser run is not evidence of scientific suitability.
