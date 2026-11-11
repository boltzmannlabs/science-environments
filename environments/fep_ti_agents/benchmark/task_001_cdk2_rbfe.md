**Task ID:** `task_001_cdk2_rbfe`

**Task:** [CDK2 RBFE reconstruction](../tasks/fep_paper_001/TASK.md)

## Published Results

**Source:** Sun and Huggins, *Assessing the effect of forcefield parameter
sets on the accuracy of relative binding free energy calculations*, Frontiers
in Molecular Biosciences (2022), [DOI 10.3389/fmolb.2022.972162](https://doi.org/10.3389/fmolb.2022.972162); pinned Alchaware revision `1ff4ea36bf354bb842b786fc6d18e482b6428edb`.

| Published metric | Reported value or outcome | Scope and interpretation |
|---|---|---|
| System | **CDK2, PDB 1H1Q** | Selected protein system from the source pair list. |
| Transformation | **Ligand 17 → ligand 1h1q** | Direction and neutral endpoint charges are task inputs. |
| Engine/protocol | **OpenMM 7.2 with OpenMMTools HREX** | Source configuration; local setup comparison must disclose substitutions. |
| Parameter arms | **GAFF 2.11; AM1-BCC and RESP** | Sensitivity arms, not interchangeable defaults. |

The source protocol reports complex and solvent legs, MCS alignment, TIP3P,
0.15 M ionic strength, 0.9 nm padding, five steric and five electrostatic
windows and HREX exchange settings. These are configuration references; they
do not by themselves establish a reproduced free-energy estimate.

## Evaluation Criteria

| Criterion | Comparison requirement | Acceptance boundary |
|---|---|---|
| Protocol extraction | Match engine, force fields, charge methods, water, legs and lambda settings. | Each field is scored independently and source/inferred values are labelled. |
| Endpoint identity | Preserve CDK2/1H1Q and ligand `17 -> 1h1q`. | Reversed or mismatched endpoints fail before simulation. |
| Setup evidence | Validate mapping and endpoint artifacts. | Missing topology or trajectories remains `REVIEW`. |
| Scientific result | Compare ΔG/ΔΔG only with matched definitions and uncertainty. | No paper-level reproduction claim without trajectories and independent analysis. |

Current status: setup reconstruction `SETUP_VALIDATED`; scientific FEP
qualification `REVIEW`.
