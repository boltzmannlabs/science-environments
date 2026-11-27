# Environment organization

Existing task IDs and native scientific execution identities are preserved. [migration_map.json](migration_map.json) records published path changes. Original campaign workspaces are unchanged.

## Published scope

The environment contains 19 scientific workflow records across six tasks. Preparation-only attempts, their configuration files and result/source packages, and their in-tree history references are excluded at the owner’s request. A Sun LEH session that executed inference and verification remains, with its actual outputs restored.

Matching runs/results/source directories use `run_<number>_<session-id>`. Existing numbers remain stable; gaps after cleanup are intentional. Native continuation sessions belong to their original scientific execution.

Configuration is separated into environment metadata, schemas, explicit shared settings and descriptive task records. Four frozen HY4 launch snapshots match their original exported settings. Unknown historical settings are not invented or silently made launchable.

Benchmark definitions, reference notes and execution comparisons are separate. Overall run-status labels are omitted; actual measurements, tool failures, unmet requirements and evaluator findings remain in the reports. Large/private native evidence stays outside the public export.

## Validation

- 19 task/config/run/result identities and 461 output hashes verified.
- Markdown links, JSON parsing and the new export’s scoped sensitive-content checks passed.
- No scientific calculations were repeated by this cleanup.
- Legacy artifact naming remains subject to source-verified model/tool/parameter metadata; no unavailable components were fabricated.

This removes the attempts from the current environment tree and its indexes. It does not rewrite Git commit history or delete original native SCI conversations.
