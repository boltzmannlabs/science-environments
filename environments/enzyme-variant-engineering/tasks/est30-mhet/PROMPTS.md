# Est30 Workflow Launch Prompts

Start SCI from the `environments/enzyme-variant-engineering/` directory.
Use a fresh ordinary main-profile conversation for each arm. An existing
conversation may retain an older tool/subagent snapshot.

The [task](TASK.md) is shared. The two prompts below select the arm; neither
changes the task or grants additional service permissions. Native subagents are
external Agent-Scientist capabilities, not files installed by this environment.

## Agent alone

```text
Run the complete assignment in tasks/est30-mhet/TASK.md as the agent-alone arm.
Do not use delegate_task, saved specialists, temporary subagents or advice from
another arm. Choose suitable native Boltzmann and/or ToolUniverse methods.
Complete actual sequence design, property evaluation, shortlisted structures and
complexes, quality/catalytic checks, at least one justified results-driven revision,
re-evaluation and final reporting. Follow the stated scope and native permissions.
Save results under a new .runs/est30-mhet/agent-alone/<timestamp>/ directory.
Do not read other-arm outputs or withheld reference outcomes. Preserve failures,
actual job IDs and missing results. Do not stop at planning or a mutation scan.
Report the session ID and output directory, then execute the full assignment.
```

## Agent with external enzyme subagents

```text
Run the same complete assignment in tasks/est30-mhet/TASK.md as a fresh assisted
arm. Use native delegate_task with tasks[].specialist set explicitly to
enzyme-variant-proposer and enzyme-variant-critic. Pass the task, permitted sources,
actual artifact paths and remaining resources to each. Obtain a proposal and a
separate critique before execution, then consult both on actual initial results
to decide the optimization revision. You execute scientific tools and re-evaluate
the changes; the critic is not a user-approval gate or independent evaluator.
Use the same assignment limits, counting specialist work within this arm's total.
Save results under a new .runs/est30-mhet/agent-with-specialist/<timestamp>/ directory.
Do not inspect the other arm, withheld reference outcomes or use the older
enzyme-variant-specialist. Do not silently replace a missing named role.
Retain real subagent run IDs, advice, decisions, scientific job IDs and outputs.
Complete the full workflow, including justified follow-up and final reporting.
```

## After execution

Keep native receipts and raw/private artifacts locally. Review outputs before
adding shareable scientific tests and results to the repository. Apply the same
declared evaluation procedure and retain negative or incomplete outcomes.
