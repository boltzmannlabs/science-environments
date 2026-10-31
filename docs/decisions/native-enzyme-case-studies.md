# Minimal native enzyme case-study environment

## Context

The earlier enzyme contribution concentrated on a research runner and software
fixtures. The clarified requirement is real scientific assignments, their tests
and results, plus a specialist that investigates failure points. Native
Agent-Scientist already provides the generic machinery.

## Decision

Replace `environments/enzyme-variant-optimization/` with
`environments/enzyme-variant-engineering/`, keeping the scientific title Enzyme
Variant Optimization. Use Markdown tasks, native saved-specialist data and a small
case-specific output evaluator. No copied execution engine, plugin, job client,
tool catalogue, input validator, state database, scheduler or model broker.

Preserve the old contribution in Git history and a local archive before removal.
Keep published reference values separate from unexecuted agent arms and from
software tests. The first case uses BglB activity/stability measurements.

## Consequences

The environment is smaller and follows ordinary SCI execution. It adds no OS
isolation, exact token/dollar enforcement or restart-persistent agent process.
The specialist is imported/reviewed natively; no profile state is silently edited.
Scientific benefit remains unmeasured until real comparison runs are completed.
Public-literature reproduction and blinded prospective benchmarking are different
claims. A recovery continuation must report inherited context and cumulative cost.

## Alternatives not selected

Further extending the old runner would keep redundant orchestration and packaging
dependencies. A documents-only environment would omit the needed native specialist
and scientific output checks. The selected design adds only those domain-specific
elements while leaving execution in SCI.

Tracking: [replacement issue #87](https://github.com/boltzmannlabs/science-environments/issues/87).
Follow the repository's issue/branch/PR/manual-review workflow; do not bypass main.
