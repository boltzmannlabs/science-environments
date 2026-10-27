# synthesis-route-gym — environment status

## Current update — 26 October 2026

**Lifecycle status: In Progress.** This update tracks the Synthetic Chemistry environment contribution on `Rebolt`. The server-6 development workspace contains later local implementation; repository delivery, independent scientific review and broader integration remain separate checks. The historical preparation snapshot is preserved below.

### Completed work

- Reviewed Agent-Scientist and its existing chemistry connector; listed the five tools and checked access, inputs and outputs.
- Identified sample targets, inventory sources and gaps; prepared the public development targets and a fixed inventory sample.
- Set up AiZynthFinder, ran initial cases, captured real tool results and native route formats, and completed a bounded 20-target development baseline.
- Defined route plausibility criteria and metrics with AI-assisted chemistry review, and separated development cases from locally reserved protected evaluation cases. Independent human SME sign-off and independent protected custody remain open.
- Consolidated baseline results, failures and capability gaps; drafted task, route, action and observation schemas; defined environment actions, budgets, checks and scoring; and prepared the implementation backlog.

These are documented development deliverables. Stock termination and route-format checks are computational evidence, not proof of a feasible synthesis or physical reagent availability.

### In-progress repository work

- Create the separate environment package and versioned schemas. **Local package and schema checks exist; contribution and review in this repository are in progress.**
- Add task, inventory and route loaders with evidence storage. **Local loaders and storage checks exist; contribution and review in this repository are in progress.**
- Confirm data and review support for condition and impurity task slices. **Narrow public development evidence exists; independent scientific review and validated outcome claims remain open.**

The current tracked task is [Issue #14: add inventory and supported constraints to retrosynthesis tasks](https://github.com/boltzmannlabs/science-environments/issues/14). It distinguishes the existing local inventory and route checks from the remaining tool-specific integration and two-scenario validation.

### Evidence and limits

The server-6 workspace retains the source records under `agent-scientist-review-2026-10-19/`, `synthesis-benchmark-preparation/`, `synthesis-aizynthfinder-baseline/`, `synthesis-route-plausibility/`, `synthesis-evaluation-split/`, `synthesis-baseline-consolidation/`, `synthesis-route-contracts/`, `synthesis-environment-specification/`, `synthesis-environment-backlog/` and `synthesis-route-gym/IMPLEMENTATION-STATUS.md`. This status-only contribution does not copy raw tool outputs, model assets, protected answers or credentials. No repository environment code, independent chemistry sign-off or protected evaluation run is claimed by this update.

## Historical preparation snapshot — 22 October 2026

**Reporting cutoff:** Original Synthetic Chemistry preparation work through the development/evaluation case split.  
**Prepared:** 22 October 2026.  
**Scope:** This is a historical milestone snapshot for the `Rebolt` branch. Later local environment implementation is intentionally outside this status update.

## Completed through this milestone

| Planned item | Recorded outcome |
|---|---|
| Review Agent-Scientist and the existing chemistry connector | Reviewed the installed Agent-Scientist runtime, chemistry connector, authorization, job lifecycle, delegation path and observed gaps. Main-model chat execution was a separate dependency. |
| List the five tools; check access, inputs and outputs | Verified access and saved real request/output fixtures for retrosynthesis, forward reaction prediction, atom mapping, condition recommendation and impurity prediction. These are interface smoke tests, not accuracy benchmarks. |
| Identify sample targets, inventory sources and gaps | Reviewed public route/stock sources and selected PaRoutes 2.0 for a reproducible development task. Recorded tool, inventory, evidence, leakage and evaluation gaps. |
| Prepare targets and the inventory sample | Prepared 20 public development targets, five named smoke targets and a fixed PaRoutes n1 inventory with 13,415 distinct full InChIKey identities. Physical stock availability, quantities and prices were not verified. |
| Set up AiZynthFinder and run initial baseline cases | Installed a separate, pinned AiZynthFinder 4.4.1 environment and ran the initial pilot against the fixed development stock. Preserved settings, model-asset hashes, logs and native outputs. |
| Capture real tool results and route formats | Retained the five Boltzmann chemistry outputs and native AiZynthFinder route JSON. Documented differences in route structure, ranking and score fields without assigning unsupported units or experimental meaning. |
| Run the baseline on a bounded development set | Completed all 20 public development target runs under fixed settings. The saved exports contain 216 routes: 203 terminate in the sample stock and 13 do not. Nineteen of 20 targets have at least one stock-terminated export. These are computational results, not verified syntheses. |
| Define route plausibility criteria and metrics with SMEs | Defined literature-grounded technical, stock, reaction-step, evidence and route-level criteria, metrics and review templates with AI-assisted chemistry review. Independent human-SME sign-off and experimental validation remain pending. |
| Separate development cases from protected evaluation cases | Kept the 20 public development cases separate from 40 locally reserved evaluation cases, with overlap checks and evaluator-side reference handling. This is logical local separation; an independent steward and isolated protected execution are still required. No reserved cases were executed for this milestone. |

## Limits at this cutoff

- Route structure and stock checks do not establish chemical feasibility, laboratory safety or physical reagent availability.
- The five live tool captures are interface evidence. Returned scores, yields and condition fields require documented semantics and independent review before scientific claims.
- The locally reserved evaluation set is not an independently sealed benchmark. Its answers and raw reference artifacts must remain outside solver inputs and this repository update.
- This status file reports the specified preparation milestone only. It is not a claim that later work has not occurred.

## Next work in the original plan

1. Consolidate baseline results, failures and capability gaps.
2. Draft task, route, action and observation schemas.

