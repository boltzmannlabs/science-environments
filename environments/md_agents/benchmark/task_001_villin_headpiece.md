**Task ID:** `task_001_villin_headpiece`

**Task:** [Villin folding protocol reconstruction](MD-PAPER-001_VILLIN/TASK.md)

## Published Results

**Source:** Duan et al., *A point-charge force field for molecular mechanics simulations of proteins based on condensed-phase quantum mechanical calculations*, J. Comput. Chem. 24 (2003), DOI: [10.1002/jcc.10349](https://doi.org/10.1002/jcc.10349).

| Published metric | Reported value or outcome | Scope and interpretation |
| --- | --- | --- |
| Folding/native-state observables | Extract from the paper and supplement before scoring. | Do not substitute a short local trajectory or experimental value. |
| Protocol settings | Force field, solvent, temperature, timestep, equilibration and production settings. | Label every field `REPORTED`, `INFERRED`, or `NOT_REPORTED`. |
| Structural comparison | Use the paper's observable definitions and reference structures. | RMSD, radius of gyration, contacts, and populations require matched units. |

## Evaluation Criteria

| Criterion | Comparison requirement | Acceptance boundary |
| --- | --- | --- |
| Input identity | Hash the local 1VII-derived input and preserve provenance. | Exact input and source record required. |
| Protocol reconstruction | Match force field, solvent, temperature, timestep, electrostatics, and sampling. | Missing values remain `REVIEW`. |
| Observable analysis | Reproduce selections, units, windows, and averaging. | No substituted observable or experimental proxy. |
| Uncertainty | Use independent replicas and a paper-compatible estimator. | One short run cannot receive scientific PASS. |
