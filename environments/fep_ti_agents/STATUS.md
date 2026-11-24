# Status

**Maturity: In progress — paper-benchmark workflow implemented; scientific FEP qualification remains REVIEW.**

This environment retains 15 specialist contracts (`FEP-AG01`–`FEP-AG15`) and
10 problem-solving contracts (`FEP-PS01`–`FEP-PS10`). The contracts are not
automatically counted as autonomous AI agents. Operational status is tracked by
`results/operational_role_audit.json` and requires an executable tool plus
task-specific evidence.

## Current paper benchmark

`FEP-PAPER-001` is the CDK2 `17 -> 1h1q` transformation from the pinned
Sun–Huggins/Alchaware source. It includes source structures, endpoint
parameterization, complex and solvent endpoint artifacts, OpenFE/Lomap mapping,
paper protocol extraction, configuration A/B/C/D comparisons and provenance.

Current role audit:

- 2 operational paper-task roles;
- 6 partially connected roles;
- 7 specification-only specialist roles;
- 10 problem-solving roles validated on fixtures only.

The paper setup reconstruction achieved 20/20 on the evaluated configuration
fields. The benchmark remains `REVIEW` because production lambda trajectories,
overlap, convergence, uncertainty and independent free-energy comparison are
not present.

`FEP-PAPER-002` adds the PTP1B `23477 -> 23482` edge from the pinned 2023
public benchmark. Protein/ligand identity and the published `-1.16 kcal/mol`
edge value validate successfully. Both ligand endpoints now have recorded
GAFF2/AM1-BCC MOL2 and `frcmod` artifacts with immutable-input provenance.
The PTP1B task now also records the preparation-tool trace, paper-parameter
comparison, and A/B/C architecture matrix. The trace is explicitly a
deterministic specialist harness record, not an autonomous LLM execution
claim.
Production FEP remains `REVIEW` because edge-specific complex/solvent
topologies, lambda trajectories and complete open protocol evidence are
unavailable.

## Validation

The FEP package and paper tasks currently pass 32 automated tests. The tests
validate contracts, pinned inputs, endpoint artifacts, mapping evidence,
orchestration output and the architecture benchmark harness. They do not claim
publication-level free-energy reproduction.

## Remaining requirements

Connect a real model/tool runtime with decision and tool-call traces, generate
validated lambda-window inputs, execute a bounded alchemical smoke calculation,
and independently evaluate overlap and estimator inputs before adding further
paper systems.
