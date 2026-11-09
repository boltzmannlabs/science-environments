# task_004_riff_diff_retroaldolases

## Description

Design retro-aldolases from a catalytic tetrad, build a substrate-accessible pocket and evaluate predicted structures, active-site dynamics and substrate/intermediate interaction geometry.

## Target

**Reaction:** (R)-methodol → 6-methoxy-2-naphthaldehyde + acetone.\
**Catalytic array:** The RA95.5-8F catalytic tetrad derived from PDB 5AN7.\
**Protected residues:** Tyr A1051, Lys A1083, Asn A1110 and Tyr A1180. Resolve their observed alternate locations explicitly.\
**Generation ligand:** LLK Z5001 in the starting array. Prepare methodol and covalent hemiaminal inputs separately for assessment.\
**Objective:** Generate new scaffolds around the catalytic functional groups and assess fold quality, novelty, dynamics and reaction-state geometry.

## Design Constraints

- Use the specified tetrad as the functional-group arrangement. Generate local backbone/rotamer alternatives around it rather than preserving the source enzyme scaffold.
- Check LLK chemistry, alternate locations, occupancies and explicit connectivity before use. A ligand analogue and a modeled covalent intermediate require separate atom maps.
- Construct a pocket and solvent-access channel during scaffold generation. Any temporary excluded-volume placeholder must be removed before final sequence design and evaluation.
- Preserve the catalytic residue identities and functional-group geometry through iterative scaffold refinement and sequence redesign. Record each iteration and any permitted local backbone movement.
- Predict candidate structures independently, then rebuild sidechains before evaluating catalytic-sidechain recovery. Save pre- and post-repacking coordinate versions.
- Keep alternative sequence/refinement branches separate. Record total structural energy and aggregation propensity with residue-count normalization, score definitions and preparation conditions.
- For apo-state dynamics, target 20 independent replicas of 20 ns per system; disclose shorter runs and all force-field, solvent, equilibration and alignment settings.
- For the two-state active-site assessment, prepare Michaelis-complex and hemiaminal states for each candidate and for the source enzyme, targeting 20 predictions per state. Keep their chemistry and sampling consistent.
- Normalize interaction measurements against the corresponding source-enzyme distributions. Report undefined normalizations explicitly; retain individual component values and the final aggregation rule.

## Workflow

| Stage | Capability | Expected evidence |
| --- | --- | --- |
| Prepare catalytic arrays | Prepare catalytic-array conformers and artificial local motifs with substrate-pocket/channel context. | Catalytic-array conformers, ligand maps and pocket/channel context. |
| Generate and refine | Generate new scaffolds, assign sequences and iterate constrained refinement and redesign. | Scaffolds, sequences and per-iteration constrained models. |
| Assess predicted structures | Predict structures, rebuild sidechains and calculate confidence, catalytic recovery, energy and surface aggregation measurements. | Predictions, pre/post-repacking models and native-scale scores. |
| Assess catalytic dynamics | Run apo ensembles or trajectories and measure catalytic-residue fluctuations and interaction-distance deviations. | Replica trajectories, RMSF and catalytic-distance observations. |
| Assess states and novelty | Assess Michaelis-complex and hemiaminal ensembles and calculate the declared normalized active-site metric; record structural-neighbour search results separately. | Matched two-state measurements, reference normalizers and structural-neighbour records. |

## Evaluation Metrics

| Property | Required calculation | Reporting scope |
| --- | --- | --- |
| Predicted fold confidence | Mean per-residue prediction confidence. | Retain predictor/version and native confidence scale. |
| Catalytic recovery | Catalytic-sidechain RMSD to the input array after sidechain reconstruction. | Record alignment and equivalent-atom mapping. |
| Structural novelty | Maximum TM-score to known structural matches. | Record search database and normalization; report cohort statistics only over the actual sampled cohort. |
| Surface aggregation and structural energy | Surface aggregation propensity and total structural energy per residue. | Preserve score definitions and native units; alternative energy scales remain separate. |
| Catalytic dynamics | Catalytic-residue RMSF and deviations of catalytic interaction distances. | Retain per-replica values, alignment, state and uncertainty. |
| Two-state active-site metric | Calculate the seven atom-defined measurements and the two-state score defined below. | Retain state-specific reference medians/MADs, individual measurements, normalized components, state scores and selected sample identities. |

