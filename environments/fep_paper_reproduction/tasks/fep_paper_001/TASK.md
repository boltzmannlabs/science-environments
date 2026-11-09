# Task: fep_paper_001

**Task family:** Paper-based FEP environment reconstruction
**Status:** executable protocol benchmark; free-energy qualification requires complete trajectories.

## Research paper

Assessing the effect of forcefield parameter sets on the accuracy of relative
binding free energy calculations. DOI: `10.3389/fmolb.2022.972162`.

Selected system: one CDK2 transformation from the JACS benchmark, using the
paper's CDK2 target (PDB 1H1Q) and the OpenMM FEP workflow. The benchmark tests
whether the agent reconstructs complex and solvent legs, not whether it runs
all eight target systems.

## Required outputs

Generate `reference/extracted_parameters.json`, four configuration files,
complex/solvent setup manifests, mapping/provenance records, and a comparison
report. Config D must be rejected when its mapping or lambda schedule is
invalid.

## Acceptance criteria

Score extraction of OpenMM 7.2, GAFF 2.11, charge model, protein force field,
water model, endpoint identity, complex/solvent legs, lambda protocol, and
analysis estimator separately. Missing topology or trajectories returns
`REVIEW`, never a fabricated ΔΔG.
