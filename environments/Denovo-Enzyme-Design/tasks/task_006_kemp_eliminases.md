# task_006_kemp_eliminases

## Description

Assess Des27 and Des27.7 for substrate retention, productive substrate orientations and reaction free-energy profiles. Begin with the specified designed starting models and preserve system identity throughout simulation.

## Target

**Reaction:** Kemp elimination of 5-nitrobenzisoxazole → 2-cyano-4-nitrophenol.\
**Classical starting systems:** Des27 and Des27.7, each in substrate-bound and unbound states.\
**Reaction-profile starting systems:** Des27 and Des27.7, each with the substrate in IN and OUT orientations.\
**Catalytic context:** Asp162; verify numbering and reactive substrate atom identities against each starting system.\
**Objective:** Calculate substrate occupancy and reaction profiles for these existing designs. This is a calculation-only assessment; generation of new enzymes is outside this task.

## Design Constraints

- Use the specified designed models rather than replacing them with an apo crystal structure or a different Kemp eliminase. Keep protein sequence and substrate identity fixed.
- Retain complete modeled systems, including required waters, ions, protonation and substrate charges. Record preparation and any structural changes before production.
- Keep classical bound/unbound systems separate from the four reaction-profile systems; their topology, parameterization and solvent treatment may differ.
- For classical dynamics, target five independent replicas of 1 microsecond per system. Record actual simulated time, equilibration and output intervals; reduced sampling remains a distinct condition.
- Declare the exact active-site centre-of-mass atom set, masses, substrate atom selection, bound-state and reactive-state predicates, and IN/OUT orientation definitions before trajectory analysis.
- For reaction profiles, prepare both IN and OUT orientations for each enzyme. Target 30 independent reaction-profile trajectories per enzyme/orientation with consistent reaction reference and calibration.
- Verify that every required equilibration and reaction window has nonempty, valid inputs. Resolve residue labels from explicit atom mappings; do not trust stale numbering comments.
- Report incomplete system parameters or unavailable reaction-profile execution as unresolved. Starting structures alone do not provide time occupancy or activation free energy.

## Workflow

| Stage | Capability | Expected evidence |
| --- | --- | --- |
| Prepare existing systems | Validate the starting sequences, systems and reactive atom maps and prepare complete simulation parameters. | Exact starting-system identities, complete parameters and reactive atom maps. |
| Run dynamics | Equilibrate and run independent bound/unbound dynamics replicas; retain trajectories and actual simulation settings. | Bound/unbound trajectories, equilibration records and actual sampling. |
| Assess retention and orientation | Calculate substrate retention and productive-orientation distributions per replica and enzyme. | Per-replica counts, explicit denominators and orientation assignments. |
| Calculate reaction profiles | Run the four orientation-specific reaction-profile ensembles with complete parameter/window inputs and assess convergence. | Both orientations for both enzymes, profiles and convergence diagnostics. |
| Compare and report | Report per-enzyme retention, per-orientation profiles and barriers, uncertainty and complete execution evidence. | Retention estimates, barriers, uncertainty and raw execution evidence. |

## Evaluation Metrics

| Property | Required calculation | Reporting scope |
| --- | --- | --- |
| Substrate retention | Fraction of analyzed trajectory time in the declared bound state. | Report per-replica occupancies and enzyme-level estimates with uncertainty; calculate the ratio only with a valid nonzero denominator. |
| Productive orientations | IN/OUT orientation fractions within the declared reactive subset of substrate-bound samples. | Retain total analyzed, bound, reactive, IN and OUT frame counts and explicit conditional denominators. Report any all-bound-frame fractions separately. |
| Reaction free-energy profiles | Profiles and activation free energies for both orientations of both enzymes. | Preserve reaction model, reactant reference, calibration, sample counts and uncertainty. |

Report every individual observation with candidate/system ID, chemical state, method/version, units or native score scale, parameters, sampling, uncertainty where applicable, and raw-artifact path. Keep per-state and per-cohort results distinct from pooled summaries. Declare alignment, equivalent-atom handling and score normalization before assessment. Missing or incompatible results remain explicitly unavailable.

A complete production parameter/window package is required in addition to the starting coordinates. Inventory and report missing or empty inputs before dispatch.

## Expected Output

**Format:** `enzyme_computational_bundle`\
**Directory:** `08_results/task_006_kemp_eliminases/<run_id>/`

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
