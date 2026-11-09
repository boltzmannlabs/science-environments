# task_002_rfdiffusion2_cysteine_hydrolase

## Description

Design new cysteine hydrolases for 4-methylumbelliferyl butyrate hydrolysis. Scaffold the catalytic site in a modeled tetrahedral state, refine sequences while maintaining the reaction geometry, and assess structural recovery and active-site preorganization.

## Target

**Reaction:** 4-methylumbelliferyl butyrate + water → 4-methylumbelliferone + butyrate.\
**Starting structure:** PDB 1PPN.\
**Catalytic residues:** Gln19, Cys25, His159 and Asn175, with the local backbone around Ser24–Trp26; verify author numbering and chain.\
**Generation state:** First tetrahedral intermediate of the specified ester substrate; its exact ligand conformer must be prepared and documented.\
**Design lengths:** 95–185 residues.\
**Objective:** Generate new scaffolds and quantify independent fold and catalytic-site recovery.

## Design Constraints

- Prepare the first tetrahedral intermediate explicitly, including stereochemistry, formal charges, Cys–substrate connectivity and the oxyanion. Do not use a peptide substrate or the crystallographic ligand as the ester.
- Preserve Cys25 heavy atoms; His159 CB and imidazole-ring atoms; the Asn175 functional group and its connecting sidechain context; and the Gln19 amide group and its connecting sidechain context. Save an explicit atom mask verified against the source residue identities.
- Retain Ser24 backbone N/CA/C and Trp26 N/CA/C/O as local context for placement of the cysteine and oxyanion hole. Track these positions when sequence indices change.
- Constrain the Cys–His, His–Asn, His–substrate and backbone/sidechain oxyanion interactions. Record target distances, angles, dihedrals, and declared tolerances from the prepared motif.
- Preserve catalytic amino-acid identities through all sequence-design/refinement cycles and record every intermediate sequence and structure.
- Use an initial backbone-designability screen followed by deeper sequence refinement of retained backbones; record the sequence and prediction counts separately for each stage.
- Assess sequence-only fold recovery independently. For the later substrate-bound and acyl-enzyme ensembles, prepare the appropriate covalent cysteine modification and retain complete atom mappings.
- Target 50 samples for each later chemical state; reduced sampling and unsupported covalent states must be identified.

## Workflow

| Stage | Capability | Expected evidence |
| --- | --- | --- |
| Prepare inputs | Prepare the motif and tetrahedral substrate state with verified donor/acceptor and residue mappings. | Verified tetrahedral-state chemistry, atom mask and catalytic interaction map. |
| Generate and screen | Generate backbones over the declared length range, design multiple sequences per backbone and independently assess initial designability. | Backbones, sequences, independent predictions and initial designability decisions. |
| Refine sequences | For retained backbones, alternate sequence redesign and constrained all-atom refinement, preserving the catalytic site. | Per-cycle sequences and constrained all-atom structures. |
| Check structural recovery | Predict refined sequences independently and assess global and catalytic-site agreement. | Separate global, catalytic-Cα and motif-heavy-atom measurements. |
| Assess reaction states | Generate substrate-bound and acyl-enzyme ensembles, calculate structural recovery and summarize per-design measurements. | Substrate/acyl-state ensembles, individual geometry records and summaries. |

## Evaluation Metrics

| Property | Required calculation | Reporting scope |
| --- | --- | --- |
| Global structural agreement | Cα RMSD between the designed and independently predicted structures. | Record sequence correspondence, global alignment and missing residues. |
| Catalytic-site recovery | Catalytic-residue Cα RMSD and motif heavy-atom RMSD. | Keep globally aligned catalytic Cα RMSD distinct from motif-aligned heavy-atom RMSD. |
| Active-site preorganization | State-specific catalytic geometry and sidechain deviation across the two assessment ensembles. | Retain individual samples and state definitions; incomplete chemical states remain unavailable. |
| Structural similarity | TM-score against known structural matches. | Record fixed-pair versus database-search scope, chain selection and score normalization. |

Report every individual observation with candidate/system ID, chemical state, method/version, units or native score scale, parameters, sampling, uncertainty where applicable, and raw-artifact path. Keep per-state and per-cohort results distinct from pooled summaries. Declare alignment, equivalent-atom handling and score normalization before assessment. Missing or incompatible results remain explicitly unavailable.

## Expected Output

**Format:** `enzyme_computational_bundle`\
**Directory:** `08_results/task_002_rfdiffusion2_cysteine_hydrolase/<run_id>/`

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
