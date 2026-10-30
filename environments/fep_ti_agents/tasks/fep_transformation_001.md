# Task: fep_transformation_001

**Task family:** Free Energy Perturbation  
**Module:** FEP/TI  
**Agent:** FEP-AG02 Transformation Feasibility Auditor  
**Status:** implemented and tested

## Description

Assess whether the mapped ligand-A to ligand-B transformation is chemically
and computationally suitable for an alchemical calculation. The auditor checks
endpoint atom identity, mapped heavy-atom coverage, bond changes, net charge,
protonation/tautomer metadata, and declared force-field support.

## Exact inputs

The valid fixture is under `tasks/inputs/fep_transformation_001/` and reuses
the immutable MOL2 endpoints and atom map from `fep_atom_mapping_001`:

- `transformation.json` — endpoint metadata and allowed elements.
- `../fep_atom_mapping_001/ligand_a.mol2` — ligand A.
- `../fep_atom_mapping_001/ligand_b.mol2` — ligand B.
- `../fep_atom_mapping_001/atom_map.json` — supplied atom correspondence.

## Execution

```bash
python scripts/validate_transformation.py \
  tasks/inputs/fep_transformation_001/transformation.json \
  --output-dir results/fep_transformation_001
```

## Expected outputs

- `transformation_assessment.json`
- `chemical_changes.csv`
- `feasibility_report.md`
- `qualification.json`

The supplied fixture returns `PASS` with one diagnostic bond-order change and
zero net charge change. A charge-changing, protonation-changing, unsupported,
or malformed variant must return `REVIEW` or `FAIL`, never an unqualified PASS.

## Constraints

Inputs are immutable. The auditor must not repair atom maps, change protonation,
invent parameters, or silently change the force field. A warning means a
scientific decision or additional protocol is required before production FEP.
