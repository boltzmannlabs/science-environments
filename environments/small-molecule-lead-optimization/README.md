# Small-Molecule Lead Optimization

**Lifecycle: In Progress. Version 0.1 implements a local Agent-Scientist plugin and offline evaluator.** Installation, native loader/registry dispatch and synthetic software checks are exercised in isolation. Live scientific-service qualification, a real case study and a matched base-agent comparison remain outstanding.

This is a general environment for investigating supplied small-molecule leads. Each task supplies its target or scientific context, starting compounds, objectives, constraints, permitted tools, budgets and final evaluation. Synthesis planning, FEP and molecular-dynamics simulation are excluded.

The agent asks: **what should improve, what compatible evidence shows improvement, and what should be investigated next?** The environment keeps the task snapshot, candidate lineage, observations, advice, actions, decisions and resource records. Existing Agent-Scientist tools perform scientific execution and retain ownership of request/file validation.

## Implemented behavior

- Explicit checks before costly actions: **warn and record; let the agent decide**. Continuing does not erase task violations or grant evaluation eligibility.
- One active campaign binding per session, with explicit subagent attachment. A conflicting record association is rejected; scientific execution remains with the host.
- Transactional SQLite storage, immutable record IDs, idempotent repeated writes, restart and unknown-outcome reporting. No automatic job retries.
- Endpoint comparisons requiring compatible molecular-form associations, units, evidence types, methods, versions and context. Missing, censored or ambiguous evidence remains unresolved.
- Numerical objective and constraint assessments, including baseline deltas, minimization/maximization and target intervals. No universal thresholds, ranking weights or chemical normalization.
- Requested, observed, estimated and unknown usage kept separate. Pending actions retain unresolved commitments.
- Frozen submissions with a digest, plus a separate offline evaluator that checks a retained receipt and evaluator-owned references.

Recording is currently explicit: the agent calls the environment tools alongside its existing scientific tools. There is no automatic interception of all tool/model calls, independent authentication of agent-entered observations, chemical graph validation, or protected-label sandbox. These limits appear in reports.

## Use and review

1. [Installation](scripts/README.md): directory or package installation, campaign storage setting, native discovery checks.
2. [Environment specification](ENVIRONMENT_SPEC.md): shared behavior and implementation boundaries.
3. [Configuration and record contracts](config/README.md), [tool-capability mapping](config/tool-mapping.md), and [task guidance](tasks/README.md).
4. [Runnable synthetic example](tasks/synthetic/README.md): software-only records and evaluator; no models, services or chemistry claims.
5. [Tests](tests/README.md), [validation evidence](results/validation.md), and [status](STATUS.md).
6. [Research](../../research/small-molecule-lead-optimization/research-notes.md) and [references](../../research/small-molecule-lead-optimization/references.md).

The installed agent discovers `leadopt_campaign` and the `leadopt_env:lead-optimization` skill. It creates a task-backed campaign, attaches its session, checks planned actions, uses its existing tools, and records results and decisions. Humans do not manually perform each research step. Maintainer reproduction scripts are separate from that agent workflow.

## Scientific validation still needed

[COVID Moonshot](tasks/covid-moonshot/README.md) is a proposed retrospective measured-library task. Its source, assay and cohort review is unfinished. Such a task tests prioritization of recorded compounds; its labels cannot establish experimental improvement for newly generated analogues.

The [comparison protocol](tests/COMPARISON_PROTOCOL.md) separates software reliability from scientific performance. No base-agent comparison has run and no improved-compound or error-free-execution claim is made.

This remains a local contribution on the feature branch. Issue linkage and maintainer/scientific review are outstanding; see [STATUS.md](STATUS.md). Repository license selection is pending in [LICENSE](../../LICENSE).
