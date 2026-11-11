# FEP-PAPER-002 — PTP1B paper-based setup reconstruction

**Task:** [PTP1B RBFE reconstruction task](../tasks/fep_paper_002/TASK.md)

## Published source and selected system

- **Source:** Ross et al., *The maximal and current accuracy of rigorous
  protein–ligand binding free energy calculations*, Communications Chemistry
  (2023), [DOI 10.1038/s42004-023-01019-9](https://doi.org/10.1038/s42004-023-01019-9).
- **Dataset:** public binding-free-energy benchmark, pinned revision
  `a65d86b782a678c75388566ce00446e45283ee63`.
- **System:** PTP1B, PDB `2QBS`.
- **Selected edge:** ligand `23477 -> 23482`.
- **Published experimental reference:** `-1.16 kcal/mol`.

This benchmark intentionally selects one concrete edge. It does not claim to
reproduce the entire dataset or a production FEP trajectory bundle.

## Benchmark objective

Measure whether the Agent Scientist can translate a published benchmark into a
traceable, executable setup: identify the system and edge, prepare endpoint
ligands, compare paper-derived parameters, and reject incomplete or perturbed
configurations.

## Configuration matrix

| Configuration | Purpose | Result |
| --- | --- | --- |
| A — paper reference | Independent source record | `REFERENCE_ONLY` |
| B — specialist-generated | Local GAFF2/AM1-BCC endpoint setup | `SETUP_PASS` |
| C — supported alternative | OpenFE-compatible alternative | `REVIEW` |
| D — perturbed | Reversed transformation fault case | `FAIL`, stopped before execution |

## Published-versus-agent comparison

The machine-readable comparison is in
`../tasks/fep_paper_002/evaluation/paper_parameter_comparison.json`.
Identity fields (protein, PDB and edge) match. The local GAFF2/AM1-BCC
parameterization is explicitly labelled an inferred local choice. Lambda
schedule, replica length, production trajectories and edge-specific protocol
details remain missing rather than being invented.

## Acceptance boundaries

- Source revision, protein identity, ligand files and edge direction must
  match the frozen manifest.
- Both endpoint ligand topologies must be independently loadable by `tleap`.
- Config D must be rejected before simulation.
- Missing production evidence must result in `REVIEW`, never `PASS`.
- A setup match must not be reported as a free-energy reproduction.

The detailed execution trace, hashes and results are retained under the task
bundle and the corresponding `results/fep_paper_002/` record.
