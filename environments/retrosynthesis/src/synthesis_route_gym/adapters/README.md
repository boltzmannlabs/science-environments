# Synthesis tool adapters

All adapter prediction outputs carry `evidence_status: predicted`. A score is the
upstream model score, not a calibrated probability of chemical feasibility.

## Existing LocalRetro

```python
from synthesis_route_gym.adapters import LocalRetroAdapter

adapter = LocalRetroAdapter(
    repo_root="/path/to/REBOLT-FEATURES",
    python_executable="/path/to/mol_gpu/bin/python",
    timeout_seconds=60,
)
result = adapter.expand("CC(=O)Oc1ccccc1C(=O)O", top_k=5)
```

`REBOLT_ROOT` and `REBOLT_PYTHON` supply defaults. The existing
`rebolt_update_opt/localretro` source is selected because its DGL edge extraction
works with the available Torch/DGL environment. Each bounded subprocess performs
CPU inference, runs offline, and reports the checkpoint SHA-256. A timeout kills
the subprocess process group. No cloud jobs are created.

```bash
python -m synthesis_route_gym.adapters localretro 'CC(=O)Oc1ccccc1C(=O)O' \
  --repo-root /path/to/REBOLT-FEATURES --python /path/to/mol_gpu/bin/python
```

The actual local inference receipt is `artifacts/adapters/localretro_smoke.json`.
This is a connectivity/inference check, not a chemical feasibility benchmark.

## AiZynthFinder

```python
from synthesis_route_gym.adapters import AiZynthFinderAdapter

adapter = AiZynthFinderAdapter(
    config_path="/path/to/frozen_config.yml",
    python_executable="/path/to/aizynth/bin/python",
    expansion_policy="uspto",
    stock_names=("benchmark_inventory",),
)
expansion = adapter.expand("CCO")
routes = adapter.search("CCO", max_iterations=100, max_transforms=6)
```

Models, stock, and the Python package must already be available. Missing assets
return `status: unavailable`; there is no substitute algorithm. The API follows
the [official Python interface](https://molecularai.github.io/aizynthfinder/python_interface.html).
Returned route trees preserve upstream stock flags, which do not establish
chemical feasibility. The environment must independently check its inventory.

`normalise_aizynth_route(tree, route_id, source_version)` converts one tree into
the gym's `RouteCandidate` dictionary. It rejects malformed trees and cycles,
preserves all precursor obligations, and leaves quantities, conditions, and
experimental evidence unknown. Upstream `in_stock` flags do not override the
gym's inventory assessor.

The reproducible official-model baseline is:

```bash
python -m venv .venv-aizynth
.venv-aizynth/bin/pip install aizynthfinder==4.4.1 pyarrow==20.0.0
PYTHONPATH=src .venv/bin/python scripts/run_aizynth_baseline.py --download
```

The PyArrow pin avoids the current PyArrow 26 / AiZynthFinder NumPy 1.x
dependency conflict. This optional environment is independent of Agent
Scientist. The script verifies the published checksums of two official public
USPTO assets (about 95 MB total), creates a four-material inventory, and runs
both AiZynthFinder and LocalRetro on the same aspirin target with one root
expansion, five proposed transformations, one preparative step, and a 60-second
per-method wall cap. It records inventory closure separately from feasibility.
This single-target baseline is a smoke experiment, not an agent comparison.

The recorded local run used AiZynthFinder 4.4.1 with its official USPTO ONNX
policy. One MCTS iteration made one expansion call and returned one inventory
closed, one-step candidate plus an unclosed root-only candidate. LocalRetro
returned four one-step candidates, three with declared precursors in inventory.
Full elapsed times including process/model startup were approximately 2.62 and
7.71 seconds, respectively. No candidate has independent chemical review;
quantities and operating conditions remain unknown. See
`artifacts/adapters/aizynth_baseline/report.json` for raw trees, normalized
routes, separate assessments, budgets, checksums, and limitations.

## Registered platform tools

```python
from model_tools import handle_function_call
from synthesis_route_gym.adapters import RegisteredPlatformAdapter

adapter = RegisteredPlatformAdapter(dispatch=handle_function_call)
receipt = adapter.submit("CCO", experiment_name="synthesis-route-gym-example")
status = adapter.status(receipt["job"]["doc_id"])
```

These methods call `boltzmann_submit` and `boltzmann_status` through Agent
Scientist's existing dispatcher. Its authentication and tool policy remain in
charge. Public submission uses `target_mol` and `outname`; custom inventory is
not a verified public submission parameter. Neither a receipt nor a completed
job is converted into a validated route. The host must retrieve and validate
the completed result through its registered artifact tools before consuming it.

## Verification

```bash
python -m pytest tests/test_adapters.py --cov=synthesis_route_gym.adapters \
  --cov-report=term-missing --cov-fail-under=80
```

Tests cover malformed molecules, stereo preservation, unavailable tools, bounded
subprocesses, sanitized errors, platform receipts, configuration propagation,
and adapter contract translation. Heavy-model behavior is mocked in unit tests;
the LocalRetro smoke receipt records actual inference separately.
