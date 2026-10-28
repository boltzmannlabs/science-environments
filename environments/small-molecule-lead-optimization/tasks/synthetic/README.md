# Runnable synthetic software example

All candidate representations and scores in this example are invented. `synthetic:lead` and similar strings are opaque fixture labels, not chemical structures or valid SMILES. The example exercises the environment without a scientific service, model, GPU or account.

From the environment directory:

```bash
python3 scripts/run_synthetic.py --output /absolute/new/synthetic-run
```

The destination must not exist. The run writes a SQLite campaign, advisory check, report, frozen submission, digest receipt and evaluator output. It records an artificial submission counter of one while making **zero real scientific submissions**. `candidate-a` improves the artificial search score from 2 to 4 and the artificial final score from 2 to 3; `candidate-b` fails the example floor. These values have no biological meaning.

Inputs are [task.json](task.json), [candidates.json](candidates.json) and [observations.json](observations.json). Final rules are preregistered in the task. The artificial reference labels in [tests/synthetic-reference.json](../../tests/synthetic-reference.json) are public software fixtures, not hidden benchmark answers. The example validates the evaluator interface and makes no isolation claim.

The normal agent uses the installed plugin and its skill. This script is a deterministic maintainer reproduction, not a replacement agent loop or a scientific baseline.

For real independent evaluation, retain the submission digest and reference file outside the tested agent's access. The offline command is:

```bash
leadopt-env evaluate --submission /evaluator/submission.json \
  --reference /evaluator/reference.json --expected-digest RETAINED_DIGEST
```

The expected digest must come from the separately retained submission receipt. A checksum cannot authenticate source measurements or prevent the agent reading files to which its host gives access.
