# **Task ID:** `task_002_ptp1b_rbfe`

**Task:** [PTP1B RBFE reconstruction](../tasks/fep_paper_002/TASK.md)

## Published Results

**Source:** Ross et al., *The maximal and current accuracy of rigorous
protein–ligand binding free energy calculations*, Communications Chemistry
(2023), [DOI 10.1038/s42004-023-01019-9](https://doi.org/10.1038/s42004-023-01019-9); [public benchmark repository](https://github.com/schrodinger/public_binding_free_energy_benchmark), pinned revision `a65d86b782a678c75388566ce00446e45283ee63`.

| Published metric | Reported value or outcome | Scope and interpretation |
| --- | --- | --- |
| Protein system | **PTP1B, PDB 2QBS** | Benchmark structure identity; not evidence of a completed local simulation. |
| Selected transformation | **23477 → 23482** | One edge from `jacs_set`; direction is part of the task contract. |
| Experimental relative affinity | **−1.16 kcal/mol** | Evaluator-only reference value; it is not a calculated FEP result. |
| Open production protocol | **Not available for this edge** | Missing edge-specific trajectories and proprietary execution details remain unresolved. |

The task intentionally selects one concrete edge. It does not claim to
reproduce the entire benchmark or a production FEP trajectory bundle.

## Configuration matrix

| Configuration | Purpose | Result |
| --- | --- | --- |
| A — paper reference | Independent source record | `REFERENCE_ONLY` |
| B — specialist-generated | Local GAFF2/AM1-BCC endpoint setup | `SETUP_PASS` |
| C — supported alternative | OpenFE-compatible alternative | `REVIEW` |
| D — perturbed | Reversed transformation fault case | `FAIL`, stopped before execution |

## Evaluation Criteria

| Criterion | Comparison requirement | Acceptance boundary |
| --- | --- | --- |
| Source identity | Match revision, protein, PDB and ligand edge. | All frozen hashes and direction must match. |
| Endpoint preparation | Generate and independently load both ligand endpoint topologies. | MOL2/FRCMOD/PRMTOP/INPCRD artifacts exist and `tleap` reports no error. |
| Protein preparation | Normalize the PDB and generate an ff14SB protein topology. | `tleap` completes without errors; the recorded net charge is retained for later neutralization. |
| Parameter provenance | Distinguish source-reported, inferred and missing parameters. | GAFF2/AM1-BCC is labelled inferred; missing lambda and replica data remain unresolved. |
| Configuration handling | Run reference, specialist, alternative and perturbed conditions. | Reversed edge is stopped before simulation; valid setup is not promoted to production. |
| Scientific qualification | Evaluate complex/solvent legs, trajectories, overlap and convergence. | Missing evidence returns `REVIEW`, never `PASS`. |

The machine-readable comparison is in
`../tasks/fep_paper_002/evaluation/paper_parameter_comparison.json`.

## Acceptance boundaries

- Source revision, protein identity, ligand files and edge direction must
  match the frozen manifest.
- Both endpoint ligand topologies must be independently loadable by `tleap`.
- Config D must be rejected before simulation.
- Missing production evidence must result in `REVIEW`, never `PASS`.
- A setup match must not be reported as a free-energy reproduction.

The detailed execution trace, hashes and results are retained under the task
bundle and `../results/fep_paper_002/`.
