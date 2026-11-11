# Published FEP reconstruction tasks

The publication benchmarks follow the uniform Science-Environments layout used
by De Novo Enzyme Design. Flat benchmark cards are indexed under
`../benchmark/task_*.md`; detailed specialist and problem-solving contracts
remain in this directory. The current paper cases are FEP01 PTP1B, FEP02
SAMPL6, and FEP03 second protein–ligand RBFE.

Each task reconstructs a specific published FEP workflow. The paper and
supporting files are the source of the protocol; the agent must generate the
environment rather than read an evaluator answer key.

## Task catalogue

| Task | System | Objective | Status |
|---|---|---|---|
| [FEP-PAPER-001](fep_paper_001/TASK.md) | CDK2, edge `17 -> 1h1q` | Reconstruct a published RBFE protocol and validate setup | Implemented / REVIEW |
| [FEP-PAPER-002](fep_paper_002/TASK.md) | PTP1B, edge `23477 -> 23482` | Reconstruct a public benchmark RBFE edge | Implemented / REVIEW |
| FEP-PAPER-003 | Sun & Huggins 2022 | Reconstruct a force-field/charge-method FEP setup | Planned |

The expanded eight-task/five-paper target is tracked in
`../benchmark/PAPER_CATALOGUE.md`. Only FEP-PAPER-001 and FEP-PAPER-002 have
frozen inputs and executed setup evidence at present.

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
