# Task ID: `task_003_force_field_sensitivity`

**Task:** [CDK2 force-field sensitivity reconstruction](../tasks/fep_paper_005/TASK.md)

## Published Results

**Source:** Sun and Huggins (2022), [DOI 10.3389/fmolb.2022.972162](https://doi.org/10.3389/fmolb.2022.972162).

The paper compares force-field, water-model and ligand-charge configurations.
The selected system is CDK2 PDB `1H1Q`, ligand `17 → 1h1q`, with frozen
protein and ligand inputs under the canonical task packet.

**Status:** `REFERENCE_READY / REVIEW`.

## Evaluation Criteria

- Validate all three frozen input hashes and the selected edge.
- Reconstruct the paper arm, an agent-generated arm and a one-factor RESP
  charge alternative.
- Stop the unsupported/undeclared water-model perturbation before simulation.
- Compare parameter fidelity separately from free-energy agreement.
- Keep production sensitivity and uncertainty `REVIEW` until trajectories exist.

The independent validator is
`../tasks/fep_paper_005/scripts/validate_inputs.py`; task tests report the
current evidence.
