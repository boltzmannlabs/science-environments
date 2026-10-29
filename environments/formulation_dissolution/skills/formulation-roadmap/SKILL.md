---
name: formulation-roadmap
description: Coordinate evidence-gated work in the ranolazine formulation-optimization-gym, select the literature or recall track, and turn its status gaps into bounded implementation tasks.
---

# Formulation roadmap

Use for project continuation and gap-to-task planning. Locate the repository from the user path or workspace. Read `STATUS_AND_GAPS_REPORT.md`, `configs/task.yaml` and [implementation plan](../../docs/implementation_plan.md). Reports describe snapshots; inspect current tools before claiming availability.

## Select the work

- Literature: audited research data and exploratory evaluation only.
- Recall: selected product/lot, controlled records and authorized analysis.
- Software: implement contracts/guards with labelled fixtures while scientific evidence is missing.

Keep Glenmark D-0092-2024 and Ajanta D-0010-2027 separate. Without case selection, continue independent software/literature work and obtain selection before case-dependent analysis. Do not select whichever episode appears first.

## Route

- [Data intake](../formulation-data-intake/SKILL.md): identity, source rights, controlled measurements.
- [Literature curation](../formulation-literature-curation/SKILL.md): publication tables/graphs and exploratory eligibility.
- [Tool integration](../formulation-tool-integration/SKILL.md): documented contracts, failures and budgets.
- [Candidate review](../formulation-candidate-review/SKILL.md): composition/process/compatibility/stability eligibility.
- [Experiment design](../formulation-experiment-design/SKILL.md): proposals and approval/result reconciliation.
- [Benchmark](../formulation-benchmark/SKILL.md): splits, model validity and comparisons.

Read only the relevant workflows. Use plan task IDs for dependencies and handoffs. Existing `agents/` specialists are bounded functions, not autonomous SCI agents. Project-authorized planning/review delegation does not establish scientific specialist benefit.

For runtime changes, write a failing behavior test, implement the smallest change and run relevant checks with independent review. Documentation changes need skill/link validation, not tests that mirror wording.

## Gate and deliver

Evaluate G0–G5 separately: software, eligible data, analysis, predictive evidence, comparative optimization and prospective confirmation. Investigation closure cannot satisfy later scientific gates. Never invent measurements, numerical success targets, formulation ranges or API endpoints.

Reuse existing authorization. Physical experiments, regulated updates, spend and manufacturing changes require approval covering the specific action; software proposals do not execute them.

Report track/case, evidence inspected, work completed with paths, checks run, unmet gates/owners and next executable task. Distinguish implemented features from proposed files and hypotheses from results. If the user requests skills/planning only, finish those artifacts without beginning the runtime backlog.
