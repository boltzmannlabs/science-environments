# Technical validation

Run from the environment directory:

```bash
python3 -B tests/run_validation.py --scratch /absolute/approved/scratch
```

Optional read-only verification of expected originating case summaries/receipts:

```bash
python3 -B tests/run_validation.py --scratch /absolute/approved/scratch --evidence-root /absolute/approved/KRAS_siRNA_case_study
```

Use `--tag python313` to record another interpreter without overwriting the default receipt/logs. The runner executes the environment tests, bundled original helper tests, project structure, skill payload integrity, frozen KRAS benchmark-snapshot integrity and an intentional missing-configuration blocker. It writes actual return codes, command logs and `results/validation_receipt[.tag].json`.

The software fixtures are explicitly NOT biological targets, measurements, model outputs or proposed siRNAs. The default tests do not need original case data, GPU, a network, models or a SCI installation. Optional historical verification reads only the expected small summary/receipt files and selected aggregates; no original verifier or scientific pipeline is executed.

`seal_contribution.py` validates final receipts, local links, JSON, payload size and allowed changed paths, then writes the small contribution output manifest and verification receipt. It also records unrelated tracked-file preservation. Do not interpret any technical receipt as whole-environment scientific or biological validation.
