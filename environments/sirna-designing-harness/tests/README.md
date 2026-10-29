# Technical validation and reproduction

From the environment directory:

```bash
python3 -B tests/run_validation.py --scratch /absolute/approved/scratch
```

A second available interpreter can use `--tag python313` to retain separate receipts/logs. Optional approved original-case checks:

```bash
python3 -B tests/run_validation.py \
  --scratch /absolute/approved/scratch \
  --evidence-root /absolute/approved/KRAS_siRNA_case_study
```

The runner executes environment tests, dedicated technical-report tests, original helper tests, project checks, skill integrity, old/new snapshot checks and the actual technical-report CLI. It also exercises the intentionally incomplete deployment template. Current counts are in [STATUS.md](../STATUS.md) and the actual receipts, not inferred from file presence. Implementation/config/task hashes bind the exact tested revision.

Dedicated tests are also runnable alone:

```bash
python3 -B tests/test_technical_reporting.py --scratch /absolute/approved/scratch
python3 -B scripts/run.py verify-technical-case
python3 -B scripts/run.py technical-report \
  --bundle results/case_studies/KRAS_14_technical_validation/bundle.json \
  --out /absolute/path/to/NEW-report-directory
```

Negative mutations are marked `SOFTWARE_FIXTURE_NOT_SCIENTIFIC_RESULT`. They test refusal/blocking behavior, not new biological designs or invented experimental results. The real recorded positive case is separately labelled. Test fixtures and CLI replay outputs go to the chosen scratch directory; original evidence is never overwritten. Reusing an existing report destination must fail.

The default tests need no GPU, model installation, network, SCI installation or original source root. The optional history command reads expected small summary/receipt files; no old verifier or scientific pipeline is executed.

After all writers finish:

```bash
python3 -B tests/seal_contribution.py
python3 -B tests/seal_contribution.py --verify-only
```

Sealing requires both passing current test receipts, unchanged tested implementation/config/task hashes, valid report/recorded-case bindings, the focused feature branch, allowed changed paths, no staging, payload bounds and intact original skill/benchmark evidence. It records the portable technical milestone and pending governance separately. Historical receipts remain under `results/history/`.
