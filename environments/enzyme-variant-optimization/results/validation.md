# Package validation

**Checked on 27 October 2026, using Python 3.12.12 on Linux.** These results describe the release checkout and its artificial examples. They do not include the ongoing scientific pipelines.

| Check | Result | What it establishes |
| --- | --- | --- |
| Portable test suite | **380 passed; 0 failed; 0 skipped** | The packaged environment handles the tested tasks, candidates, file transfers, results, and failures. |
| Suite with optional native support | **386 passed; 0 failed; 0 skipped** | Includes six additional scripted tests of role context and host-failure reporting. |
| Installed package | **Passed** | A fresh virtual environment installed the built wheel and ran its CLI. |
| Installed research example | **Passed** | Actual pinned DiscoveryRSI code changed the next investigation using a synthetic result and recovered saved state after reopening. |
| Installed executor example | **Passed** | A mock quality step retained one of two candidates, and the next property step received that candidate. |
| Synthetic task creator | **Passed** | Created a toy structure with a matching hash and started local base-arm state. |
| Python dependency consistency | **Passed** | `pip check` reported no broken requirements in the test environment. |

The package check made **zero model requests, zero scientific service submissions, and zero GPU calls**. Initial dependency installation is separate from the network-free wheel installation check. The optional native-support tests used supplied host-support source with scripted responses; they do not show a live Agent-Scientist model episode or scientific campaign.

## Repeat the checks

Follow the environment README to install the locked test dependencies and pinned DiscoveryRSI source, then run:

```bash
.venv/bin/python -m pytest -q
.venv/bin/python scripts/run_offline.py --output .runs/my-example
.venv/bin/python scripts/check_package.py --upstream .runtime/DiscoveryRSI --output .checks/my-package
.venv/bin/python scripts/check_release.py
.venv/bin/python -m pip check
```

Use a new output directory for each example/package check. The optional test command, for an operator with the separately supplied support modules, is:

```bash
.venv/bin/python -m pytest -c pyproject.toml tests -q --native-support=/absolute/path/to/native-support/src
```

The exact test counts, dependency versions, source revision, and wheel hash for this check are in [validation.json](validation.json). Generated local reports, virtual environments, source checkouts, and test state are ignored by Git.

## What remains to be established

Live tool completion, final ligand/geometry handling on real structures, and the matched scientific comparison require their own evidence. These tests do not measure whether the specialist produces better enzymes than a fixed workflow or the base agent. Native support distribution, license selection, and maintainer review are still required for release readiness.
