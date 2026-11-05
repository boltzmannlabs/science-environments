# Small-molecule optimization — environment specification

**Status: Specification.** This describes a scientific task contract.

## Objective

Improve predicted DRD2 activity and QED while retaining similarity to each original starting molecule. ADMET reward guidance and mandatory ADMET conditions are distinct frozen variants.

## Inputs, constraints and outputs

The [task definition](tasks/drd2-optimization.md) specifies the required inputs, scientific objectives,
metrics, budget handling, failure states and output artifacts. The agent chooses
among authorized workflows; mandatory assessment rules remain fixed. Prepared
inputs, scoring assets, evaluator and execution limits are required before a run.

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
