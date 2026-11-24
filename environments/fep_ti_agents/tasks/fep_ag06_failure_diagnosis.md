# Task: fep_ag06_failure_diagnosis

## Description

Diagnose crashes, NaN energies, constraint failures, scheduler interruptions, and failed replicas from the earliest evidence.

## Dataset and inputs

- Immutable run manifest, window/replica logs, checkpoints, and engine version
- Controlled failure cases FEP-T06 and FEP-T07

## Tools to use

Log parser, checkpoint inspector, numerical finite-value checks, and bounded retry planner.

## Expected outputs

`failure_report.json` with first failing step, evidence-backed root cause, allowed correction, rollback point, and retry limit.

## Acceptance and limitations

PASS means a justified recovery preserves the original inputs. Unresolved or scientifically unsafe failures must return FAIL/REVIEW.
