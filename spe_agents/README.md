# Boltzmann Labs SPE Agent Environments

This standalone folder defines 18 active specialist Single-Point Energy agent environments. They share one registry, prompt builder, evidence evaluator, input/structure validation boundary, and versioned SPE adapter protocol. The environments are scientific task contracts—not 18 separate quantum-chemistry engines or Python environments. Historical IDs 13 and 16 are retired and surviving IDs remain unchanged.

Every adapter starts as `unverified`. A contract may be used for planning and validation, but it must not be described as operational until its engine translation, failure handling, result parsing, provenance, and environment-specific tests have passed.

The illustrated program plan is available as [Boltzmann_Labs_SPE_Agent_Implementation_Plan.docx](docs/Boltzmann_Labs_SPE_Agent_Implementation_Plan.docx). Its project-local source and visual assets are in `docs/`.

The first static inventory of the committed legacy service is in
[LEGACY_ENGINE_CAPABILITY_INVENTORY.md](docs/LEGACY_ENGINE_CAPABILITY_INVENTORY.md).
It deliberately keeps the service `unverified` until live capability and
scientific smoke tests exist.

The executable validation campaign, deterministic fixtures, active 54-case manifest,
and filled prompts are documented in [campaign/README.md](campaign/README.md).
The latest qualification summary is in
[summary.md](reports/qualification_v2/summary.md).
The first live GPU execution evidence is in
[agent_01_smoke_summary.md](reports/live_spe_module/agent_01_smoke_summary.md).
The controlled fixed-workflow versus Agent Scientist benchmark is specified in
[BENCHMARK_SPEC.md](benchmark/spe_v1/BENCHMARK_SPEC.md). It uses the same local
Boltzmann SPE adapter for every approach, hides frozen references from decision
makers, and scores outputs with an independent evaluator. The first measured
development and held-out comparison is summarized in
[summary.md](reports/spe_benchmark_v1/summary.md).

The failure-focused successor is specified in
[SPE Benchmark v2.1](benchmark/spe_v2/BENCHMARK_SPEC.md). It preserves v1,
adds failure-class scoring and repeated held-out runs, supplies the relevant
18-environment specialist context only to the specialist arm, and keeps its
[independent accuracy track](benchmark/spe_v2/accuracy_track.json) outside the
primary reliability gate. Measured results and interpretation are in the
[v2.1 summary](reports/spe_benchmark_v2/summary.md).

The next specialist-value milestone is frozen in the
[18-agent qualification matrix](reports/specialist_qualification_v1/qualification_matrix.md)
and its [protocol](benchmark/specialist_qualification_v1/PROTOCOL.md). It defines
54 held-out scenarios and keeps execution qualification separate from measured
incremental value. The concise evidence status is in the
[specialist qualification summary](reports/specialist_qualification_v1/summary.md).

Batch 1 has now executed the matched specialist-on/off comparison for Agents
01, 03, 04, 05, 06, 07, 08, and 14. The scientifically corrected, response-
preserving result is in the [Batch 1 v1.1 report](reports/specialist_qualification_batch1/v1_1/summary.md),
and the consolidated current status is in the
[qualification matrix v2](reports/specialist_qualification_v2/qualification_matrix.md).

## Layout

```text
environments/<id>-<slug>/agent.json  # 18 active specialist scientific contracts
src/spe_agents/                      # standalone registry, router, prompts, evaluator, CLI
src/spe_agents/adapters.py           # versioned adapter protocol and test-only mock
schemas/                             # shared task/result exchange contracts
tests/                               # contract, routing, prompt, and evaluator tests
BASE_AGENT_INSTRUCTIONS.md           # safety and execution rules shared by all agents
ENVIRONMENTS.md                      # catalog and implementation order
```

## Use

From this `spe` directory:

```bash
PYTHONPATH=src python -m spe_agents.cli validate
PYTHONPATH=src python -m spe_agents.cli list
PYTHONPATH=src python -m spe_agents.cli show 10
PYTHONPATH=src python -m spe_agents.cli route "compare conformer energies"
PYTHONPATH=src python -m spe_agents.cli prompt 20
python -m unittest discover -s tests -v
python scripts/run_initial_campaign.py
python scripts/run_live_spe_module_smoke.py
python scripts/build_specialist_qualification_matrix.py --project-root .
PYTHONPATH=src python -m spe_agents.benchmarking.cli \
  --output reports/spe_benchmark_v1/development \
  --split development \
  --approaches all \
  --decision-command "python scripts/agent_scientist_spe_decision_bridge.py"
```

Or install it independently:

```bash
python -m pip install -e .
spe-agents validate
spe-benchmark --help
```

## Architecture boundary

The shared runtime loads and routes contracts and evaluates explicit evidence. `tool_adapters` name intended integrations such as `boltzmann-spe-api`; they do not assert that those services are installed or scientifically validated. Execution belongs behind adapter interfaces so one engine can serve many environments while each specialist retains its own input rules, outputs, warnings, acceptance criteria, and recovery policy.

The adapter protocol is currently `1.0`. It covers machine-readable capabilities,
pre-submission capability checks, normalized request fingerprints, submission,
status, cancellation, structured results, artifacts, and classified failures.
`MockSPEAdapter` is deliberately test-only: every result or failure must be
scripted explicitly, so it cannot be mistaken for a calculation engine.
