# Repository Architecture

Scientific environments live under `environments/<environment-name>/`.
Each environment owns its specification, references, task packets, tests,
configuration, and small versioned result summaries.

The current environments are:

- `environments/spe_agents/` — single-point-energy specialist workflows.
- `environments/geo_opt_agents/` — geometry-optimisation specialist workflows.

Benchmark reports and raw artifacts remain inside the environment that produced
them. Repository-wide policies belong in `docs/`. Large generated datasets,
credentials, and restricted data are excluded.
