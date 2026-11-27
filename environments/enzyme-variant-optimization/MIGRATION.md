# Execution-layout migration

Existing task IDs and scientific evidence are preserved. [migration_map.json](migration_map.json) records relocated paths. Original workspaces and native histories are unchanged; no scientific jobs were replayed.

## Scope

23 independently started native workflow records span all six tasks. Continuation sessions are grouped rather than counted as fresh workflows; software fixtures are excluded. Four HY4 runs add assisted results for LEH, BLA, AtHOL1 and Zhang. Earlier Codex/DiscoveryRSI runs and interrupted starts are retained separately.

## Review items

- Full historic settings, completion timestamps and code versions are unknown where not recovered; no values invented.
- BLA/AtHOL1 HY4 remain partial despite native goal-completion messages. RML DiscoveryRSI completion claims remain unaccepted pending missing-stage review. Sun DiscoveryRSI lacks a returned independent evaluator result.
- Legacy/generated filenames remain preserved with checksums and mappings. Complete prescribed artifact renaming needs source-verified model/tool/parameter identity or a maintainer-agreed fallback; this export does not claim final naming compliance.
- Original large artifacts, raw requests and transcripts are retained privately; public copies are sanitized. This is an evidence export, not a new execution or a promise of portable replay.
- Benchmark comparisons keep their documented legacy layout and historical agent-alone scope; all assisted workflows are discoverable through the results/run indexes.

## Local validation

- 23 run/config/result identities checked across six tasks; 467 exported artifact checksums verified.
- 169 migrated non-Markdown legacy files verified byte-for-byte against the prior tracked files.
- All 232 JSON files parsed during final review; documentation links and path-character checks passed.
- All six historical benchmark reports rebuilt successfully from their explicitly routed historical inputs (16 linked figures).
- Revised native launch preparation exercised against the relocated task path; SCI and scientific execution were not started.
- Maintained launcher, validator and report modules compile; git diff --check passed.
- New execution/config/result exports checked for internal host paths, private addresses, storage-user identities and signed URL signatures; none found by those checks. This is a scoped scan, not a guarantee about all possible sensitive content.
- Complete prescribed generated-artifact naming remains a documented review item; safe path characters alone do not establish naming compliance.
