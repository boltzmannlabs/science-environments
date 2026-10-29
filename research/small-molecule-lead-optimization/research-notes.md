# Small-molecule lead optimization: research and design notes

**Status: supporting research for the version-0.1 implementation, In Progress.** Source inspection date: 28 October 2026. No scientific run, candidate evaluation, or comparison against the base agent has been performed for this contribution.

The [environment specification](../../environments/small-molecule-lead-optimization/ENVIRONMENT_SPEC.md) describes the reusable environment and its implementation boundaries. Source links and inspection boundaries are maintained in [references.md](references.md).

## Agreed scope

The environment supports general small-molecule lead optimization. Each task supplies its starting molecules, objective, target context when relevant, constraints, allowed tools, and evaluation contract. Synthesis planning, FEP, and simulation workflows are outside the agreed scope. No target is built into the environment's common rules.

Agent-Scientist supplies model execution and scientific tool access. The environment should add reusable task and evidence handling rather than another catalogue of scientific request fields. The local plugin interface and installation path are implemented and checked in an isolated host. These software checks do not establish live scientific-service readiness; see the [validation record](../../environments/small-molecule-lead-optimization/results/validation.md).

## Reference roles

### SMDD-Bench: task and evaluation conventions

The inspected lead-optimization metrics distinguish objectives to improve from properties to keep within tolerances and chemical constraints. Objective records include a property, direction, and improvement threshold relative to a baseline. Its separate evaluator reads a task definition, resolves inputs and output artifacts, and reports passed, failed, or errored steps. These are useful examples of explicit task and evaluation contracts. [S1–S3](references.md#smdd-bench)

The inspected implementation uses ADMET-AI and Boltz2 predictions for several endpoints. Those endpoints establish success against computational criteria, not experimentally demonstrated lead improvement. Its fixed chemistry cutoffs, similarity threshold, model choices, and output format are benchmark decisions; they are not adopted as universal requirements here. The repository's task archive was not downloaded, and the benchmark was not executed.

### PMO: evaluation under resource limits

Practical Molecular Optimization evaluates optimization methods under limited oracle access and motivates measuring how performance develops as evaluations are spent. The inspected paper compares 25 methods on 23 computational tasks. Its repository distinguishes repeated production runs from tuning. This supports making resource accounting and repeated comparisons explicit when later defining our evaluation protocol. [P1–P2](references.md#practical-molecular-optimization-pmo)

PMO's oracle scores are computational objectives; they do not supply experimental measurements for arbitrary new molecules. Its numerical budget, aggregation choices, and algorithm rankings are not defaults for this environment. A remote submission, an internal oracle evaluation, a candidate, and a model request can be different resource units; their accounting must be agreed before comparison.

## Local integration evidence

The inspected Agent-Scientist checkout contains canonical Boltzmann request definitions, file checks, and limits, with generated Small Molecule Design modules. Those contracts should determine permitted job names and payloads. The environment can connect task-level records to those tools while retaining molecule identity, parentage, input artifacts, job identities, and returned observations. Version 0.1 implements explicit agent-entered records and comparisons; it does not intercept or authenticate all scientific calls. [I1–I3](references.md#agent-scientist-and-local-repository-sources)

A catalogue entry alone does not show account entitlement or current worker operation. A submitted job is not a completed scientific result. Predicted affinity, docking score, predicted property, and experimental activity need distinct names, units, and provenance; a combined report must not silently exchange them.

## General environment and specific tasks

The environment should describe which information a task must declare. It should not select a target, compound series, property cutoff, budget, tool order, or ranking weights on behalf of every task. Which of these must be explicit before execution remains part of specification review.

COVID Moonshot/Mpro is a proposed future task only. A [primary-source feasibility review](moonshot-task-review.md) and task-preparation dossier are included. No frozen dataset, cutoff, assay selection or evaluation split is included. That task will require its own data qualification and review. An arbitrary generated molecule has no hidden experimental answer merely because its starting series came from a measured dataset.

## Enhancement options for discussion

The refined specification makes baseline coverage, investigation questions, endpoint comparisons, feedback, and stopping reasons concrete. The following are further design proposals, not selected algorithms or implemented features. They extend the objective/constraint and resource-accounting ideas above; they are not claims that the reference repositories implement these exact policies.

| Option | Benefit to the agent | Decision to discuss |
| --- | --- | --- |
| Tradeoff-based selection | Retain candidates for which improving one objective costs performance on another. A Pareto set contains candidates that are not dominated across all comparable objectives. | Whether tasks use a Pareto set, a primary objective with constraints, or declared weighted ranking; handling missing endpoints and uncertainty. |
| Diversity-aware batches | Avoid spending the entire assessment budget on nearly identical candidates; explore different permitted analogue branches. | Similarity representation, diversity rule, relationship to lead-preservation constraints, and budget allocation. |
| Assessment chosen for missing evidence | Prefer an assessment that can resolve a current selection question, such as missing baseline evidence or predictor disagreement. | Selection heuristics, repeat rules, and when uncertainty warrants an additional assessment. No automatic confidence model is assumed. |
| Reuse compatible evidence | Reuse an existing result when molecular form, endpoint, method/version, settings, target/structure context, and inputs match; retain its original source. | Exact matching/invalidation rules and resource accounting. Similar molecules or repeated references to one result are not independent evidence. |
| Explicit campaign memory for unsuccessful branches | Preserve constraints failed, unresolved scientific questions, and execution failures so the next round can revise its approach. | Which records are supplied to the model, how they are summarized, and how reevaluation is justified when evidence changes. A transient tool failure must not permanently rule out a molecule. |

The immediate review priority is the comparison contract: what constitutes a compatible baseline and what the agent should see when that evidence is absent. Selection algorithms, additional critic calls, and automatic stopping thresholds require separate discussion before implementation.

## Implemented choices and remaining decisions

The user selected **warn and record; let the agent decide**, explicit checks before costly actions and one campaign binding per session with explicit subagent attachment. Version 0.1 uses immutable JSON task/record contracts, SQLite transactions, verbatim molecular representations, compatible scalar comparisons and a separate offline evaluator. It introduces no specialist model or automatic ranking.

Further decisions concern chemical normalization/graph checks, aggregation across repeated evidence, automatic observation of native activity, ranking/uncertainty policies and real-task evaluator isolation. Numerical bounds and method compatibility do not replace chemical or assay review.

## Advisory integration review

The following are source-level findings from the inspected Agent-Scientist revision in [references](references.md#agent-scientist-and-local-repository-sources), not runtime validation:

- Pre-tool hooks accept action directives, not an arbitrary warning response. Callback failures/timeouts can block execution. Using this guard for advisory recording risks conflicting with the selected policy.
- Explicit environment check/status responses can present warnings for the agent to consider. Automatic post-tool observations arrive after the action; they cannot establish that the agent saw a warning before it submitted.
- The host has a context hook during turn preparation, but it is skipped when persistence is disabled. Delivery timing and coverage need testing; do not assume every internal model request receives fresh warnings.
- Deferred tool calls use normal dispatch. Code-execution RPC also uses dispatch, but may supply only a task ID that changes between turns. Session/campaign correlation must be explicit; ambiguous calls stay unassociated.
- Supported observation middleware or post-tool hooks can record native activity. Raw service calls and direct handler invocation may bypass them. Recording failures and unknown job outcomes must remain visible; no complete-monitoring or sandbox claim follows from a plugin hook.

**Approved and implemented workflow:** the agent requests an advisory check before a costly campaign action, decides, then uses its existing tools and explicitly records actions/results. Status/report retains the advice and records. One active campaign binding per session and explicit delegated-session attachment are implemented. Automatic interception remains unimplemented; the explicit-record coverage limitation is returned in every report.

The check operation must never silently submit a scientific job. Missing campaign association should produce an observation gap, not attach activity to a global most-recent campaign. No automatic request rewrite or retry is implied by warning-only behavior.

The current work is a local review draft. Issue discovery/creation and PR verification were unavailable because GitHub CLI authentication was unavailable; no issue assignment, maintainer review, remote submission, or approval is claimed.
