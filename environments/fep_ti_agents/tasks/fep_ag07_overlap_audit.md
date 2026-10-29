# Task: fep_ag07_overlap_audit

## Description

Quantify phase-space overlap between neighboring lambda windows and identify windows that cannot support a reliable estimator.

## Dataset and inputs

- Per-window reduced energies or derivatives, trajectories, replica IDs, and overlap threshold

## Tools to use

Overlap matrix estimator, effective-sample-size calculation, and independent numerical sanity checks.

## Expected outputs

`overlap_report.json` with pairwise overlap, weakest windows, uncertainty, and targeted sampling recommendations.

## Acceptance and limitations

PASS requires all required adjacent pairs above the frozen criterion. Missing overlap evidence is REVIEW, never an implicit PASS.
