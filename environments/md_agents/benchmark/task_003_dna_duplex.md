**Task ID:** `task_003_dna_duplex`

**Task:** [DNA duplex protocol reconstruction](MD-PAPER-003_DNA_DUPLEX/TASK.md)

## Published Results

**Source:** The selected primary DNA-duplex MD study must be pinned by DOI,
revision, input structure, and supplementary reference data before numerical
comparison. The current packet exposes no unverified published values.

| Published metric | Reported value or outcome | Scope and interpretation |
| --- | --- | --- |
| Base-pair occupancy | Extract hydrogen-bond and pairing definitions. | Definitions and denominator must match. |
| Helical observables | Extract twist, rise, and stacking definitions and ranges. | A stable short trajectory is not reproduction. |
| Simulation protocol | Recover force field, water/ions, temperature, pressure, electrostatics and sampling. | Missing values remain explicit. |

## Evaluation Criteria

| Criterion | Comparison requirement | Acceptance boundary |
| --- | --- | --- |
| Source pinning | Record DOI, revision, structure hash, and supplementary locations. | `NOT_PINNED` prevents scientific PASS. |
| Preparation | Match termini, protonation, ions, water model, and box. | No silent preparation changes. |
| Analysis | Use paper base-pair, stacking, and helical selections. | Units and selections must be identical. |
| Uncertainty | Analyze independent replicas and convergence. | Report uncertainty and missing references separately. |
