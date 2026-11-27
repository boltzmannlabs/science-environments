# Execution records

One record represents one independently started task workflow. Corrected requests, alternative tools, revisions and native continuation sessions remain in that logical run. Preparation-only starts are excluded.

[Run registry](registry.json) links all six tasks to configurations and result packages. Usage belongs here, not in reusable configuration. Original full transcripts and large artifacts remain in private archives; per-call native history is retained outside this repository.

## Usage scopes

Each `run.json` separates the listed parent continuation sessions, recursively linked native specialist sessions, and their deduplicated sum in `usage_accounting`. The snapshot date, session IDs and excluded associated/other sessions are recorded explicitly. Reasoning tokens are a subset of output and are not added again. These persisted counters do not establish complete billing or auxiliary-call coverage.

`legacy_parent_snapshot` refers to one saved parent session, not all continuations. `historical_reported_accounting` and original `usage_summary.json`/`usage.json` files are earlier snapshots with their original coverage; they are not additional usage to add to the native totals. The result READMEs link to the counting scope.
