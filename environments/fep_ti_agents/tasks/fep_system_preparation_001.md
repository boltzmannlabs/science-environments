# Task: fep_system_preparation_001

**Task family:** Free Energy Perturbation  
**Module:** FEP/TI  
**Agent:** FEP-AG05 System Preparation and Equilibration Auditor  
**Status:** implemented and tested

## Description

Validate complex and solvent systems before production FEP. The auditor checks
topology/coordinate counts, periodic boxes, charge neutralization, minimization,
and NVT/NPT stability against frozen thresholds. It returns a production
readiness decision without modifying inputs.

## Exact input

`tasks/inputs/fep_system_preparation_001/sampl6_oa_systems.json` contains the
SAMPL6 OA-G3 complex and solvent legs, source revision, atom counts, box sizes,
minimization evidence, and equilibration metrics.

## Execution

```bash
python scripts/validate_system_preparation.py \
  tasks/inputs/fep_system_preparation_001/sampl6_oa_systems.json \
  --output-dir results/fep_system_preparation_001
```

## Expected output

- `complex_preparation_report.md`
- `solvent_preparation_report.md`
- `equilibration_metrics.json`
- `production_readiness.json`

Valid legs return `PASS`. Count mismatch, invalid box, non-neutralized input,
failed minimization, incomplete NVT/NPT, or unstable metrics return `FAIL` or
`REVIEW`. A successful parser load alone is not production readiness.
