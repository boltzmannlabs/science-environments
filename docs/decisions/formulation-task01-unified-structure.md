# Decision: register a unified formulation Task - 01

Date: 2026-11-15
Status: Implemented on requested Rebolt working branch; scientific review pending.

## Context

The user requested a formulation environment and consistent task-specific folders under tasks, benchmark and results. Existing Rebolt environments, including ranolazine-focused formulation_dissolution, must remain intact. Current scientific evidence concerns clarithromycin IR under an assumed 800 mg basis and cannot be pooled with other APIs or release types.

## Decision

Create `environments/formulation_environment/` with one shared source package and explicit task registry. Preserve the requested literal identifier `Task - 01` in all three task sections. Use singular benchmark to match repository structure. Put title/objective/overall work in task documentation, source/metric contracts in benchmark, and curated v1/v2 calculations/reports in results. Add a linked research topic.

## Alternatives

Overwriting the existing ranolazine environment risks conflating distinct scientific systems. A single flat results folder hides task provenance. Duplicating SDKs/full article archives adds avoidable legal/privacy and reproducibility burden. Claiming a better-than-literature formulation from lower curve-fitting error is scientifically unsupported.

## Consequences

New tasks require matched folders, registry/dispatch entries and tests; existing tasks/results stay versioned. Inputs are portable snapshots, runs refuse overwrites, and published artifacts exclude local/account details. Tests and actual offline replay gate publication. No new root license is selected, no main merge is performed, and no review/physical validation is inferred from push success.
