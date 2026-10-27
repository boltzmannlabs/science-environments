# Enzyme Variant Optimization

**Status: In Progress. The offline package works; the live scientific comparison is still being completed.**

This environment helps Agent-Scientist improve an existing enzyme by studying changes to its amino-acid sequence. Each proposed sequence is a **candidate variant**. The environment keeps that candidate's sequence, structures, tool results, and design history together, so later decisions can use the correct evidence.

The work can start with new computational designs or a supplied list of variants that have experimental measurements. In the second case, the agent sees the sequences while a separate evaluator keeps the test measurements hidden.

| Component | What it does |
| --- | --- |
| Agent-Scientist | Plans the overall task and uses the available scientific tools. |
| This environment | Records candidates and jobs, prepares inputs, checks returned files, and connects results to the correct candidates. |
| Enzyme specialist | Proposes an investigation, reviews it through a separate critic call, and uses the results to suggest the next step. |

The specialist uses the existing language model and tools. It does not contain a newly trained enzyme model. Whether its extra review improves candidate selection, reliability, or efficiency must be measured in the benchmark.

## What is included

- `src/enzyme_research/`: the task rules, saved experiment records, input preparation, tool connections, result checks, reports, and specialist code.
- `src/enzyme_research/_support/enzyme_workflow/`: a copy of our existing workflow executor for offline examples and tests. It does not install a second top-level `enzyme_workflow` plugin.
- `tasks/`: the input format and a runnable example made with artificial test data.
- `config/`: example configuration without account credentials.
- `tests/`: checks for input handling, result matching, failure handling, and saved-state recovery.
- `scripts/`: commands to prepare dependencies, run the example, and test a fresh package installation.
- `results/`: short reports of the checks actually completed.

The specification is [ENVIRONMENT_SPEC.md](ENVIRONMENT_SPEC.md). Implementation maturity and limitations are in [STATUS.md](STATUS.md). Scientific context is in the matching [research notes](../../research/enzyme-variant-optimization/research-notes.md) and [references](../../research/enzyme-variant-optimization/references.md).

## Run the offline example

Requirements: Linux or another system with Python 3.12+, Git, and network access for the initial dependency installation. Subsequent demonstrations use only local files. No account, GPU, model weights, or paid scientific jobs are needed for this example.

From this environment's directory:

```bash
python3.12 -m venv .venv
.venv/bin/python -m pip install -r config/offline-test.lock
.venv/bin/python -m pip install --no-deps --no-build-isolation -e .
.venv/bin/python scripts/fetch_discovery.py
.venv/bin/python -m pytest -q
.venv/bin/python scripts/run_offline.py --output .runs/first-example
```

The dependency helper clones public DiscoveryRSI at revision `7389e0b58ae50486ab35aa3dcbfa2fa15fea1a91` into ignored `.runtime/`. It refuses to change an existing different or dirty checkout. A caller can select an existing checkout using `--destination`; tests use `ENZYME_DISCOVERY_SOURCE` when supplied.

The example uses artificial data to exercise the actual research and workflow code. A supplied result reports poor stability; the next recorded investigation changes from activity to stability. A second example rejects one candidate after a mock quality check and forwards the other to a property step. Expected report fields include `success: true`, `synthetic_only: true`, zero remote submissions, and zero model requests. The test coordinates and scores are artificial. Use a new output directory for another run.

The basic installed command is also available:

```bash
.venv/bin/enzyme-research demo --upstream .runtime/DiscoveryRSI --output .runs/core-example
.venv/bin/python scripts/check_package.py --upstream .runtime/DiscoveryRSI --output .checks/package
```

The package check builds a wheel, which is Python's installable package file. It installs that wheel into a fresh virtual environment and runs the example from outside the source folder. This checks that required code and support files were included.

## Use with Agent-Scientist

The plugin provides four operations: `enzyme_research_start`, `enzyme_research_next`, `enzyme_research_status`, and `enzyme_research_report`. The [enzyme-research skill](src/enzyme_research/skills/enzyme-research/SKILL.md) explains their use. A task runs in one of three modes: `fixed` follows a predefined workflow; `base` lets Agent-Scientist choose its actions; `specialist` adds the dedicated proposer and critic. All use the same candidate-tracking and execution rules.

To run actual Agent-Scientist model calls and remote scientific jobs, an operator also needs:

1. An installed, authorized Agent-Scientist runtime and its canonical Boltzmann tool catalogue.
2. Absolute paths to a clean, revision-pinned Agent-Scientist checkout, its Python executable, and the user's existing profile. Credentials remain in that profile.
3. The separate `enzyme_environment` and `enzyme_benchmark` support modules used by `native_episode.py`. They connect the agent to the host model and limit what the tested process can access. Their public installation path is still to be prepared. This execution mode requires Linux and bubblewrap.
4. A configured `research_runtime` value, based on [config/runtime.example.json](config/runtime.example.json), and a reviewed real task with working scientific tool bindings.

The optional `tests/native/` checks use scripted responses to test the proposer/critic context and host-failure reports. They need those separate support modules, so they are outside the default test command. An operator who has both modules can run `python -m pytest -c pyproject.toml tests -q --native-support=/absolute/path/to/native-support/src`. These tests do not make real model or scientific-service requests.

The `workflow_source` setting selects the executor actually used by that process. If Agent-Scientist already loaded its executor, configure that existing source. Do not mix that loaded implementation with the bundled snapshot. The environment reads tool request schemas from the canonical catalogue rather than copying a second catalogue of input fields. Tool deployment and scientific outputs remain external dependencies.

All listed tools use the current catalogue for their job names and availability, including the five newly deployed enzyme tools. No second activation step is needed. Input preparation now supports one PDB for EnzyControl or DeepAllo, and one PDB/CIF for RFD3, preserving the selected file's atoms and residue labels. Other required settings are supplied according to each tool's current contract. The dated [catalogue check](results/catalogue-check.json) records the exact Agent-Scientist revision and contracts inspected for this package update.

The live contract currently requires an explicit `seed` for EnzyControl. Catalytic Geometry takes uploaded JSON paths for both `reaction_template` and `template_binding`; its API requires the binding file. These API requirements differ from some local-worker options, so follow the current catalogue when submitting requests.

The command-line `start` operation creates a local experiment record. Running a live investigation also needs the configured host to supply the model calls. The four registered plugin operations alone do not complete this setup. No changes to Agent-Scientist core source are required.

## Scope and evidence

This contribution focuses on variants of an existing enzyme. When a benchmark supplies a fixed list of measured variants, the agent must choose from that list. Newly generated sequences cannot be assigned experimental scores that do not exist. Structure prediction, preparation, and docking use external tools. Creating a new enzyme from scratch requires a separate task and evaluation design.

The offline tests show whether the software behaves as expected. To establish whether the specialist improves enzyme results, compare the fixed workflow, base agent, and specialist under the same task and resource limits. Define the evaluation rules before the runs and score them using independent measurements in `science-benchmarking`. The ongoing pipelines are separate from this package's test report.

The repository's [license selection](../../LICENSE) is pending. See [THIRD_PARTY_NOTICES.md](THIRD_PARTY_NOTICES.md) before public distribution.
