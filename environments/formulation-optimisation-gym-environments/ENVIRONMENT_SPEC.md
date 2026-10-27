# Environment specification — formulation optimization gym

## Scientific scope

Investigate FDA-reported ranolazine extended-release dissolution recall D-0092-2024 (Glenmark 500 mg), maintaining distinct cases for other manufacturer/strength recalls. Do not infer historical recalled-batch formula, controlled method, numeric failure, root cause, or QC criteria from a public enforcement notice or later label. Distinguish external published research prototypes from recalled tablets.

## Executable components

The [working gym](scripts/formulation-optimization-gym/) implements persistent evidence-linked episode state, typed actions and observations, budget/approval ledger, six bounded local specialist contracts, source import and cross-check scripts, a deterministic composition validator, model/tool adapters, evaluation verifier/baseline/holdout benchmark, and CLI/tests. No autonomous SCI delegation or authorized live dissolution API was present. See its [architecture](scripts/formulation-optimization-gym/docs/architecture.md). The user-supplied original build specification remains outside this documentation tree at `/home/boltzmann6/sai_kiran/formulation_optimisation_gym/ranolazine_formulation_optimization_gym_spec.md`; this tree does not copy or modify it.

## Evidence and model rules

Use evidence labels `measured`, `literature_reported`, `predicted`, `derived`, `assumed`, `unknown`; store source/provenance and units. Accept laboratory measurements only with explicit authorized records and approval. Without independently verified measured holdouts, product benchmark is `not_evaluated`. Separate opt-in simulation on other-product research compositions from the historical episode; disclose all assumptions, constraints, model version, seed, uncertainty interpretation and lack of experimental validation. Do not trigger physical experiments or product changes.

## Organization

Research: [notes](../../research/formulation-optimisation-gym-environments/research-notes.md), [references](../../research/formulation-optimisation-gym-environments/references.md). Configuration: [config index](config/README.md). Tasks: [tasks index](tasks/README.md). Tests: [tests index](tests/README.md). Actual outcomes: [report](ENVIRONMENT_REPORT.md), [status](STATUS.md).
