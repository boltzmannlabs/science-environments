# Implementation status

**Lifecycle: In Progress. Local implementation and review draft, version 0.1.**

## Implemented and checked locally

- General lead-optimization specification, research references and existing-tool capability mapping.
- Versioned JSON task and record contracts, with runtime validation and checked schema exports.
- Standalone Agent-Scientist plugin, registered skill, schema discovery and local CLI.
- Explicit checks before costly actions; warning-only task-rule handling and durable continuation records.
- One campaign binding per session, explicit subagent attachment and record-association checks.
- SQLite transactions, immutable/idempotent records, restart persistence and unresolved-attempt tracking.
- Compatible scalar evidence comparisons, numerical constraints, separate eligibility, and requested/observed/estimated/unknown resource records.
- Frozen submissions, retained-receipt verification and a separate offline evaluator.
- Runnable artificial example, executable unit/adversarial tests, isolated native loader/dispatch test and offline package installation check.
- Scientific comparison protocol and a Moonshot preparation dossier; the latter is not a runnable scientific task.

The [validation record](results/validation.md) gives commands, versions and evidence. These checks use artificial data and isolated host storage. No active user installation/configuration was changed, and no model or scientific-service call ran.

## Explicit implementation limits

Version 0.1 records actions/results supplied by the agent. It does not automatically intercept native scientific/model calls or authenticate their provenance. Reports disclose incomplete coverage. Molecules are opaque source/form records; graph validation, normalization, replicate aggregation and automatic ranking are not implemented. The evaluator does not provide filesystem isolation or prove lack of prior model exposure.

Synthesis planning, FEP and molecular-dynamics simulation remain outside scope. The environment cannot guarantee error-free operation or better scientific performance than the base agent.

## Remaining work

1. Qualify a model using the installed skill and actual scientific tool outputs, with explicit resource allowance and dated job/artifact evidence.
2. Approve and freeze the first real case's dataset, identities, assay endpoint, cohort, scoring and protected evaluator deployment. The [Moonshot dossier](tasks/covid-moonshot/README.md) records preparation gaps; it has not been run.
3. Execute the matched base-agent comparison under the [protocol](tests/COMPARISON_PROTOCOL.md), then obtain scientific review.
4. Link a tracking issue and obtain maintainer/software review before publication or merge. The [local contribution draft](results/contribution-draft.md) is prepared; no issue or PR was published.

Additional enhancement proposals—automatic observation, chemical-graph policies, richer uncertainty and selection algorithms—require separate design agreement. They are not implied implemented by the general specification.

## Contribution state

Local branch: `feat/small-molecule-lead-optimization`. GitHub CLI issue discovery was previously unavailable due to authentication; issue linkage remains unverified. No reviewer approval, PR, merge or scientific acceptance is claimed. Repository license selection remains pending in [LICENSE](../../LICENSE).
