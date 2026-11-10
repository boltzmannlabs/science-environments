# Task: fep_paper_001

**Task family:** Paper-based FEP environment reconstruction
**Status:** executable protocol benchmark; free-energy qualification requires complete trajectories.

## Research paper

Assessing the effect of forcefield parameter sets on the accuracy of relative
binding free energy calculations. DOI: `10.3389/fmolb.2022.972162`.

Selected system: CDK2 PDB 1H1Q with the pinned public-code transformation
**ligand 17 → ligand 1h1q**. The exact pair is line 2 of
`inputs/source_cdk2/cdk2_pairs.txt`, from Alchaware revision
`1ff4ea36bf354bb842b786fc6d18e482b6428edb`.

## Required outputs

Generate `reference/extracted_parameters.json`, four configuration files,
the pinned ligand structures under `inputs/edge_17_to_1h1q/`, an independent
MCS mapping, endpoint-readiness evidence, and a Config A/Config B comparison.
Config D must be rejected when its mapping or lambda schedule is invalid.

## Acceptance criteria

Score extraction of OpenMM 7.2, GAFF 2.11, charge model, protein force field,
water model, endpoint identity, complex/solvent legs, lambda protocol, and
analysis estimator separately. Missing topology or trajectories returns
`REVIEW`, never a fabricated ΔΔG. A production FEP run is only eligible after
both complex and solvent endpoint topologies, solvent coordinates, an approved
atom map, lambda-window trajectories, replica metadata and independent
overlap/convergence/uncertainty evidence are present.