Report every individual observation with candidate/system ID, chemical state, method/version, units or native score scale, parameters, sampling, uncertainty where applicable, and raw-artifact path. Keep per-state and per-cohort results distinct from pooled summaries. Declare alignment, equivalent-atom handling and score normalization before assessment. Missing or incompatible results remain explicitly unavailable.


### Two-state active-site metric definition

Use the source residue identities below as catalytic roles and map them to each candidate. Define substrate atoms by chemical identity: `C_k` is the ketone carbonyl carbon, `O_k` its oxygen, `C_adj` the methyl-side carbon directly bonded to `C_k`, and `O_beta` the oxygen of the pre-existing beta-hydroxyl group. In the hemiaminal, `O_hemi` is the hydroxyl oxygen derived from `O_k`. Record their actual state-specific chain, residue and atom labels before scoring; `O_hemi` and `O_beta` are different atoms.

| State | Measurement | Ordered atoms or atom pair |
| --- | --- | --- |
| Michaelis complex | Attack distance | Lys A1083 NZ — `C_k` |
| Michaelis complex | Attack angle | Lys A1083 NZ — `C_k` — `O_k`; vertex at `C_k` |
| Michaelis complex | Attack dihedral | Lys A1083 NZ — `C_k` — `O_k` — `C_adj` |
| Hemiaminal | First hydroxyl interaction | Tyr A1051 OH — `O_hemi` |
| Hemiaminal | Second hydroxyl interaction | Tyr A1180 OH — `O_hemi` |
| Hemiaminal | Amide interaction | Asn A1110 ND2 — `O_hemi` |
| Hemiaminal | Beta-hydroxyl interaction | Tyr A1051 OH — `O_beta` |

The asparagine atom is its sidechain amide nitrogen ND2. Report distances in angstroms and angles/dihedrals in degrees. Preserve the same atom ordering, dihedral convention and reference-state chemistry for candidates and the source enzyme. Do not swap equivalent-looking atoms separately to improve a candidate score.

For state \(s\), sample \(j\) and component \(k\), let \(x_{s,j,k}\) denote the measurement. Using the separately generated source-enzyme ensemble for the same state, calculate:

\[
\mu_{s,k}=\operatorname{median}_{r=1}^{20}x^{\mathrm{ref}}_{s,r,k},
\qquad
D_{s,k}=\operatorname{median}_{r=1}^{20}
\left|x^{\mathrm{ref}}_{s,r,k}-\mu_{s,k}\right|.
\]

Normalize and average within each prediction:

\[
z_{s,j,k}=\frac{x_{s,j,k}-\mu_{s,k}}{D_{s,k}},
\qquad
d_{s,j}=\frac{1}{K_s}\sum_{k=1}^{K_s}z_{s,j,k},
\qquad K_{\mathrm{Michaelis}}=3,\quad K_{\mathrm{hemiaminal}}=4.
\]

The composite score is:

\[
m_{\mathrm{AS}}=
\min_{j=1,\ldots,20}d_{\mathrm{Michaelis},j}
+
\min_{j=1,\ldots,20}d_{\mathrm{hemiaminal},j}.
\]

Use signed normalized components as written; do not take absolute values of the numerator, rescale the MAD, or minimize individual components before averaging. The two state minima may come from different samples. Retain both selected sample IDs and all component measurements. If a required atom is missing, a reference MAD is zero, or the required ensemble is incomplete, leave this score unavailable; report any reduced-sampling or altered-definition score separately. Do not insert an epsilon, omit a component, or silently change the sample count.

## Expected Output

**Format:** `enzyme_computational_bundle`\
**Directory:** `08_results/task_004_riff_diff_retroaldolases/<run_id>/`

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
