# task_003_serine_hydrolases

## Description

Design new serine hydrolases around the specified catalytic motif and evaluate the catalytic hydrogen-bond geometry across the ester-hydrolysis reaction states.

## Target

**Reaction:** Hydrolysis of a 4-methylumbelliferyl ester to 4-methylumbelliferone and its corresponding carboxylate.\
**Default substrate:** 4-methylumbelliferyl phenylacetate, matching the phenylacetyl group in the modeled near-tetrahedral motif ligand. Acetate and butyrate campaigns require separately prepared ligand/state inputs and remain separate cohorts.\
**Starting motif:** A serine–histidine–aspartate catalytic arrangement with backbone oxyanion-hole context.\
**Chemical inputs:** Prepare the specified ester and its near-tetrahedral intermediate with explicit topology and conformers.\
**Protected local segments:** A56–60, A83–85, A113–115 and B145–147. Catalytic residues are Ser A58, His A84 and Asp A114; the additional segment supplies backbone oxyanion-hole context.\
**Objective:** Scaffold the motif, design sequences, and assess catalytic geometry over five chemical states.

## Design Constraints

- Use the listed motif segments and modeled ligand as inputs; alanine-rich template regions outside those segments are context, not a full sequence or backbone to preserve.
- Verify the ligand topology and near-tetrahedral state before generation. Record atom names, bond orders, protonation, charge and any covalent serine–ligand bond; do not treat the modeled intermediate as the unmodified substrate.
- Preserve the catalytic residue identities, the serine–histidine–acid interaction network and the selected backbone oxyanion-hole donor geometry. Map every protected source residue to the generated sequence.
- Generate and refine scaffolds, then alternate sequence design and constrained all-atom refinement for three cycles. Keep canonical generated models separate from assessment structures.
- Assess fold recovery and catalytic-site agreement before multistate analysis. Declare whether structure predictions are sequence-only or use sparse structural contacts; report those regimes separately.
- Prepare apo, substrate-bound, first tetrahedral intermediate, acyl-enzyme and second tetrahedral intermediate states. Define state-specific serine modifications and atom mappings explicitly.
- Target 50 samples per state. Measure Ser(Oγ)–His(Nε)–His(Cε) with His Nε as the angle vertex consistently across all states.
- Calculate the angle independently of any restraint used in generation, retain every sample and distinguish invalid mappings from geometric outliers. Do not assign experimental activity classes to generated candidates.

## Workflow

| Stage | Capability | Expected evidence |
| --- | --- | --- |
| Prepare inputs | Validate the specified motif and ligand chemistry and construct state definitions and protected residue maps. | Verified chemical states, ligand topology and protected residue map. |
| Generate and refine | Generate new scaffolds, reconstruct complete all-atom structures and perform the constrained sequence/refinement cycles. | New scaffolds and three traceable sequence/refinement cycles. |
| Check design validity | Predict structures and apply predeclared fold and motif-validity checks. | Predicted structures and separate sequence-only/contact-assisted validity decisions. |
| Assess reaction states | Generate separate ensembles for the five chemical states and calculate the same atom-defined catalytic angle in each sample. | Five state-specific angle ensembles with atom mappings and sample counts. |
| Compare and report | Report per-state angle distributions, per-candidate summaries and selection decisions. | State distributions, declared pooling weights and selection decisions. |

## Evaluation Metrics

| Property | Required calculation | Reporting scope |
| --- | --- | --- |
| Catalytic serine–histidine geometry | Distribution of Ser(Oγ)–His(Nε)–His(Cε) angles. | Report individual angles, state-level medians and pooled summaries with explicit state weights. Keep substrate cohorts and prediction regimes separate. |

Report every individual observation with candidate/system ID, chemical state, method/version, units or native score scale, parameters, sampling, uncertainty where applicable, and raw-artifact path. Keep per-state and per-cohort results distinct from pooled summaries. Declare alignment, equivalent-atom handling and score normalization before assessment. Missing or incompatible results remain explicitly unavailable.

## Expected Output

**Format:** `enzyme_computational_bundle`\
**Directory:** `08_results/task_003_serine_hydrolases/<run_id>/`

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
