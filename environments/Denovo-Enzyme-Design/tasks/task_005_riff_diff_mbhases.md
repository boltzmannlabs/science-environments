# task_005_riff_diff_mbhases

## Description

Design new enzymes for the coupling of 2-cyclohexen-1-one and 4-nitrobenzaldehyde using two distinct catalytic arrays. Evaluate each array family separately.

## Target

**Reaction:** 2-cyclohexen-1-one + 4-nitrobenzaldehyde → 2-[hydroxy(4-nitrophenyl)methyl]cyclohex-2-en-1-one.\
**Array A:** BH32.14-derived catalytic arrangement; catalytic His A2, Trp A3, Arg A4 and Glu A6; modeled reactant components CHO Z1 and NBA Z2.\
**Array B:** BH1.8-derived catalytic arrangement; His A23, Glu A26, Glu B6 and Trp E3; modeled component MIH Z1. Glu A26 is the proton-transfer residue whose pKa is evaluated.\
**Objective:** Scaffold each specified functional-group arrangement, design sequences and calculate computational structural/chemical quality measures.

## Design Constraints

- Preserve the two array identities, catalytic residue roles and modeled chemistry. Record canonical/noncanonical residue chemistry when present in source inputs rather than silently interchanging forms. Do not pool their sequences or structural predictions into a single cohort.
- Array A contains two modeled reactant components; array B uses a combined state representation. Verify component connectivity, protonation, atom selections and the canonical histidine representation before generation.
- Preserve catalytic residue identities and functional-group geometry while building local backbone motifs and new scaffolds. Map residues across chains and numbering changes explicitly.
- Build substrate-pocket and channel space during scaffold generation; remove any temporary pocket-shaping placeholder before final assessment.
- Alternate constrained refinement and sequence redesign, keeping branch choices and iteration counts attached to each candidate. Do not treat the final crystal structure of a design as the input catalytic array.
- Predict structures independently and reconstruct sidechains before measuring catalytic-array RMSD. Record prediction and repacking settings and coordinate versions.
- Normalize surface aggregation propensity and total structural energy by the number of designed residues. Preserve native scoring definitions and units.
- For array B, also calculate the pKa of the residue mapped from Glu A26 and assess the reaction product placement relative to the modeled array ligand using a chemically valid common-atom map. These two metrics are not applicable to array A.
- Track Glu A26 through any chain or residue renumbering. Glu B6 is a separate residue; report its pKa only as an additional, separately labelled observation if calculated.
- Declare the design budget and ranking rule separately for each array; preserve all candidates and failures.

## Workflow

| Stage | Capability | Expected evidence |
| --- | --- | --- |
| Prepare catalytic arrays | Validate the two starting arrays and their distinct chemical states and create atom/residue maps. | Separate array-A/array-B identities, chemical states and atom maps. |
| Generate and refine | Construct local motifs and pocket context, generate scaffolds and iteratively design/refine sequences. | Per-array scaffolds, sequences and refinement lineage. |
| Assess predicted structures | Predict structures, reconstruct sidechains and calculate confidence, catalytic RMSD and normalized surface/energy measurements. | Predictions, repacked models and residue-normalized measurements. |
| Assess array-B chemistry | For array B, prepare the product complex and calculate the pKa of the residue mapped from Glu A26 and common-atom product displacement. | Mapped Glu A26 pKa and product common-atom displacement for array B. |
| Compare and report | Report and select candidates separately for each array family. | Separate array-family summaries and selection decisions. |

## Evaluation Metrics

| Property | Required calculation | Reporting scope |
| --- | --- | --- |
| Predicted fold confidence | Mean per-residue prediction confidence. | Record the native scale and prediction settings. |
| Catalytic-array recovery | Catalytic-sidechain RMSD between repacked predicted structures and the corresponding input array. | Record atom selections, alignment and equivalent-atom handling. |
| Aggregation propensity | Surface aggregation propensity divided by design residue count. | Record structure, surface definition and normalization. |
| Structural energy | Total structural energy divided by design residue count. | Record score function, units and preparation; alternative scales remain separate. |
| Facilitating glutamate pKa | Predicted pKa of the candidate residue mapped from array B Glu A26. | Retain the source-to-candidate mapping, carboxyl-group definition and calculation conditions. Glu B6 is a distinct supporting residue and must not be substituted; array A is not applicable. |
| Product displacement | Common-heavy-atom RMSD of the modeled product to the corresponding array ligand representation for array B. | Record chemically valid atom mapping and protein alignment; incompatible mappings remain unavailable. |

Report every individual observation with candidate/system ID, chemical state, method/version, units or native score scale, parameters, sampling, uncertainty where applicable, and raw-artifact path. Keep per-state and per-cohort results distinct from pooled summaries. Declare alignment, equivalent-atom handling and score normalization before assessment. Missing or incompatible results remain explicitly unavailable.

## Expected Output

**Format:** `enzyme_computational_bundle`\
**Directory:** `08_results/task_005_riff_diff_mbhases/<run_id>/`

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
