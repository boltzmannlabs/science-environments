# task_001_rfdiffusion2_retroaldolase

## Description

Design new enzyme scaffolds for retro-aldol cleavage of methodol. Preserve a minimal catalytic functional-group arrangement, then assess fold consistency, active-site preorganization and structural novelty.

## Target

**Reaction:** Methodol → 6-methoxy-2-naphthaldehyde + acetone. Model (R)-methodol explicitly; identify any racemic assessment separately.\
**Starting structure:** PDB 5AN7, chain A; the declared polymer sequence contains 258 residues, of which 244 are present in the deposited coordinates, including the modified polymer residue. These counts are distinct from the requested design length.\
**Catalytic atoms:** Chain A Tyr1051 CZ/OH; Lys1083 CE/NZ; Asn1110 CG/OD1/ND2; Tyr1180 CZ/OH, using author numbering. Verify these identities against the coordinates.\
**Generation ligand:** The LLK inhibitor in the starting structure. It is a generation analogue; use separately prepared methodol and carbinolamine models for reaction-state assessment.\
**Design lengths:** Separate conditions of 120, 150 and 180 residues.\
**Objective:** Generate motif-preserving sequences/scaffolds and quantify their structural and active-site properties.

### Residue-number correspondence

Prepare a separate derivative using the native structure's sequence-based residue identifiers. The catalytic correspondence is:

| Source author identifier | Prepared identifier | Residue | Protected atoms |
| --- | --- | --- | --- |
| A1051 | A51 | TYR | CZ, OH |
| A1083 | A83 | LYS | CE, NZ |
| A1110 | A110 | ASN | CG, OD1, ND2 |
| A1180 | A180 | TYR | CZ, OH |

Verify this mapping against the native coordinate record. Sequence-based identifiers retain gaps for unobserved residues; they are not a consecutive renumbering of the 244 observed residues. Preserve the original source identifiers in the mapping record. The source author numbers do not indicate protein length.

## Design Constraints

- Apply the verified numbering transformation consistently to all observed polymer residues and every affected structural reference, including modified polymer residues and covalent/peptide links. Preserve chain identity, atom names, alternate-location decisions, coordinates and chemical connectivity. The modified residue MHO A1237 corresponds to A237; retain it and its peptide connections.
- Use A51, A83, A110 and A180 in prepared-input motif selections, fixed-atom selections and any residue-based constraints. Changing request labels without changing the prepared coordinate identifiers is invalid. Preserve ligand identifiers or map any changes explicitly, and update the LLK–lysine LINK endpoint to Lys A83 NZ.
- Keep the original declared sequence and missing-residue gaps. Do not invent coordinates, shorten the sequence or change chemistry to satisfy an assumed identifier-format restriction. Save the source-to-prepared map and verify one-to-one atom correspondence before generation.
- Preserve the nine specified catalytic heavy atoms and catalytic amino-acid identities during generation. Retain all ligand atoms needed to describe the LLK chemical state and map any covalent linkage explicitly.
- Resolve alternate locations and select the LLK instance corresponding to chain A; record occupancies and selection rationale. Do not combine atoms from incompatible conformers.
- Keep conditions with buried versus unconstrained ligand exposure separate. Record the intended exposure condition for every generated backbone.
- Keep the catalytic lysine fixed during sequence design and exclude lysine at newly designed nonmotif positions. Verify the resulting sequences rather than assuming constraints were applied.
- Assign multiple sequences per backbone and assess their structures from sequence without copying catalytic coordinates into the prediction. Preserve backbone→sequence→prediction relationships.
- After sequence assignment, calculate active-site and global structural agreement and catalytic-lysine/ligand solvent exposure as supporting eligibility checks. Declare acceptance rules before evaluation without adjusting them to outcomes.
- Prepare six assessment states: apo, noncovalent substrate complex and four carbinolamine stereoisomers. Target 50 independent samples per state; identify reduced sampling explicitly.
- Do not count samples for which a chemical state, catalytic atom mapping or substrate connectivity could not be established. Retain such failures in the ledger.

## Workflow

| Stage | Capability | Expected evidence |
| --- | --- | --- |
| Prepare inputs | Prepare the minimal motif, LLK analogue and state-specific chemical models; save explicit connectivity and source atom mappings. | Verified motif, ligand/state topologies and source-to-prepared maps. |
| Generate candidates | Generate new backbones for the declared length/exposure conditions, assign sequences and refine under the catalytic constraints. | Mapped scaffolds, full-length sequences and generation/refinement settings. |
| Check structural recovery | Predict sequences independently and check fold recovery, catalytic identities, motif recovery, solvent exposure and ligand compatibility. | Independent predictions, fold/motif correspondence and exposure checks. |
| Assess reaction states | Generate the six state ensembles and retain every sample with its parent sequence and state. | Per-state ensembles and complete sample/chemical-state ledgers. |
| Compare and select | Calculate the requested structural measurements and select candidates with the predeclared rule. | Individual measurements, uncertainty, selection decisions and raw outputs. |

## Evaluation Metrics

| Property | Required calculation | Reporting scope |
| --- | --- | --- |
| Catalytic-site recovery | Per-catalytic-residue sidechain heavy-atom RMSD from the design. | Report alignment, atom selection and averages for each state. |
| Active-site flexibility | Within-ensemble sidechain RMSF for each catalytic residue. | Report ensemble alignment, all samples and state-level summaries. |
| Substrate interaction occupancy | Fraction of samples supporting the defined substrate–catalytic-residue hydrogen bonds. | Record donor/acceptor selections, geometric predicate and denominator; apo substrate interactions are not applicable. |
| Structural novelty | TM-score to structurally similar known proteins. | Distinguish a fixed-pair alignment from a nearest-neighbour database search; retain database version, matching chains and normalization. |

Report every individual observation with candidate/system ID, chemical state, method/version, units or native score scale, parameters, sampling, uncertainty where applicable, and raw-artifact path. Keep per-state and per-cohort results distinct from pooled summaries. Declare alignment, equivalent-atom handling and score normalization before assessment. Missing or incompatible results remain explicitly unavailable.

## Expected Output

**Format:** `enzyme_computational_bundle`\
**Directory:** `08_results/task_001_rfdiffusion2_retroaldolase/<run_id>/`

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
