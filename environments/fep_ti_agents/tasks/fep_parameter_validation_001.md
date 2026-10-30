# Task: fep_parameter_validation_001

**Task family:** Free Energy Perturbation  
**Module:** FEP/TI  
**Agent:** FEP-AG03 Force-Field and Parameter Auditor  
**Status:** implemented and tested

## Description

Validate that every atom and bond in a frozen FEP system has a supported atom
type, charge, and bonded parameter, and that the declared water/ion models are
compatible with the selected force-field inventory.

## Exact inputs

- `tasks/inputs/fep_parameter_validation_001/system.json`
- `tasks/inputs/fep_parameter_validation_001/forcefield.json`

## Execution

```bash
python scripts/validate_parameters.py \
  tasks/inputs/fep_parameter_validation_001/system.json \
  tasks/inputs/fep_parameter_validation_001/forcefield.json \
  --output-dir results/fep_parameter_validation_001
```

## Expected outputs

`parameter_validation.json`, `missing_parameters.csv`, `charge_audit.json`,
`topology_validation_report.md`, and `qualification.json`.

Valid inputs return `PASS`; missing types, bonded terms, count mismatches, or
incompatible solvent models return `FAIL` or `REVIEW`. The validator never
invents parameters or changes frozen files.
