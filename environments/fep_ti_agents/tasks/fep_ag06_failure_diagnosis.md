# Task: fep_ag06_failure_diagnosis

**Task family:** Free Energy Perturbation / execution recovery
**Module:** FEP/TI
**Status:** implemented and fixture-tested (not production-qualified)

## Description

Diagnose crashes, NaN energies, constraint failures, scheduler interruptions, and failed replicas from the earliest evidence.

## Target

The frozen fixture is `tasks/inputs/fep_failure_recovery_001/failure_cases.json`.
It contains four exact window/replica cases: a recoverable constraint failure,
a NaN without a checkpoint, a scheduler interruption, and a protocol-mismatched
checkpoint. The fixture declares OpenMM 8.2.0 and a one-retry budget.

## Required execution steps

1. Hash and preserve the input manifest.
2. Parse each log and report the earliest failure step.
3. Classify the failure using log and finite-energy evidence.
4. Verify checkpoint validity and protocol compatibility.
5. Permit restart only for an explicitly safe, compatible checkpoint and an allowed failure class.
6. Record a bounded retry plan and immutable rollback point; never overwrite inputs.
7. Return FAIL when no scientifically safe restart exists.
8. Independently inspect the generated report and history files.

## Expected outputs

`failure_report.json`, `recovery_plan.json`, and `recovery_history.jsonl`, each
including the case ID, first failing step, root cause, checkpoint evidence,
allowed correction, rollback point, retry limit, and input hash.

## Acceptance and limitations

PASS means a justified recovery plan is available and preserves the original
inputs. Deliberately unsafe cases remain FAIL, so the mixed fixture batch is
REVIEW. This task does not claim that a restarted production trajectory has
been generated or that free-energy sampling is converged.
