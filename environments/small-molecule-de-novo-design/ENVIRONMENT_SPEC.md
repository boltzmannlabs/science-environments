# De novo small-molecule design — environment specification

**Status: Specification.** This describes a scientific task contract.

## Objective

Generate molecular candidates for one p38α target. The agent retrieves and prepares the public 1A9U structure for common final docking with Smina. Ten final records form the evaluation panel; an up-to-three shortlist is separate.

## Inputs, constraints and outputs

The [task definition](tasks/p38alpha-design.md) specifies the required inputs, scientific objectives,
metrics, budget handling, failure states and output artifacts. The agent chooses
among authorized workflows; mandatory assessment rules remain fixed. The task
states the property constraints, and the operator may provide resource limits;
the agent discovers suitable authorized
Boltzmann tools in the active profile and prepares and verifies the
inputs, scoring assets and records. Freeze a common bundle and provide a separately
controlled evaluator for independent comparisons. Unresolved essential inputs
or capabilities stop execution with a recorded blocker, not an interactive query.

## Reproducibility and evaluation

Freeze scorer versions, inputs, identity rules, preparation, budgets and output
hashes. Keep observable failures and unknown backend counts explicit. Separately
controlled assessment must follow output freeze. Predicted values remain distinct
from experimental measurements.

[Shared specification](../../research/small-molecules/shared-specification.md),
[models and tools](../../research/small-molecules/models-and-tools.md),
[status](../../research/small-molecules/STATUS.md) and
[validation notes](../../research/small-molecules/specification-validation.md)
record the cross-task contract, dependencies and remaining work.
