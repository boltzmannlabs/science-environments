# Problem-Solving Agent Environment Specification

## Contract

Each agent receives immutable inputs, logs, model settings, failure evidence,
allowed actions, retry limits, and acceptance criteria. It returns diagnosis,
proposed change, verification evidence, status, provenance, and an explicit
stop reason.

## Safety rules

Original inputs and evaluator rules are immutable. Repairs must be minimal,
approved, reversible, and recorded. An agent must stop when evidence is
insufficient, a parameter would be invented, or a retry would change the
scientific question.

## Statuses

`PASS` means the fixture's diagnosis and verification gates passed. `REVIEW`
means the correct action is to withhold a scientific claim. `FAIL` means a
required safety or diagnosis gate failed.
