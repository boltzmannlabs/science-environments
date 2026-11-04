# Enzyme Variant Environment Native Execution

## Context

The previous enzyme package duplicated workflow execution and saved-state
machinery around capabilities already provided by Agent-Scientist. It also
bundled a separate specialist implementation. The current contribution needs a
clear scientific environment that follows the repository's standard layout.

## Decision

Replace only the old enzyme-variant-optimization environment and its matching
research directory with enzyme-variant-engineering. Keep a process specification,
model/tool inventory, status, one concrete Est30 task and research references.
Use native Agent-Scientist tool discovery, execution, validation and records.

Saved-subagent definitions and implementation belong in the Agent-Scientist
repository and must follow its separate branch and PR process. This environment
may specify required role names and expected behavior, but does not ship their
code, personal profile state or installation files.

## Alternatives

Keeping the old runner would retain duplicate execution and maintenance paths.
Copying the newer local specialist definitions here would violate repository
ownership. Empty test/result folders would add no evidence. None is included.

## Consequences

The environment has no installable package or replacement job runner. A task
still depends on configured native services and applicable model/software access.
Existing local chats, plugins and records are not changed by this repository PR.
Tests and results are added after completed artifacts are reviewed; scientific
improvement and public-release readiness are not implied by documentation checks.
