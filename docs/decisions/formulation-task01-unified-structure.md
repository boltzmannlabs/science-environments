# Decision: register a unified formulation Task - 01

Date: 2026-11-15
Status: Implemented on requested Rebolt working branch; scientific review pending.

## Context

The user requested a formulation environment and consistent task-specific folders under tasks, benchmark and results. Existing Rebolt environments, including ranolazine-focused formulation_dissolution, must remain intact. Current scientific evidence concerns clarithromycin IR under an assumed 800 mg basis and cannot be pooled with other APIs or release types.

## Initial decision

Create `environments/formulation_environment/` with one shared source package and explicit task registry. Preserve the requested literal identifier `Task - 01` in all three task sections. Use singular benchmark to match repository structure. Put title/objective/overall work in task documentation, source/metric contracts in benchmark, and curated v1/v2 calculations/reports in results. Add a linked research topic.

## Alternatives

Overwriting the existing ranolazine environment risks conflating distinct scientific systems. A single flat results folder hides task provenance. Duplicating SDKs/full article archives adds avoidable legal/privacy and reproducibility burden. Claiming a better-than-literature formulation from lower curve-fitting error is scientifically unsupported.

## Consequences

New tasks require matched folders, registry/dispatch entries and tests; existing tasks/results stay versioned. Inputs are portable snapshots, runs refuse overwrites, and published artifacts exclude local/account details. Tests and actual offline replay gate publication. No new root license is selected, no main merge is performed, and no review/physical validation is inferred from push success.

## Follow-up naming decision

At the user's request, replace the numbered directory name with `clarithromycin-500mg-ir-formulation-dissolution` under tasks, benchmark and results. Preserve `Task - 01` only as the stable logical ID and CLI selector. Record `folder_slug` separately, update paths/links/manifests/tests, and leave scientific artifacts unchanged. Future tasks should similarly use meaningful descriptive folders rather than number-only directory names.

## Unified numbered task folders (2026-11-20)

The user's latest naming requirement supersedes the earlier descriptive-only convention: use `task-NN-short-title` consistently under tasks, benchmark and results. Task-01 now uses `task-01-clarithromycin-ir-formulation-dissolution`; Task-02 uses `task-02-ranolazine-er-dissolution`. Task-02's existing environment-local config, scripts and docs folders use the same slug. Update registry paths, maintained links and manifest locations while preserving scientific artifacts, their hashes and historical execution receipts. The shared structure check verifies every registered task and rejects unregistered task directories in the three required sections.
