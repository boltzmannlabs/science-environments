# Task: fep_ag14_false_success

## Description

Reject technically completed simulations that lack overlap, convergence, required outputs, provenance, or physical sanity.

## Dataset and inputs

- Exit status, logs, trajectories, overlap/convergence reports, hashes, and acceptance rules
- Controlled cases FEP-T04, FEP-T05, and FEP-T10

## Tools to use

Independent evidence checklist, finite-value and file-integrity checks, and frozen-rule evaluator.

## Expected outputs

`false_success_report.json` with each gate, evidence pointer, and PASS/REVIEW/FAIL decision.

## Acceptance and limitations

PASS requires every mandatory gate. A zero exit code or plausible scalar cannot override a failed scientific gate.
