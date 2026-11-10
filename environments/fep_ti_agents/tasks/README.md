# Published FEP reconstruction tasks

Each task reconstructs a specific published FEP workflow. The paper and
supporting files are the source of the protocol; the agent must generate the
environment rather than read an evaluator answer key.

## Task catalogue

| Task | System | Objective | Status |
|---|---|---|---|
| [FEP-PAPER-001](fep_paper_001/TASK.md) | CDK2, edge `17 -> 1h1q` | Reconstruct a published RBFE protocol and validate setup | Implemented / REVIEW |
| [FEP-PAPER-002](fep_paper_002/TASK.md) | PTP1B, edge `23477 -> 23482` | Reconstruct a public benchmark RBFE edge | Implemented / REVIEW |
| FEP-PAPER-003 | To be selected | Reconstruct a charge-changing transformation | Planned |

## Required task bundle

Every paper task must contain a paper reference, source manifest, exact
molecular inputs, independently curated parameters, generated configurations,
execution logs, evaluation reports and tests. Keep published values separate
from newly calculated values. Record missing or ambiguous parameters instead of
silently selecting defaults.

## Configuration experiments

Run the same task with four simulation configurations: frozen paper reference,
agent reconstruction, justified alternative and deliberately perturbed setup.
Separately compare agent architectures: general agent, specialist-assisted
agent, and orchestrated specialists plus problem-solving roles and an
independent evaluator.
