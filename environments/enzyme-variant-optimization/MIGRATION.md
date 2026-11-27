# Execution-layout migration

Existing task IDs and scientific evidence are preserved. [migration_map.json](migration_map.json) records relocated paths. Original workspaces and native histories are unchanged; no scientific jobs were replayed.

## Scope

23 independently started native workflow records span all six tasks. Continuation sessions are grouped rather than counted as fresh workflows; software fixtures are excluded. Four HY4 runs add assisted results for LEH, BLA, AtHOL1 and Zhang. Earlier Codex/DiscoveryRSI runs and interrupted starts are retained separately.

## Review items

- Full historic settings, completion timestamps and code versions are unknown where not recovered; no values invented.
- BLA/AtHOL1 HY4 remain partial despite native goal-completion messages. RML DiscoveryRSI completion claims remain unaccepted pending missing-stage review. Sun DiscoveryRSI lacks a returned independent evaluator result.
- Legacy/generated filenames remain preserved with checksums and mappings. Complete prescribed artifact renaming needs source-verified model/tool/parameter identity or a maintainer-agreed fallback; this export does not claim final naming compliance.
- Original large artifacts, raw requests and transcripts are retained privately; public copies are sanitized. This is an evidence export, not a new execution or a promise of portable replay.
- Benchmark definitions, reference notes and evaluated outputs are now separated; all assisted workflows remain discoverable through the results/run indexes.

## Local validation

- 23 run/config/result identities checked across six tasks; 467 exported artifact checksums verified.
- 169 migrated non-Markdown legacy files verified byte-for-byte against the prior tracked files.
- All 232 JSON files parsed during final review; documentation links and path-character checks passed.
- All six historical benchmark reports rebuilt successfully from their explicitly routed historical inputs (16 linked figures).
- Revised native launch preparation exercised against the relocated task path; SCI and scientific execution were not started.
- Maintained launcher, validator and report modules compile; git diff --check passed.
- New execution/config/result exports checked for internal host paths, private addresses, storage-user identities and signed URL signatures; none found by those checks. This is a scoped scan, not a guarantee about all possible sensitive content.
- Complete prescribed generated-artifact naming remains a documented review item; safe path characters alone do not establish naming compliance.

## Configuration and naming correction

The complete configuration layout now contains environment.yaml, real schemas, opt-in shared settings and task configurations with descriptive model/approach filenames. Original configuration IDs and all 23 logical native run IDs remain unchanged. Four exact HY4 launch snapshots moved to their run records with checksums. Earlier incomplete settings are explicitly non-launchable. Benchmark comparisons and generated-source snapshots were relocated through additional entries in migration_map.json; no scientific measurements were recalculated.

### Follow-up audit checks

- Environment/configuration YAML and JSON Schemas validate all 23 configuration records; all four populated config areas have real linked content.
- Complete HY4 launch preparation passes with descriptive task settings; incomplete historical configurations are rejected before launch. No SCI or scientific job started.
- All four frozen HY4 launch snapshots match the settings in the preceding commit.
- Schema checks reject missing model settings, invalid model types and non-boolean launch readiness.
- All six benchmark reports rebuild from the relocated reference/evaluation paths.
- 23 native run identities and 467 output checksums remain validated; documentation links pass.
- Native run IDs remain unchanged. Task/config/result indexes provide model and approach labels so users do not need to decode session IDs.

## Numbered run folders

All 23 existing executions now use run_001_<original-session-id> style names, numbered independently by task/start order. Matching runs/results/source folders have identical names. Native run IDs, session lineage and scientific outputs remain unchanged. The run_prefix_mappings entries in migration_map.json preserve previous paths. Append future run numbers; do not renumber existing records.

Validation for numbered folders: all 23 records and 467 artifact checksums pass; all Markdown links and source-export hashes resolve; all six benchmark reports rebuild; 313 scientific output/source files are byte-identical to the preceding commit. No scientific jobs were launched.

## Run-level status field removal

At the owner’s request, execution-status fields and status columns were removed from the published run registry, run records and result summaries. Original tool job statuses, evaluator findings, frozen inputs and factual reports are unchanged. No replacement completed/partial label was added.

Remaining run-status headings, obsolete status explanations and overall classification fields in exported summaries were removed. Findings, unmet requirements, qualification evidence and native tool-job statuses remain intact.
