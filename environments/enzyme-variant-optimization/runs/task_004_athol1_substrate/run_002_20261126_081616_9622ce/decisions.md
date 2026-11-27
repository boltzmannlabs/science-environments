# Decisions — task_004_athol1_substrate (agent_with_specialist)

## Specialist receipts
- enzyme-method planning report: `planning_report.md` (intermediate; no jobs). Route: CatPred endpoint + Boltz2/MolProbity/Catalytic_Geometry structures + Random_Controlled_Mutagenesis generation + Thermal_MPNN/Netsolp/Enzymes screen.
- enzyme-recovery (Boltz2): `native_receipts/recovery_boltz2.md`. Worker affinity-precompute failure, not payload; no resubmission. Protein-only retry also failed (empty PDB).
- enzyme-recovery (generation): `native_receipts/recovery_generation.md`. Task-ineligible RCM output; deterministic edit-list extraction under stated conditions.

## Failure / recovery log
1. Boltz2 doc 6b07ed071715676d03408b6d (protein+SAH+CCI): terminal `failed`, worker FileNotFoundError `pre_affinity_1.npz`, safe_to_retry=false. Worker infrastructure; no resubmission.
2. Boltz2 doc 6b07f19fc45f4015f0eb8206 (protein-only test): terminal `failed`, empty PDB. Boltz2 unusable for this task.
3. Random_Controlled_Mutagenesis doc 6b07f1a77fb17f3eac9ce690: Success but output ineligible (lengths 228-242, ~77-140 substitutions, indels). `mutaions_per_epoch` is per-round not a total cap; no documented field enforces <=8 substitutions/length 235.
4. Recovery: deterministic difflib alignment (autojunk=False) extracted concat-only mismatches at editable positions, first 8 ascending, applied to exact 235-aa parent. 8 derived reconstructions R1D0-R1D7 with full lineage; none is presented as a native full-length output.

## Round-1 shortlist rule (FROZEN before outputs)
Retain variants with protected positions unchanged, <=8 substitutions and no severe stability/solubility flag; rank by CatPred predicted kcat; shortlist top 3 for reaction-complex assessment.

## Round-1 observation -> revision decision (stage 6)
All 8 round-1 variants have LOWER predicted kcat than parent (best R1D5 1462.59 vs 1598.69; delta -136). R1 variants also cluster in the remote N-terminal/surface region (edits at positions 1-6, 15-22, 29-68, 92-135, 183-201) away from the SAH sulfur (5-15 A shell). Thermal Tm and Netsolp solubility are near parent for all, so the deficit is endpoint-specific, not an obvious folding collapse.
DECISION: change strategy from broad surface mutagenesis to a RESULTS-DRIVEN focused second-shell design. Restrict editable positions to the 9-15 A shell around SAH SD (72 positions identified from 3LCC geometry, see shell list in shell2_calc) while keeping all first-shell/cosubstrate/catalytic/tag positions protected; generate a new batch with the same native tool but a narrowed `indices` mask. Testable expectation: substitutions closer to the bound cosubstrate/alkyl pocket have a higher chance of altering the predicted turnover endpoint than remote surface substitutions. This is revision round 1 of at most 2.

## Structure/geometry evidence limitation
Boltz2 unusable; no de novo candidate complex structures. Parent 3LCC (with SAH bound) is used as the parent reactant reference. Candidate complexes will be assembled as SEQUENCE-THREADED SURROGATES on the parent SAH-bound scaffold with ethyl iodide placed by native docking/geometry tools where available; these are explicitly NOT de novo predictions and are labelled surrogates in structure_evidence/.
