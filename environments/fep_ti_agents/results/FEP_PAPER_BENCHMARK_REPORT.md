# FEP paper benchmark — current milestone

Task: `FEP-PAPER-001` (CDK2, edge `17 -> 1h1q`)

This milestone keeps the 15 specialist contracts (`FEP-AG01`–`AG15`) and 10
problem-solving contracts (`FEP-PS01`–`PS10`) and tests them against the
paper-derived CDK2 workflow. The roles are not counted as autonomous AI agents
unless a model decision, tool call, handoff and execution trace are present.

## Operational audit

The audit is machine-readable in `results/operational_role_audit.json`:

| Category | Count | Meaning |
|---|---:|---|
| Operational | 2 | Executable paper-task tool and evidence are present (mapping and ligand parameterization). |
| Partial | 6 | Some executable/readiness evidence exists, but the complete specialist decision loop is not connected. |
| Specification | 7 | Contract/task exists, but no paper-task executable evidence exists yet. |
| Fixture-only problem solving | 10 | PS roles run on the synthetic validation fixture, not production trajectories. |

## Orchestration

`scripts/orchestrate_paper_task.py` applies an auditable specialist-selection
policy. It selects setup, leg-validation and audit roles for this neutral
transformation and records the missing `lambda_trajectories_present` gate. It
does not claim LLM autonomy; it is a deterministic harness until a model/tool
runtime is connected.

## Architecture experiments

`results/agent_architecture_benchmark.json` records the requested experiments:

- **A:** general-purpose agent baseline;
- **B:** general agent plus relevant FEP specialists;
- **C:** orchestration plus problem-solving roles and independent evaluator.

The current comparison is evidence-based harness output, not a claim that 25
independent AI agents executed. The paper reconstruction achieved 20/20 on the
evaluated configuration fields, but scientific qualification remains `REVIEW`
because production lambda trajectories, overlap, convergence and uncertainty
are absent.

## Remaining gates

1. Connect an actual model/tool runtime and persist decision/tool-call traces.
2. Generate validated lambda-window inputs from the endpoint systems.
3. Run a bounded alchemical smoke calculation, then evaluate overlap and
   estimator inputs independently.
4. Extend to FEP-PAPER-002 and a charge-changing FEP-PAPER-003 only after the
   first workflow is stable.
