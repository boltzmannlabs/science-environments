# Task ID: `task_004_second_rbfe`

**Task:** [Second PTP1B RBFE edge](../tasks/fep_paper_004/TASK.md)

## Published Results

**Source:** Ross et al. (2023), [DOI 10.1038/s42004-023-01019-9](https://doi.org/10.1038/s42004-023-01019-9).

The second frozen edge is PTP1B `2QBS`, ligand `23477 → 23479`, with
experimental reference `−0.29 kcal/mol`. Both endpoint structures, the edge
table and hashes are present in the canonical task packet.

**Status:** `REFERENCE_READY / REVIEW`.

## Evaluation Criteria

- Preserve the same reference/agent/alternative/perturbed configuration matrix.
- Validate endpoint identity, topology compatibility and transformation
  direction before simulation.
- Confirm the reversed-edge fault configuration is stopped before execution.
- Keep missing production trajectories and scientific reference evidence as
  `REVIEW`.

The independent validator is
`../tasks/fep_paper_004/scripts/validate_inputs.py`; task tests report the
current evidence.
