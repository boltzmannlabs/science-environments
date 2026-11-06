# Task: vhh_ha_rsv_fixed_framework_design

## Description

Design VHH candidates against influenza hemagglutinin and respiratory syncytial virus fusion protein site III. Run separate antigen campaigns while preserving the parent framework sequence and internal framework backbone geometry.

Evaluate only aggregation propensity, humanness, interface interaction energy, and predicted cross-target specificity. Choose suitable computational methods independently and retain actual results for later comparison.

## Target

**Targets:** Influenza hemagglutinin and RSV fusion protein site III\
**Reference Antibody:** PDB 3EAK chain A, observed variable-domain residues 1–127\
**Binding Regions:** Hemagglutinin B521, B545, and B552 in 5VLI; the interprotomer region containing A305 and B456 in 7LUC\
**Structure and Context:** 5VLI antigen chains A and B; 7LUC antigen chains A, B, and C\
**Reference Inputs:** Native scaffold sequence and coordinates, antigen records, and verified chain/residue mappings\
**Antibody Format:** Single-domain VHH\
**Objective:** Generate constrained CDR variants and predict aggregation propensity, humanness, interface interaction energy, and cross-target specificity

## Design Constraints

- Extract the observed variable domain from 3EAK chain A; exclude duplicate scaffold chains and cloning tags.
- Use one-based parent positions for native design regions: CDR1 **26–35**, CDR2 **55–60**, and CDR3 **102–117**. Preserve every framework residue outside these regions.
- Request output loop lengths of **7**, **6**, and **5–13 residues**, respectively. Map protected residues explicitly when loop lengths change.
- Preserve framework sequence and internal framework backbone coordinates. Whole-antibody rigid-body movement is permitted. Declare the coordinate-preservation tolerance before evaluation.
- Use the specified native antigen chains and verify target sites against author residue numbering. Record missing regions, modifications, and preparation choices.
- Keep canonical designs separate from any assessment structures prepared for interface scoring. Do not change canonical framework coordinates during scoring preparation.
- Declare the generation budget, property definitions, comparison panel, and selection rule before inspecting results.
- Assess HA candidates against RSV and RSV candidates against HA as the minimum cross-target comparison. Record any additional native decoy targets.

## Computational Tool Capabilities

Choose suitable available capabilities independently. If a required capability is missing, use an appropriate open-source implementation and execute the calculation. Record actual methods and versions in the output.

| Stage | Capability | Expected Evidence |
| --- | --- | --- |
| 1. Prepare inputs | Retrieve native scaffold and antigen structures and verify chain/residue mappings. | Sequences, coordinates, preparation records, and input hashes. |
| 2. Generate candidates | Generate CDR sequences and conformations while preserving the framework sequence and internal backbone geometry. | Candidate sequences, canonical structures, edit traces, and generation settings. |
| 3. Check design validity | Verify permitted edits, loop lengths, framework preservation, and sequence–structure correspondence. | Validity decisions and reasons for exclusions. |
| 4. Predict aggregation and humanness | Calculate spatial surface aggregation propensity and human-repertoire-based sequence humanness. | Candidate-level property outputs, residue-level contributions where supported, and calculation definitions. |
| 5. Assess target and decoy interactions | Prepare antibody–antigen poses and calculate matched interface energies and cross-target interaction profiles. | On-target and decoy assessment structures, energy outputs, specificity profiles, and panel coverage. |
| 6. Compare and report | Apply the predeclared property-based selection rule separately for each antigen. | Complete predictions, shortlist, exclusions, and unresolved calculations. |

## Evaluation Metrics

| Property | Required Prediction | Calculation Scope and Reporting |
| --- | --- | --- |
| Aggregation propensity | Calculate a spatial surface aggregation-propensity score for each candidate. | Record the structure used, solvent-exposure treatment, residue contributions where available, aggregation definition, and native score scale. Keep sequence-only aggregation estimates separately identified. |
| Humanness | Calculate a human-repertoire prevalence-based humanness score. | Record peptide-window definition, subject-prevalence criterion, repertoire snapshot, sequence scope, and aggregation rule. Report whole-VHH and CDR-specific results where supported. |
| Interface interaction energy | Calculate the energy difference between the bound complex and separated antibody/antigen partners under one consistent scoring protocol. | Preserve the energy definition, scoring units, sign convention, partner selections, preparation/refinement conditions, and structure hash. Keep component energies when available. |
| Predicted cross-target specificity | Calculate each candidate's interaction profile against its intended target and the declared native decoy panel. | Retain per-target results, method and decision criterion, panel coverage, and on-target versus decoy comparisons. If the method supports positive-interaction classification, report positive fractions and their normalization with explicit denominators. Unsupported classifications remain unavailable. |

Record every candidate-level result, calculation method/version, units or score scale, conditions, and raw-artifact path. Summarize distributions separately for HA and RSV, retaining sample counts and the individual observations. Keep pooled summaries distinct from results for particular candidates.

Predeclare the scoring and ranking rules. Different humanness definitions, aggregation measures, interaction-energy scales, or specificity criteria must remain distinguishable during later comparisons. If a normalized specificity result has a zero denominator, report it as undefined.

## Expected Output

**Format:** `antibody_design_bundle`\
**Directory:** `08_results/vhh_ha_rsv_fixed_framework_design/<run_id>/` outside the task-definition directory

- `designed_sequences.fasta`: generated full-length VHH candidates with antigen and candidate identifiers.
- `property_predictions.csv`: aggregation, humanness, and interface-energy predictions with units/scales, calculation conditions, and missing-result status.
- `specificity_predictions.csv`: candidate-by-target predictions, target identities, scoring definitions, declared classifications where supported, and panel coverage.
- `metrics.json`: the four requested property assessments, input/design validity checks, methods, parameters, hashes, and exclusions.
- `shortlist.csv`: eligible unique candidates selected separately for each antigen using the declared rule.
- `report.md`: input preparation, actual execution, property distributions, target/decoy comparisons, selection rationale, and limitations.
- Supporting canonical designs, assessment structures, residue maps, native calculation outputs, and execution logs.

## Important Instructions

- Execute actual calculations and retain native outputs for every reported prediction.
- Use only the four listed properties as comparison objectives. Supporting structures and validity checks establish that the inputs and designs comply with the task.
- Do not consult prior designed candidate libraries, output mutation lists, historical rankings, or precomputed outcome tables during generation or selection.
- Freeze generated outputs before an independent evaluator performs later comparisons.
- Preserve method and construct differences so an evaluator can determine which quantities support direct numerical comparison.
- Run long calculations in a persistent screen session with logging enabled and record how to attach to it.
- Keep execution artifacts outside this task-definition directory and preserve native inputs.
