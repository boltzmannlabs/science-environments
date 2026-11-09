# task_007_kemp_qmmm

## Description

Calculate reaction free-energy surfaces and activation free energies for KE07, KE10(V131N), KE15 and KE16, using exact designed enzyme–substrate models and a consistent treatment of the bond-changing reaction.

## Target

**Reaction:** Kemp elimination of 5-nitrobenzisoxazole → 2-cyano-4-nitrophenol.\
**Systems:** KE07, KE10(V131N), KE15 and KE16; preserve exact construct/mutation identities.\
**Starting-model requirement:** Obtain the designed enzyme–substrate coordinates and full sequences for each system before execution.\
**Structural identity checks:** KE07 derives from the 1THF scaffold and has an experimental structure, 2RKX. Neither a natural scaffold nor a crystal structure automatically reproduces its original designed complex.\
**Objective:** Evaluate the reaction surfaces of existing designs. New enzyme generation is outside this task.

## Design Constraints

- Bind each system to an exact designed sequence, complete mutation list, substrate pose and atom numbering. Do not substitute KE07 for another construct or silently revert V131N.
- Prepare the chemically correct substrate, catalytic base and protein environment with explicit protonation, charges, connectivity and any truncation or boundary atoms.
- Define the reactive region, electronic treatment, surrounding molecular environment, solvent and boundary conditions before execution. Save a complete parameter/input package.
- Sample coupled proton transfer and isoxazole N–O ring opening; specify reaction coordinates, restraints, window placement, equilibration and production sampling.
- Calculate a continuous reaction free-energy surface and identify the connected reactant-to-product pathway and transition-state region. A single-point energy or static geometry is insufficient.
- Use one declared reactant free-energy reference and consistent units; check convergence, overlap or connectivity of sampled regions and uncertainty.
- Keep changes to the system representation or reaction model separately identified. Never tune sampling or restraints after seeing the barrier without declaring a new condition.
- If a system does not support the intended bound/reactive configuration, report the structural or sampling problem explicitly and retain an unavailable result if no valid pathway is established.

## Workflow

| Stage | Capability | Expected evidence |
| --- | --- | --- |
| Recover designed complexes | Recover and verify exact designed input models, sequences and molecular parameters for each system; report any missing package. | Verified constructs, full mutation lists, substrate poses and parameters. |
| Prepare reaction models | Prepare reactive and surrounding regions, chemical states, solvent and a fixed sampling protocol. | Reactive-region definitions, solvent/boundary conditions and frozen protocol. |
| Sample reaction surface | Equilibrate systems and sample the coupled proton-transfer/ring-opening surface with traceable execution. | Traceable coupled proton-transfer/ring-opening sampling. |
| Check convergence | Reconstruct surfaces, check convergence and locate the intended reaction pathway. | Connected reaction surfaces and convergence/overlap diagnostics. |
| Compare and report | Extract activation free energies with uncertainty, preserving unavailable results and supporting diagnostics. | Per-system activation free energies, uncertainty and explicit missing results. |

## Evaluation Metrics

| Property | Required calculation | Reporting scope |
| --- | --- | --- |
| Activation free energy | Reactant-to-transition-state free-energy difference for each modeled system. | Report units, reaction model, system representation, reference state, convergence and uncertainty. Keep electronic barriers and rate-derived estimates separate. |

Report every individual observation with candidate/system ID, chemical state, method/version, units or native score scale, parameters, sampling, uncertainty where applicable, and raw-artifact path. Keep per-state and per-cohort results distinct from pooled summaries. Declare alignment, equivalent-atom handling and score normalization before assessment. Missing or incompatible results remain explicitly unavailable.

Exact designed complexes and reaction-parameter inputs are a prerequisite. If they cannot be recovered, return an input/capability gap report rather than reporting a calculated barrier.

## Expected Output

**Format:** `enzyme_computational_bundle`\
**Directory:** `08_results/task_007_kemp_qmmm/<run_id>/`

- `input_manifest.json`: input identities, hashes, chemical states, preparation decisions and missing inputs.
- `sequences.fasta` and `structures/`: sequences and structures, identifying generated candidates and imported controls.
- `residue_atom_mapping.csv`: source-to-design residue and atom correspondences, including state-dependent changes.
- `metrics.csv`: individual computational measurements with units/scales, state, replicate/sample and missing-result status.
- `metrics.json`: calculation definitions, validity checks, sample counts, uncertainties and exclusions.
- `selection.csv`: selection decisions and reasons; mark calculation-only systems as controls.
- `report.md`: completed work, computational results, selection rationale, capability gaps and limitations.
- Native prediction, ensemble or simulation files and complete execution logs.

## Important Instructions

- Choose suitable working tools independently and record their actual methods and versions. Preserve each metric’s definition and native scale when comparing implementations.
- Execute real calculations and retain native outputs for every reported measurement.
- Preserve the starting input coordinates. Save preparation, refinement and evaluation structures as separate files with residue and atom mappings.
- Declare the candidate budget, sampling, scoring definitions and selection rule before evaluating outputs. Record incomplete calculations and exclusions.
- Keep existing structures and controls distinct from newly generated candidates. Do not use historical rankings or outcome tables to select new candidates.
- Freeze generated candidates before independent comparison. Supporting validity checks do not establish catalytic activity.
- Keep execution artifacts outside the task and input directories. Run long calculations in a persistent logged session and record how to reconnect.
