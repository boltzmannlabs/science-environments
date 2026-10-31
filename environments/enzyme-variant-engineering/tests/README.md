# Scientific task checks

The [BglB acceptance plan](bglb-activity-stability/ACCEPTANCE.md) defines what its
design outputs mean and how they are compared with the published reference.
`evaluate.py` evaluates a saved shortlist; it does not prepare molecular-tool
requests, execute jobs, train a predictor or replace native input validation.

From this environment directory:

```bash
python3 -m unittest discover -s tests/bglb-activity-stability -p 'test_*.py' -v
```

For optional native-definition compatibility, use the Python environment belonging
to the installed Agent-Scientist, supplying its source path:

```bash
python3 tests/bglb-activity-stability/check_native.py --sci-source /path/to/Agent-Scientist
```

That path is installation-specific. This check calls the original native
`Specialist.parse` and does not create a profile, enable a specialist, invoke a
model or submit a scientific job. Core Python unit tests use only the standard
library; they do not require SCI or a GPU.

Software-check results are not activity predictions or successful live-agent runs.
Adding a case means adding its own scientific acceptance criteria and only the
evaluation code it actually needs, not copying a general execution framework.
