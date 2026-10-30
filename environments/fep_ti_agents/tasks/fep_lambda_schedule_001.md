# Task: fep_lambda_schedule_001

**Task family:** Free Energy Perturbation  
**Module:** FEP/TI  
**Agent:** FEP-AG04 Lambda Schedule Optimizer  
**Status:** implemented and tested

## Description

Validate a supplied electrostatic/steric lambda schedule before expensive FEP
sampling. The auditor checks endpoint coverage, ordering, duplicates, adjacent
gaps, charge-changing staging, and soft-core settings. Recommendations are
reported separately; the frozen schedule is never silently changed.

## Exact input

`tasks/inputs/fep_lambda_schedule_001/transformation.json`

## Execution

```bash
python scripts/validate_lambda_schedule.py \
  tasks/inputs/fep_lambda_schedule_001/transformation.json \
  --output-dir results/fep_lambda_schedule_001
```

## Expected output

`lambda_schedule.json`, `lambda_validation.json`,
`schedule_recommendations.md`, `window_configuration/`, and `qualification.json`.

The baseline returns `PASS`. Duplicate, out-of-order, endpoint-incomplete,
large-gap, invalid-softcore, and charge-change cases return `FAIL` or `REVIEW`.
