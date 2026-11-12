**Task ID:** `task_002_barnase_barstar`

**Task:** [Barnase–barstar interface dynamics reconstruction](MD-PAPER-002_BARNASE_BARSTAR/TASK.md)

## Published Results

**Source:** *Propagation of Dynamic Changes in Barnase Upon Binding of Barstar: An NMR and Computational Study*, J. Mol. Biol. (2007), DOI: [10.1016/j.jmb.2007.01.051](https://doi.org/10.1016/j.jmb.2007.01.051).

| Published metric | Reported value or outcome | Scope and interpretation |
| --- | --- | --- |
| Interface dynamics | Extract the reported free/bound dynamics and contact observables. | Free and bound systems must not be conflated. |
| Simulation protocol | Recover engine, force field, solvent, temperature, electrostatics, replicas and production length. | Defaults are not substitutes for missing settings. |
| NMR/computational comparison | Compare identical residue selections and order parameters. | NMR is supporting context, not a computational baseline. |

## Evaluation Criteria

| Criterion | Comparison requirement | Acceptance boundary |
| --- | --- | --- |
| Complex identity | Use PDB 1BRS-derived input with hash and preparation record. | Invalid or altered interface inputs fail setup. |
| Protocol reconstruction | Preserve free/bound distinction and every reported control parameter. | Unreported parameters are `NOT_REPORTED`. |
| Contact/dynamics analysis | Match contact definitions, residue selections, and trajectory windows. | Alternative definitions are separate. |
| Replication | Run independent replicas and calculate uncertainty. | Short bounded replicas remain `REVIEW`. |
