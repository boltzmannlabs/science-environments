# Task: fep_paper_005

**Task family:** Paper-based FEP force-field sensitivity reconstruction  
**Status:** executable setup benchmark / review

## Research source

Sun and Huggins, *Assessing the effect of forcefield parameter sets on the
accuracy of relative binding free energy calculations* (2022), DOI
`10.3389/fmolb.2022.972162`. Selected system: CDK2 PDB `1H1Q`, ligand `17 →
1h1q`, pinned from the Alchaware source inputs.

## Objective

Evaluate whether agents correctly extract and configure the reported force
field, water model, charge method and alchemical settings, then isolate one
parameter change at a time. This benchmark measures setup sensitivity; it does
not claim a paper-level ΔΔG reproduction without complete trajectories.

## Required outputs

- Input hash and source validation.
- Four configurations: paper reference, agent reconstruction, one-factor
  alternative, and invalid perturbed setup.
- Parameter comparison marking `REPORTED`, `INFERRED`, `NOT_REPORTED` or
  `CONFLICTING`.
- Independent validation that Config D stops before simulation.

## Acceptance

The agent must preserve the paper reference configuration, change only the
declared sensitivity factor in Config C, and reject Config D. Missing endpoint
topologies, lambda trajectories, convergence, uncertainty and reference
comparison remain `REVIEW`.
