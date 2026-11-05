# Molecular optimization

**Status: Specification.** Target: DRD2.

Task: [tasks/drd2-optimization.md](tasks/drd2-optimization.md).

The agent improves supplied starting molecules using the activity/QED/similarity
qualification rules. Optional ADMET guidance and mandatory ADMET conditions have
separately defined roles. Multiple starting molecules are cases for one target.

Share the task file and its prepared input/scorer bundle with the execution agent.
Working predictor assets and execution limits must be supplied before a run.

Common [environment specification](../ENVIRONMENT_SPEC.md),
[tool boundaries](../MODELS_AND_TOOLS.md) and [status](../STATUS.md) apply.
This folder contains a task specification, not an executable implementation.
