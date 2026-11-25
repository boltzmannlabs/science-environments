# Task: fep_paper_003

**Task family:** Paper-based FEP environment reconstruction  
**Status:** reference-ready / setup validation

## Research source

SAMPL6 host–guest challenge, selected relative transformation **OA-G3 → OA-G6**.
The frozen source URLs, endpoint identities and experimental reference are
recorded in `reference/parameters.json`.

## Scientific objective

Construct a traceable host–guest relative free-energy environment from the
published source inputs. The agent must identify the octa-acid host, guest
identity, endpoint charge state, complex and solvent legs, and any reported
protocol values. It must label each chosen setting as `REPORTED`, `INFERRED`,
`NOT_REPORTED`, or `CONFLICTING`.

## Required inputs

- `inputs/complex/oa_g3_complex.pdb`
- `inputs/complex/oa_g6_complex.pdb`
- `inputs/solvent/oa_g3_solvent.pdb`
- `inputs/solvent/oa_g6_solvent.pdb`
- `reference/parameters.json`

## Required outputs

- `evaluation/input_validation.json`
- `configs/config_A_reference.json`
- `configs/config_B_agent.json`
- `configs/config_C_alternative.json`
- `configs/config_D_perturbed.json`
- `expected_outputs/qualification.json`

## Acceptance

- Validate all four frozen PDB inputs against their SHA-256 values.
- Confirm the OA-G3 → OA-G6 direction and the evaluator-only experimental
  relative target of `0.21 ± 0.028 kcal/mol`.
- Identify incomplete topology, lambda, production and estimator evidence as
  `REVIEW`; never fabricate an executed free-energy result.
- Reject the deliberately reversed/sign-inconsistent configuration before
  simulation.
