# Local delivery and reproducibility

This historical delivery record includes commands and references for local research assets, including `examples/portfolio/` and `artifacts/`, which are not bundled in this source release. Those commands require the original archived inputs. Use the current [environment README](../README.md) for portable installation and executable examples, and [validation status](../results/README.md) for the repository migration checks.

This guide covers package **0.1.0**, task contract **1.0**, and local Agent Scientist plugin **0.1.0**. Paths are relative to the package root unless stated otherwise. Recorded artifacts support only the specific runs they contain; write new runs to separate output directories.

## Architecture and actions

A task pins target identity, inventory, constraints, evidence records, and budget. `SynthesisRouteEnv` maintains routes, revisions, submissions, and a chained event log. Adapters return predictions with source versions. A separate evaluator reads hidden outcomes or independent review records after decisions are saved.

| Action | Behavior |
|---|---|
| `inspect` | Return task, routes, and resource state. |
| `expand` | Request bounded precursor proposals from the configured scientific adapter. |
| `propose_route` | Store a route with a new identifier and optional revision-parent identifier; return deterministic findings. |
| `validate` | Check target identity, precursor obligations, inventory, constraints, supplied quantities, and evidence matching. |
| `predict_conditions` | Run the configured condition-yield model on explicit chemical-role inputs within its declared domain. |
| `rank_routes` | Compare stored routes using deterministic gates and declared surrogate utility; preserve missing yields. |
| `submit` | Record a bounded ranked shortlist, including an empty shortlist if needed. |

`reset` belongs to the host. Agents cannot reset an episode to recover budget. Failed and invalid actions consume the shared allowance. Submission acceptance covers deterministic checks, not experimental success. Conditions and model-assisted ranking require a host-supplied `ConditionRanker`; an unavailable model is reported explicitly.

See [schemas.py](../src/synthesis_route_gym/schemas.py), [environment.py](../src/synthesis_route_gym/environment.py), [validation.py](../src/synthesis_route_gym/validation.py), [planning.py](../src/synthesis_route_gym/planning.py), and [benchmark.py](../src/synthesis_route_gym/benchmark.py).

The local Small Molecule handoff accepts candidate identity, source job/tool provenance, inventory, and constraints through `SmallMoleculeHandoff` in [api.py](../src/synthesis_route_gym/api.py). Tests establish the contract behavior; cross-pod performance gains remain unproven.

## Agent Scientist and model restriction

[agent_runner.py](../src/synthesis_route_gym/agent_runner.py) resolves `model.default` and `model.provider` directly from the main profile's `config.yaml`. It does not follow a different active profile. Main, strategist, condition scientist, critic, and automated review sessions all use that resolved LLM. Alternate-model fallback and extra context-compression model calls are disabled in this benchmark runner.

The recorded model is `gpt-6-sol`, provider `openai-codex`. This is a receipt of the present configuration, not a replacement configuration. The new condition-yield model and existing chemistry checkpoints are scientific tools, separate from the LLM roles.

[agent_bridge.py](../src/synthesis_route_gym/agent_bridge.py) keeps chemistry and Agent Scientist interpreters separate. It gives the research agent only allowed environment tools. Hidden outcomes, arbitrary file reads, terminal execution, and web retrieval are not attached as agent capabilities. Calls and token reservations share one ledger across specialists. Confirmed usage settles matching reservations; unmatched reservations remain charged conservatively. Admission can stop even when reported provider tokens remain below the nominal cap.

The [plugin manifest](../integrations/agent_scientist/plugin.yaml) registers `srg_action`. Standalone execution requires chemistry libraries in that interpreter; the verified benchmark route here uses the bridge. With the environment variables from the [README](../README.md), verify discovery without an LLM call:

```sh
"$SRG_SCIENTIST_PYTHON" integrations/agent_scientist/verify_discovery.py \
  --scientist-source "$SRG_SCIENTIST_SOURCE"
```

Credentials remain in Agent Scientist's normal profile. Do not copy them into task files or artifacts.

## Reproduce the scientific model and decision test

```sh
export SRG_DOYLE_DATA=/home/boltzmann6/server3_data/boltzmann3/anaconda3/lib/python3.13/site-packages/gauche/datasets/reactions/DreherDoyle.csv

OMP_NUM_THREADS=2 OPENBLAS_NUM_THREADS=2 MKL_NUM_THREADS=2 \
.venv/bin/python scripts/train_condition_ranker.py \
  --dataset "$SRG_DOYLE_DATA" --output artifacts/reproduction/model

.venv/bin/python scripts/run_heldout_route_benchmark.py \
  --dataset "$SRG_DOYLE_DATA" --model-dir artifacts/reproduction/model \
  --output artifacts/reproduction/route_decisions
```

