# Configuration

`offline-science.json` is a valid minimal `srg-science-config-v1` configuration for software replays. It does not activate a reaction predictor or provide measured outcomes. Task constraints and budgets belong in the task JSON, not this file.

For ordinary Agent Scientist, configure trusted host settings from [the integration guide](../integrations/agent_scientist/README.md): `SRG_CHEMISTRY_PYTHON`, optional `SRG_PACKAGE_ROOT`, and separately supplied `REBOLT_ROOT` / `REBOLT_PYTHON` for LocalRetro. The latter requires compatible model assets. `SRG_BACKEND_TIMEOUT_SECONDS` is a per-backend-call timeout, distinct from aggregate research budgets.

Never put API keys, profile authentication, private evaluator records or machine-specific absolute paths in versioned configuration. All LLM roles use the main/default Agent Scientist profile. Scientific model manifests/checkpoints are supplied separately and must retain their source, version and digest.

An offline replay from the environment root:

```sh
retrosynthesis replay --task examples/applications/inventory/task.json --science-config config/offline-science.json --actions examples/applications/inventory/actions.json --output artifacts/reproduction/inventory.json
```
