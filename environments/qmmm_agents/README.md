# QM/MM Specialist Agents

**Status: Fixture-qualified; production QM/MM execution pending.** This
environment defines seven QM/MM problem-solving agents, their task contracts,
evidence rules, and a deterministic validation profile. It does not claim a
production QM/MM calculation merely because separate QM and MM components can
run.

## Agents

`QMMM-PS01` QM-region selection, `QMMM-PS02` boundary/link atoms,
`QMMM-PS03` charge and embedding, `QMMM-PS04` QM-region SCF,
`QMMM-PS05` coupling and forces, `QMMM-PS06` region sensitivity, and
`QMMM-PS07` trajectory failure recovery.

The reusable shared recovery layer is in
[`../md_agents/recovery_agents/cross_domain`](../md_agents/recovery_agents/cross_domain/). This package keeps
the QM/MM task contract and evidence local while reusing those runtime rules.

Run the fixture validator:

```bash
python scripts/run_qmmm_validation.py
```

## Qualification boundary

The current result validates region/boundary/charge/SCF/coupling evidence
logic on frozen fixtures. A real QM/MM engine adapter, prepared topology,
validated QM region, embedding method, link-atom protocol, energy/force
references, and trajectory case are still required for production status.