The original experiment is [Ahneman et al., Science (2018)](https://doi.org/10.1126/science.aar5169); its machine-readable table is distributed with [GAUCHE](https://github.com/leojklarner/gauche/blob/main/gauche/datasets/reactions/DreherDoyle.csv). The frozen [protocol](../artifacts/model/protocol.json) records data identity and split assignments. Product grouping keeps halide variants producing the same product together. Model selection used validation data. The final test has one product family and three correlated substrate variants; scaffold independence is not claimed.

The [provenance reconciliation](../artifacts/model/provenance_reconciliation.json) verifies that all 3,955 local records exactly match the pinned upstream records in the same order. The byte-level hash difference is solely CRLF versus LF line endings; neither the frozen dataset nor the model was rewritten.

The learned ExtraTrees yield predictor is exported as numeric JSON and loaded through [ConditionRanker](../src/synthesis_route_gym/ranking.py), without executable pickle loading. Bands are descriptive validation-residual bands with no calibrated coverage guarantee. Route utility is a documented heuristic using predictions and missingness, not a learned route-success probability.

| Recorded held-out measure | Learned predictor | Training condition-mean baseline |
|---|---:|---:|
| Top-1 mean selected measured yield, % | 50.805 | 49.844 |
| Top-1 mean simple regret, percentage points | 12.109 | 13.069 |
| Best measured yield among top 5, mean % | 59.922 | 60.166 |
| Best measured yield among top 10, mean % | 60.545 | 62.581 |

The top-1 gain is **0.961 percentage points**. The baseline wins at top 5 and top 10. These narrow retrospective results support neither statistical-significance nor broad synthesis claims. The route-contract experiment reuses the same test and supplied recorded candidates; it does not measure discovery of new routes.

Attach the saved model with `--condition-model artifacts/model/condition_ranker.json` on `plan`, `agent`, or `replay`, or construct an environment explicitly:

```python
from synthesis_route_gym.environment import SynthesisRouteEnv
from synthesis_route_gym.ranking import ConditionRanker
from synthesis_route_gym.schemas import Task

model = ConditionRanker.load("artifacts/model/condition_ranker.json")
env = SynthesisRouteEnv(Task.model_validate(task_json), condition_ranker=model)
```

Inputs require `aryl halide`, `ligand`, `additive`, and `base`. Prose conditions and arbitrary reaction classes are not validated model inputs. See the [versioned model contract](../artifacts/model/tool-contract.v1.json).

## Reproduce the independent search baseline

```sh
python -m venv .venv-aizynth
.venv-aizynth/bin/python -m pip install aizynthfinder==4.4.1 pyarrow==20.0.0
.venv/bin/python scripts/run_aizynth_baseline.py --download \
  --aizynth-python .venv-aizynth/bin/python \
  --localretro-python "$REBOLT_PYTHON" \
  --output artifacts/reproduction/aizynth_baseline
```

This downloads approximately 95 MB of official model/template assets and verifies published checksums. The protocol permits one root expansion, up to five proposals, one step, and 60 seconds per method. It is an actual single-target smoke comparison with different generators, separate from the fixed/main/specialist comparison. Stock closure is reported separately from feasibility.

## Portfolio evidence

The [five-example runner](../examples/portfolio/run_examples.py) produces all application outputs. Its [guide](../examples/portfolio/README.md) distinguishes evidence kinds. Condition policies receive only condition identities and previously observed measurements, never hidden optima or outcome-sorted warm starts. The Python callback is not a sandbox against arbitrary untrusted code; the agent receives only tool observations.

Actual impurity inference is also available:

```python
from synthesis_route_gym.adapters.impurity_local import LocalImpurityAdapter

result = LocalImpurityAdapter(
    repo_root=repo_root,
    python_executable=chemistry_python,
    device="cpu",
    timeout_seconds=120,
).predict("CCOC(C)=O.O", "CCO", top_k=5)
```

The [live result](../artifacts/portfolio/impurity_live_ethyl_acetate.json) used the existing direct impurity T5 checkpoint. Several candidates are chemically questionable for this simple input. Training labels derive from multi-product proxies, and measured impurity truth is absent. Precision, recall, concentrations, and chemical validation remain unavailable. The [report](../artifacts/portfolio/impurity_live_report.json) retains this negative finding.

Biocatalytic retrieval uses [RHEA:58148](https://www.rhea-db.org/rhea/58148), with source locations and all products retained. Similarity matches remain analogues. A database transformation does not establish enzyme availability, conditions, yield, or a validated process. Process selection uses explicitly illustrative costs; missing costs never become zero.

## Recorded comparison and acceptance

The fixed/main/specialist aspirin task permits 80 actions, 12 expansions, 600 seconds, and top 3 submissions. Both LLM arms have the same 24-call and 200,000-token admission caps. These are equal resource allowances, not equal actual consumption.

| Recorded run | Submitted routes | Expansions | Environment elapsed seconds | LLM outcome |
|---|---:|---:|---:|---|
| [Fixed](../artifacts/local_fixed_aspirin.json) | 2 | 12 | 90.04 | No LLM |
| [Main v2](../artifacts/local_main_aspirin_v2.json) | 1 | 1 | 35.27 | Completed; 31,728 recorded tokens |
| [Specialists v2](../artifacts/local_specialists_aspirin_v2.json) | 0 | 2 | 98.82 | Stopped before submission; 98,624 recorded tokens |

These are execution counts for one target, not feasibility scores. The specialist trace records a strategist stage allocation stop and later main-session token-admission stop. Specialist benefit is unproven; use the main arm by default. Token telemetry and monetary cost are different quantities; no billing conclusion is drawn here.

| Requirement | Evidence and remaining gate |
|---|---|
| Interactive environment and route checks | Implemented with tests, inventories, revisions, limits, and event traces. |
| Existing tool reuse | Actual LocalRetro, AiZynthFinder, and impurity checkpoint inference receipts. |
| New scientific model | Held-out measured-data evaluation; narrow top-1 gain with top-5/top-10 losses retained. |
| Three-arm comparison | Actual one-target traces with matched caps; broader targets and repeated seeds remain necessary. |
| Independent chemical review | Six unique proposals reviewed individually in separate main-profile contexts: three source-supported transformations and three unresolved. All remain incomplete for laboratory execution; see the [case study](CASE_STUDY.md). |
| Five applications | All paths execute; measured validation is strongest for conditions. Impurity, cost, and biocatalytic limits remain explicit. |
| Small Molecule handoff | Local typed contract and tests; cross-pod gains unproven. |
| Reproducibility | Versioned inputs, hashes, traces, source records, tests, and run commands. |

Passing tests or returning a route does not establish scientific superiority. General multi-step improvement, reliable impurity prediction and quantitative process-cost benefit still require evidence. The requested review is an automated source audit in a separate context using the same main-profile model; it is not a human review or a statistically independent model assessment.

## One-week work sequence

| Day | Work and quality gate |
|---|---|
| 1 | Audit tools, checkpoint paths, main-profile model, and data; establish runnable fixed baseline. |
| 2 | Build task/state/action contracts, structural and inventory checks, budgets, and evidence labels; test failures first. |
| 3 | Freeze splits, train the scientific model, compare baselines, retain signed metric differences. |
| 4 | Connect five application paths and specialists; execute sourced examples and record missing evidence. |
| 5 | Run fixed/main/specialist comparisons with matched limits; retain timeouts, empty submissions, and regressions. |
| 6 | Review held-out outputs independently, check source correspondence, investigate model failures. |
| 7 | Reproduce the workflow, audit acceptance, and deliver code, manifests, results, and unresolved requirements. |

This is the requested week's work sequence, not a claim that every research gate has passed.

## Ownership and versioning

| Artifact | Version/source | Responsible role |
|---|---|---|
| Environment, validation, CLI | [pyproject.toml](../pyproject.toml), package 0.1.0 | Retrosynthesis environment maintainer; individual assignment pending |
| Main-profile runner and bridge | [runner](../src/synthesis_route_gym/agent_runner.py), [plugin manifest](../integrations/agent_scientist/plugin.yaml) | Agent Scientist integration maintainer; individual assignment pending |
| Scientific model | `doyle-condition-ranker-0.1.0`; [tool contract](../artifacts/model/tool-contract.v1.json) | Retrosynthesis pod ML maintainer; individual assignment pending |
| Data and independent review | [protocol](../artifacts/model/protocol.json), source locators, blinded fingerprints | Benchmark curator and independent chemistry reviewer; individual assignment pending |

Tests in `tests/` distinguish mocks from actual inference receipts. Run the complete suite with coverage using the README command; inspect its current result rather than treating an earlier test count as permanent. Preserve source/checkpoint hashes and version artifacts whenever data, models, schemas, or interpretations change.
