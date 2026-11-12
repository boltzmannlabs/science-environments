# Task: md_paper_002

**Task family:** Conventional molecular dynamics paper reconstruction  
**Domain:** Computational chemistry and simulation methodology  
**Status:** reference-ready / setup validation

## Research paper

*Discovery of All-d-Peptide Inhibitors of SARS-CoV-2 3C-like Protease*, ACS
Chemical Biology (2023), DOI `10.1021/acschembio.2c00735`.

Selected input: SARS-CoV-2 3CLpro structure PDB `6M2N`.

## Objective

Evaluate whether AI agents can extract, configure, and validate a published
conventional atomistic molecular-dynamics protocol using a frozen structural
input. The benchmark evaluates literature parameter extraction, molecular
system preparation, force-field and solvent configuration, minimization,
NVT/NPT equilibration, standard production-MD configuration, input validation,
and provenance tracking. It is a computational-methodology benchmark; it does
not involve biological experimentation, pathogen engineering, biological
optimization, or experimental pathogen handling.

Excluded: coarse-grained MD, enhanced sampling, FEP, and free-energy
calculations.

## Paper-derived parameters

- GROMACS 2021.4
- AMBER14SB protein force field
- TIP3P water
- Dodecahedral periodic box
- Steepest-descent minimization
- 0.1 ns NVT and 1 ns NPT equilibration
- 310 K, 1 bar
- PME electrostatics, 12 Å cutoff
- Leapfrog stochastic dynamics, 2 fs timestep
- LINCS constraints

Each value is classified in `reference/parameters.json` as `reported`,
`inferred`, `not_reported`, or `conflicting`. Production duration and replica
details must be extracted from the full paper and supplementary information;
they are not silently invented for executable inputs.

Production duration and replica details must be extracted from the full paper
and supplementary information. Conflicting descriptions remain explicit
`REVIEW` evidence.

## Required outputs

- `reference/parameters.json`
- `configs/config_A_reference.json`
- `configs/config_B_agent.json`
- `configs/config_C_alternative.json`
- `configs/config_D_perturbed.json`
- `evaluation/input_validation.json`
- `expected_outputs/qualification.json`

## Acceptance

The input hash, PDB identity and reported preparation parameters must validate.
Config C may change one supported setting only. Config D must be rejected before
execution. A successful short preprocessing or MD run does not establish
agreement with the paper's production observables.
