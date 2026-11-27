# Decisions and recovery record

## Stage 1 freeze
Parent = 1BLI chain A (483 aa, engineered N190F/Q264S/N265Y), catalytic D231/E261/D328 verified in PDB numbering; 3 Ca2+ + 1 Na+ retained; no disulfides; maltose proxy. Mask of 18 surface positions; 27 protected positions. Primary endpoint tmPred_enzymes via Enzymes; conditions frozen in RUN_PLAN.json before generation.

## Specialist receipts
- enzyme-method (intermediate): method_route.md, deleg_a6775571/task-0, completed, 39 api_calls, tokens in/out 2,889,414/41,420.
- enzyme-recovery (intermediate): generation_diagnosis.md, deleg_5b036295/task-0, completed, 29 api_calls, tokens in/out 2,386,941/55,996.

## Generation failure and recovery (evidence-linked)
- Random_Controlled_Mutagenesis (6b07f3b4c45f4015f0eb82c7): 12 sequences, 347-452 substitutions, lengths 473-495. Task-ineligible: violates 483 length, <=8 substitutions, protected positions. Root cause: mutaions_per_epoch is a per-round mutation rate with no total cap; indices only protects 27 sites, does not restrict editing to the mask. No corrective payload can enforce the budget.
- Ligand_MPNN (6b07f3bc7fb17f3eac9ce8b5): 8 sequences, 185-208 substitutions, length 481 (first two residues lost), catalytic E261/D328 edited in 2 draws. Task-ineligible; no mask/fixed-position field in contract.
- Recovery decision: try AntiBMPNN (6b0806727fb17f3eac9cf661) with explicit one-based residue_positions_to_design mask on the full 483-residue AF model. This is an antibody-conditioned model applied off-label to an enzyme; partial-validation warning recorded. Accept output only if length 483, edits within mask, <=8 substitutions, all protected residues unchanged. If it fails, generation remains an unresolved blocker and no improvement will be claimed.

## Baseline result
Parent tmPred_enzymes 51.934 degC (replica std 5.989), NetsolP soluble 0.575 / usable 0.445, CatPred kcat proxy 101.269 s^-1, pLDDT 98.5/pTM 0.957, MolProbity clashscore 5.67/Rama outliers 0%. ThermoMPNN per-position ddG table saved for evidence-driven mask refinement. All are computational predictions, not measured high-temperature activity or Tm.

## Catalytic_Geometry recovery (stage 7)
Job 6b0827cf1715676d0340bb53 (input_source='mutagenesis') FAILED terminal validation: 'mutagenesis output is not ready for catalytic geometry: the archive contains sequences but no all-atom reaction structure. Required next stages: all_atom_structure_prediction, ligand_or_cofactor_placement, entity_mapping_export, catalytic_geometry'. Diagnosis: the 'mutagenesis' source adapter expects a sequence archive from the mutagenesis tool, not a structure ZIP. Corrected attempt uses the documented 'generic' adapter on the same all-atom model ZIP; measurement_only mode, same user-defined template/binding. This is a contract-driven correction, not a repeat of an identical request. If it fails, catalytic geometry stays unresolved and no catalytic pass/fail claim is made.
