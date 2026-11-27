# Diagnosis: two task-ineligible generation outputs (intermediate, read-only review)

Frozen target: PDB 1BLI chain A, 483 aa, protected 27 (incl. catalytic D231/E261/D328),
editable mask 18, <=8 substitutions/variant, length exactly 483, <=24 unique incl. parent,
MLDE excluded. No jobs submitted in this review.

## 1. Random_Controlled_Mutagenesis (6b07f3b4c45f4015f0eb82c7, accepted+completed)

Submitted payload (jobs.json): seq=parent(483), n_samples=12, file_format="csv",
indices=27 zero-based protected, mutaions_per_epoch=4 (API typo, required spelling).

Observed (CSV): 12 sequences, lengths 473-495; pairwise alignment to parent:
110-163 substitutions + 15-72 insertions/deletions per sequence (~60% identity).
Protected positions were mostly preserved (26-27 of 27 aligned), so `indices` behaved
as the current canonical contract says ("zero-based protected positions excluded from
mutation"). NOTE contract drift: the maintained source record
`contract_sources/standardization-record.v1.json` describes `indices` as "Positions to
mutate (e.g. [5,10])" — the opposite meaning. Not the cause of this failure.

Failure cause: no contract field bounds the TOTAL number of mutations or preserves length.
`mutaions_per_epoch` (limits 1-109) is a per-round rate; worker applies many rounds,
so `mutaions_per_epoch=4` still produced >100 substitutions and indels. Local validator
`validate_mutagenesis` only checks indices are in range. A corrected call (e.g. value 1)
cannot guarantee <=8 substitutions or length 483. No corrected payload exists.

## 2. Ligand_MPNN (6b07f3bc7fb17f3eac9ce8b5, accepted+completed)

Submitted payload: input_path=parent_chainA_with_ions.pdb, num_sequences=8 only.
Canonical contract has exactly these two fields — no mask, fixed positions,
redesign fraction, temperature or seed field.

Observed (results.csv): 8 sequences, all 481 aa (input PDB chain A starts at residue 3,
ends 483 -> first two residues absent), ~185-208 substitutions vs parent (~60% identity).
Proper alignment: catalytic E261 edited/gapped in ids 2 and 3; D328 edited/gapped in id 3;
D231 retained in all. Length 481 alone disqualifies all 8.

Failure cause: full-chain inverse folding redesigns essentially every position; no
contract-supported way to restrict it. No corrected payload exists.

## 3. Other active catalog tools (all 130 job names reviewed)

- Function_Based_Enzyme_Generation: label(EC) + n_samples only; de novo, no scaffold/parent input. NO.
- Genzyme_Generation: substrate/product SMILES -> structures; de novo. NO.
- enzycontrol: generates enzyme BACKBONES; scaffold labels are placeholders, not designed sequences. NO.
- Enzyme_RFD3: min/max_length can force 483, but builds de novo motif scaffolds with review rejects,
  not parent+<=8 substitutions. NO.
- boltzgen, pxdesigninfer, pxdesignpipeline, ppiflow*: de novo proteins/binders/backbones. NO.
- Thermal_MPNN, stability-binding-ddg endpoint, Enzymes, etc.: predictors/scorers, not constrained generators.
- Insilico_Directed_Evolution (MLDE): position-focused library but EXCLUDED by task. NO.
- stability-binding-ddg: its wrapper DOES generate full-length variants at chosen positions
  (`sequence`, `chain`, `mutations` list of one-based positions, `num_mutations`). Passing <=8
  editable positions would yield <=8 substitutions at full length. BUT it requires a docked
  two-chain (A+B) protein complex (none available; 1BLI is monomeric with only chain A),
  and its endpoint is binding ddG with contradictory sign documentation. Off-label; not recommended.
- AntiBMPNN: documented `residue_positions_to_design` map (one-based selections, e.g. "114,123,127")
  restricts design to named positions while retaining the rest of the chain. This is the only
  active generator with an explicit, documented position-level mask. Off-label (antibody tool)
  but the schema requires only a PDB with the named chain. Best contract-supported alternative.
- Solublempnn: has `fixed_residues` + `invert_selection`, but the authorized catalog gives no
  syntax/semantics ("Use the exact source field"), so a mask payload cannot be composed reliably
  without a validation run. Secondary candidate.

## 4. Decision

No corrected call to either failed tool can satisfy the frozen constraints.
The only plausible contract-supported alternative is a small AntiBMPNN validation run:

experiment_data (parent submits):
  input_path = uploaded structure_evidence/BLA_1BLI_parent.pdb (483 residues numbered 1-483)
  chains_to_design = ["A"]
  residue_positions_to_design = {"A": "114,123,126,127,128"}   (<=8 editable positions)
  generation_count = 8
(Do NOT use parent_chainA_with_ions.pdb / 1bli.pdb: both start at residue 3 -> 481 aa output.)

Verification gates on returned FASTA/CSV before any screening:
  1. length == 483 for every sequence;
  2. align to parent: substituted positions subset of editable mask, count <=8;
  3. D231/E261/D328 and all 27 protected positions identical to parent;
  4. deduplicate and keep cumulative unique (incl. parent) <=24;
  5. confirm non-designed positions retained parent identity (spot-check full alignment).
If any gate fails, discard the output; do not treat a platform "Success" as eligibility.

If the AntiBMPNN validation run is rejected or violates a gate, no remaining active tool can
generate the required constrained variants. Then document an unresolved generation blocker and
continue the independent evidence stages (parent baselines, structural/quality/function checks)
with honest negative reporting; do not silently substitute the ineligible sequences.
