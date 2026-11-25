# FEP/TI case studies

This is the canonical scientific benchmark catalogue. Each case study is a
specific paper-derived molecular problem; it is separate from the reusable
agent contracts in `src/agents/` and `src/problem_solving/`.

## Qualification levels

| Status | Meaning |
|---|---|
| `CATALOGUED` | Paper and objective identified; inputs are not yet frozen. |
| `REFERENCE_READY` | Published metrics and required inputs are collected. |
| `SETUP_VALIDATED` | Molecular inputs and configurations pass independent checks. |
| `EXECUTED` | Required simulations completed with receipts and raw outputs. |
| `SCIENTIFICALLY_VALIDATED` | Outputs independently evaluated against criteria. |
| `REPRODUCED` | Published outcome reproduced within predefined uncertainty. |

## Catalogue

The machine-readable source of truth is `catalogue.json`. Do not count a
directory as complete merely because it exists; the status must be supported
by the case evidence and tests.

Every case uses the same bundle:

```text
CASE_ID/
├── TASK.md
├── PAPER_REFERENCE.md
├── inputs/
├── reference/
├── configs/
├── execution/
├── evaluation/
└── tests/
```

Published values, reconstructed values and experimental context remain
separate. Missing information is recorded as `REVIEW`.
