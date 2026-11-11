# FEP/TI paper-reproduction catalogue

The FEP environment follows the same principle as the De Novo Enzyme Design
environment: multiple concrete task definitions are grouped by independent
research papers. A task is not counted as executed until its inputs, configs,
tests and evidence are present.

## Current catalogue target

The first catalogue contains **8 task definitions from 5 distinct papers or
benchmark studies**. Related edges from one source are retained as separate
tasks, but the publication count remains distinct.

| Task | Paper/study family | System or focus | Status |
|---|---|---|---|
| FEP-PAPER-001 | Alchaware/CDK2 study | CDK2 edge `17 -> 1h1q` | Implemented / REVIEW |
| FEP-PAPER-002 | Ross et al. 2023 public benchmark | PTP1B `2QBS`, edge `23477 -> 23482` | Implemented / REVIEW |
| FEP-PAPER-003 | SAMPL6 host–guest challenge | OA-G3 → OA-G6 setup reconstruction | Reference-ready / REVIEW |
| FEP-PAPER-004 | Ross et al. 2023 public benchmark | PTP1B edge `23477 → 23479` | Reference-ready / REVIEW |
| FEP-PAPER-005 | Sun & Huggins 2022 | Force-field and charge-method sensitivity | Reference-ready / REVIEW |
| FEP-PAPER-005 | Fu et al. 2022 BFEE2 protocol | Abl-SH3:p41 binding free-energy setup | Planned |
| FEP-PAPER-006 | Ross et al. 2023 public benchmark | A second independently selected benchmark edge | Planned |
| FEP-PAPER-007 | Published charge-changing FEP study | Charge correction and electrostatic protocol | Planned |
| FEP-PAPER-008 | Published convergence/reproducibility study | Replica and sampling reconstruction | Planned |

The catalogue deliberately does not require the full SAMPL6 collection. Each
future task must pin one system, source revision, molecular inputs, protocol,
reference values and acceptance criteria before implementation.

## Paper grouping

- Tasks 001 and 002 are separate pilot systems from separate source families.
- Tasks 003 and 004 share one Sun–Huggins paper but test different reported
  configurations or transformations.
- Task 005 is a distinct BFEE2 protocol paper.
- Task 006 uses a second edge from the public Ross benchmark.
- Tasks 007 and 008 are reserved for papers with sufficiently detailed charge
  correction or convergence methodology.

## Required task bundle

Every task follows the repository layout:

```text
tasks/fep_paper_<id>/
├── TASK.md
├── PAPER_REFERENCE.md
├── inputs/
├── reference/
├── configs/
├── execution/
├── evaluation/
├── expected_outputs/
└── tests/
```

The benchmark record belongs under `benchmark/`, and a results index belongs
under `results/`. Missing paper parameters remain explicit `REVIEW` evidence;
they are never silently replaced by defaults.
