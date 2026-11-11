# FEP agent-configuration comparison

## Benchmark

`FEP01_PTP1B`: PTP1B `2QBS`, ligand `23477 → 23482`, using identical paper,
input and evaluator contracts for all configurations.

## Current evidence

| Configuration | Status | Evidence | Scientific qualification |
|---|---|---|---|
| General agent | NOT_EXECUTED | No model runtime/tool trace in package | REVIEW |
| FEP specialist | EXECUTED | Parameterization, tleap, OpenFE hybrid setup and RTX 3060 OpenCL run | REVIEW |
| Agent + subagents + evaluator | PARTIALLY_EXECUTED | Specialist tools plus independent evaluator; no auditable LLM handoffs | REVIEW |

The specialist execution completed both complex and solvent legs over 11
windows with 2 ps equilibration and 10 ps production per window. Energies were
finite, but the run has one repeat and insufficient samples for convergence,
replica agreement and uncertainty. The evaluator therefore correctly returns
`REVIEW`.

## Scoring status

The five weighted setup dimensions are defined in
`benchmark/FEP01_PTP1B/TASK.md`. Parameter comparison and input validation are
available for the specialist workflow. A general-agent score and an
orchestrated-agent score are intentionally not fabricated: they require an
actual model runtime, identical inputs, auditable tool calls and recorded
outputs.

## Completion gates

- [x] Paper and molecular inputs pinned.
- [x] Specialist configuration and endpoint preparation executed.
- [x] GPU/OpenCL simulation evidence recorded.
- [x] Independent evaluator rejects false convergence.
- [ ] General-agent runtime executed.
- [ ] Specialist-assisted LLM trace executed.
- [ ] Full orchestrated handoff trace executed.
- [ ] Independent repeats, convergence, uncertainty and publication comparison.

This report measures environment-construction capability separately from
scientific reproduction. It does not count deterministic setup scripts as
autonomous AI agents.
