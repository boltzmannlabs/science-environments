# Task: fep_atom_mapping_001

**Task family:** Free Energy Perturbation  
**Module:** FEP/TI  
**Agent:** FEP-AG01 Alchemical Mapping Auditor  
**Status:** implemented on feature branch; scientific benchmark qualification pending

## Description

Validate the supplied atom correspondence for the SAMPL6 OA-G3 → OA-G6
relative transformation before any alchemical simulation is launched.

## Target and exact inputs

Inputs are under `tasks/inputs/fep_atom_mapping_001/`:

- `ligand_a.mol2` and `ligand_b.mol2`: frozen ligand heavy-atom fixtures.
- `atom_map.json`: supplied correspondence and immutability declaration.
- `transformation.json`: endpoint names, charges, benchmark and expected behavior.
- `expected_outputs.json`: machine-checkable acceptance requirements.

The upstream SAMPL6 source and revision are pinned in
`benchmarks/sampl6/manifest.json`. These small MOL2 files are a validation
fixture; they do not replace the upstream host/guest topology or production
trajectory files.

## Required execution steps

1. Parse both MOL2 files and reject malformed or empty structures.
2. Validate mapped atom IDs and one-to-one correspondence.
3. Compare mapped element identities.
4. Compare mapped bond pairs and report bond-order changes.
5. Report unmapped atoms and duplicate mappings.
6. Preserve input hashes and never silently rewrite the mapping.
7. Return `PASS`, `REVIEW`, or `FAIL` with machine-readable diagnostics.

Run:

```bash
python scripts/validate_atom_mapping.py \
  --input tasks/inputs/fep_atom_mapping_001 \
  --output results/fep_atom_mapping_001.json
```

## Expected output and acceptance

The valid fixture returns `PASS` while retaining expected bond-order changes
as diagnostics. Unknown atoms, duplicate mappings, or element mismatches
return `FAIL`; incomplete mappings return `REVIEW`. The output must include
input SHA-256 hashes and `silent_repair: false`.

The downloaded SAMPL6 complexes can be checked with:

```bash
python scripts/validate_sampl6_mapping.py \
  --input tasks/inputs/fep_atom_mapping_001 \
  --output results/fep_atom_mapping_001_sampl6.json
```

This validates the GST guest atom names/elements in the real source PDBs. PDB
coordinates alone do not provide complete bond-order or stereochemistry
metadata, so this is an input/mapping validation result—not a completed FEP
simulation.

## Local molecular execution

The branch also includes a bounded native OpenMM molecular TI proof:

```bash
python scripts/run_molecular_ti.py \
  --output results/molecular_ti_local_001.json
```

It runs two replicas across 11 lambda windows with explicit endpoint bonded
parameters and records platform, seeds, energies, derivatives, and lambda
coverage. It establishes local alchemical execution, but is not a
protein–ligand production FEP qualification.

The downloaded SAMPL6 guest endpoints can be parameterized and smoke-tested
locally with:

```bash
python scripts/run_sampl6_endpoint_smoke.py
```

This uses AmberTools GAFF2/AM1-BCC and OpenMM CUDA for 100-step endpoint runs.
It verifies the real guest parameterization and engine path; it does not claim
that the two endpoint runs constitute a relative FEP estimate.

## Constraints

No production simulation is allowed for this task. Do not infer stereochemical
validity from a MOL2 file that contains no stereochemical metadata; report that
limitation. Do not silently repair atom maps or change endpoint charges.
