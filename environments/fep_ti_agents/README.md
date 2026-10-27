# FEP/TI Specialist Agents

**Status: Specification with fixture validation.** This environment defines
ten FEP/TI problem-solving specialists, their inputs/outputs, acceptance
criteria, and evidence rules. It does not claim a production free-energy
calculation without real windows, trajectories, overlap, convergence,
uncertainty, and reference evidence.

## Read in this order

1. [Environment specification](ENVIRONMENT_SPEC.md)
2. [Configuration and schemas](config/)
3. [Agent contracts](agents/contracts.json)
4. [Task cards](tasks/)
5. [Fixture results](results/fixture_results.json)
6. [Acceptance tests](tests/)

Shared diagnosis, retry, audit, and provenance logic is in
[`../md_agents/recovery_agents/cross_domain`](../md_agents/recovery_agents/cross_domain/).

## Agents

FEP-PS01 audits alchemical mapping; FEP-PS02 transformation feasibility;
FEP-PS03 lambda schedules; FEP-PS04 phase-space overlap; FEP-PS05 convergence;
FEP-PS06 hysteresis and cycle closure; FEP-PS07 estimators and uncertainty;
FEP-PS08 charge-changing corrections; FEP-PS09 restraints and standard state;
and FEP-PS10 final result qualification.

## Package structure

```text
fep_ti_agents/
├── README.md / ENVIRONMENT_SPEC.md / REFERENCES.md
├── agents/contracts.json
├── config/
├── tasks/
├── results/
├── scripts/
└── tests/
```
