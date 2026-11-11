**Task ID:** `task_003_force_field_sensitivity`

**Task:** Force-field sensitivity reconstruction.

## Published Results

**Source:** Sun and Huggins (2022), [DOI 10.3389/fmolb.2022.972162](https://doi.org/10.3389/fmolb.2022.972162).

The paper compares force-field, water-model and ligand-charge configurations.
The exact transformation and source metric table for this case must be pinned
before execution; this task is currently `CATALOGUED`.

## Evaluation Criteria

- Freeze one reported transformation and all endpoint structures.
- Reconstruct the paper arm, an agent-generated arm and one-factor-at-a-time
  alternatives.
- Compare parameter fidelity separately from free-energy agreement.
- Do not mark `REFERENCE_READY` until supplementary inputs and computed
  reference metrics are collected.
