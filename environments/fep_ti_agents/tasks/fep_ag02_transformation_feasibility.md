# Task: fep_ag02_transformation_feasibility

## Description

Determine whether endpoint chemistry, protonation, charge, stereochemistry, and available force-field terms support the requested transformation.

## Dataset and inputs

- Endpoint structures and mapped transformation from FEP-AG01
- Force-field/parameter inventory and requested complex/solvent legs

## Tools to use

Chemical graph and valence checks, parameter coverage checker, charge/electron accounting, and immutable input manifest.

## Expected outputs

`transformation_report.json` containing supported/unsupported features, charge changes, assumptions, and a bounded recommendation.

## Acceptance and limitations

PASS requires compatible endpoints and complete supported terms. The agent must not invent topology or silently alter protonation to obtain PASS.
