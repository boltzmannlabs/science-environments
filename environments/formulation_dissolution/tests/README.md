# Tests and reproducibility

The original 46-test suite is retained and extended with configuration/state, composition/unit/dose, numerical behavior, optimization/budget, fixed-seed, supplied-profile and end-to-end scenario regressions. All scientific examples in tests are synthetic contract objects, public identity fixtures or literature summaries. No real ranolazine measured-profile dataset has been evaluated.

From the environment directory:

```bash
python -m unittest discover -s tests -v
python -m pytest -q
```

Base Python explicitly skips six simulation-only tests. With `pip install -e '.[simulation,test]'`, all 97 tests execute. The actually tested environment is Python 3.14.7/Linux; see the current machine-generated [receipt](../results/validation.json), not historical test counts in old notebooks.

For a complete check, install build/Ruff as well, then run:

```bash
python scripts/check_release.py
```

It runs pytest/unittest, fatal-error lint (E9/F63/F7/F82), format-checks new integration code, dependency consistency, the actual bounded scenario and selection/negative control, six-model pipeline/verifier, fixture/abstention CLIs, and a wheel build/fresh isolated base-only install outside the source tree. It records actual command exit codes/output and versions; it does not create plausible test output. Optional `--source-run PATH` hashes originals read-only to generate copy provenance and a historical-run summary. New run assets go to ignored `.checks/`; the code wheel does not include data/config fixtures.

There is no repository-wide type-check contract. Full static typing and inherited-code reformatting are not claimed; new files are format-checked and all code receives fatal-error lint. The original baseline's compact formatting is preserved to keep scientific changes reviewable. Source identity attestations and lab approval fixtures are not authentication of real controlled documents or lab authority.
