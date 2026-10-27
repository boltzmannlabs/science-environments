# Task: fep_ag04_lambda_schedule

## Description

Construct or audit a bounded lambda schedule using pilot derivative variance, endpoint difficulty, soft-core settings, and adjacent-window overlap.

## Dataset and inputs

- Validated transformation and initial lambda schedule
- Pilot per-window energies/derivatives, compute budget, and overlap threshold

## Tools to use

Window diagnostics, schedule generator, overlap estimator, and immutable protocol diff.

## Expected outputs

`lambda_schedule_report.json` with window values, rationale for additions, unstable regions, and protocol hash.

## Acceptance and limitations

PASS requires explicit reproducible windows and bounded diagnostics. Schedule changes cannot change chemical endpoints or correction conventions.
