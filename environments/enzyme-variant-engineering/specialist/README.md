# Native enzyme specialist

This is an ordinary Agent-Scientist saved-specialist definition, not a plugin,
separate agent engine or new model. It is advisory: the child reads evidence,
researches chemistry and proposes targeted follow-up; the parent runs scientific
tools using existing native authorization and input validation.

## Import and review

Use an SCI version with native saved specialist support. From the intended
profile, using the actual file path in your checkout:

```text
/subagent import "specialist/enzyme-variant-specialist.json"
/Update_subagent enzyme-variant-specialist
/new
```

The relative path above assumes SCI is running in this environment directory.
Native import keeps the definition disabled until review. Review its instructions
and three existing capabilities: file reading, web search and page extraction.
Resolve missing tools through normal SCI setup or deselect them if not required.
Do not edit profile JSON to bypass native review. Existing definitions are not
overwritten: choose a new name or update the existing one explicitly.

It is explicit-only so the base-agent arm does not receive it automatically.
After review, a direct assignment is:

```text
/subagent run enzyme-variant-specialist "Review the BglB task and the supplied candidate evidence. Identify the scientific failure points and recommend the smallest informative next investigation."
```

Pass actual task/result paths and remaining resource limits in the assignment.
The child starts with fresh context; naming it does not give it the earlier chat.
The parent can use native `delegate_task` with the saved specialist name, retain
its receipt and continue the normal workflow after receiving its recommendation.
Use `/subagents` and `/subagent status` for native definition/run information.

## Boundaries

The definition has no Boltzmann job permissions, terminal access, child grants,
credentials or private source locations. Its 30-iteration/900-second values are
native specialist defaults, not an extra scientific budget or exact spending cap.
The native allowlist is not an OS-level filesystem/network sandbox. No automatic
restart-resumption or experimental outcome is implied by saving this definition.

Current native references:
[saved specialists](https://github.com/boltzmannlabs/Agent-Scientist/blob/main/website/docs/user-guide/features/saved-specialists.md)
and [delegation](https://github.com/boltzmannlabs/Agent-Scientist/blob/main/website/docs/user-guide/features/delegation.md).
Use the installed version's documented commands if these change.
