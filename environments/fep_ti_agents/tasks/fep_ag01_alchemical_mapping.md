# Task: fep_ag01_alchemical_mapping

## Description

Audit atom correspondence for a proposed alchemical transformation before any production sampling. Check conserved substructures, atom-map uniqueness, stereochemistry, formal charges, bond-order changes, dummy atoms, and endpoint protonation.

## Dataset and inputs

- `benchmarks/sampl6/manifest.json` (OA-G3 → OA-G6 pilot pair)
- Endpoint structures/topologies, atom map, charge and parameter manifest

## Tools to use

RDKit or an equivalent graph validator; topology parser; SHA-256 manifest; independent valence and mapping checks.

## Expected outputs

`mapping_report.json` with mapped pairs, conserved atoms, changed bonds, unmapped atoms, warnings, provenance, and PASS/REVIEW/FAIL status.

## Acceptance and limitations

PASS requires unique chemically valid correspondence. Ambiguous maps, unsupported ring changes, or missing parameters must stop. This card does not prove free-energy convergence.
