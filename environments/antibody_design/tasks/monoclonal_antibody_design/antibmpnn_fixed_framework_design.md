# Task: huj3_gp120_fixed_framework_design

## Description

Design humanized J3 (huJ3) VHH variants against HIV-1 C1086 gp120 while preserving the parent framework sequence and canonical backbone. Evaluate the generated candidates using only three physicochemical predictions: residue-volume descriptors, hydrophilicity descriptors, and net charge.

Calculate the same properties for the native parent under matched conditions. Choose suitable computational methods independently and retain actual calculation outputs for later comparison.

## Target

**Target:** HIV-1 C1086 gp120\
**Reference Antibody:** The supplied 121-residue humanized J3 parent\
**Binding Region:** J3-associated gp120 interface\
**Structure and Context:** PDB 7RI1 polymer entity 1, author chain A\
**Reference Inputs:** Supplied parent sequence, native antigen coordinates and construct sequence, residue mapping, and a sequence-matched parent structural model\
**Antibody Format:** Single-domain VHH\
**Objective:** Generate constrained CDR variants and predict their residue-volume descriptors, hydrophilicity descriptors, and charge

## Design Constraints

- Use this native parent input sequence:

  ```text
  EVQLVESGGGLVQPGGSLRLSCAASGSIFNQYAMAWFRQAPGKEREFVAGMGAVPHYGEFVKGRFTISRDNSKNTVYLQMNSLRAEDTAVYYCARSKSTYISYNSNGYDYWGQGTLVTVSS
  ```

- The antibody deposited in 7RI1 differs from this humanized parent. Preserve the supplied parent sequence outside the permitted design positions.
- Build or validate a sequence-matched parent structure, then freeze it as the canonical backbone before design.
- Use one-based parent positions. Run separate configurations allowing edits at CDR1 positions **26–33**, or CDR3 positions **97, 101, 103, 104, 105, and 106**.
- Preserve every other residue, including positions **98–100**, and retain the parent sequence length.
- Preserve the canonical backbone and framework identities. Record protected-position and coordinate-preservation checks as input/design validity checks.
- Keep the antigen construct, numbering, missing-residue treatment, and parent/candidate calculation conditions consistent.
- Declare generation budget, sampling settings, selection rule, descriptor definitions, and charge-calculation conditions before inspecting results.

## Computational Tool Capabilities

Choose suitable available capabilities independently. If a required capability is missing, use an appropriate open-source implementation and execute the calculation. Record actual methods and versions in the output.

| Stage | Capability | Expected Evidence |
| --- | --- | --- |
| 1. Prepare inputs | Retrieve and validate native inputs, map residues, and establish the frozen parent backbone. | Input sequences, coordinates, residue maps, preparation notes, and hashes. |
| 2. Generate candidates | Generate complete sequences within each permitted edit mask using the fixed structural context. | Candidate sequences, canonical structures, edit traces, and actual generation settings. |
| 3. Check design validity | Verify protected identities, sequence length, framework preservation, and duplicate handling. | Validity decisions and reasons for exclusions. |
| 4. Predict physicochemical properties | Calculate the three requested properties for each generated candidate and the native parent. | Region-specific descriptor and charge records, calculation conditions, and raw outputs. |
| 5. Compare and report | Apply the predeclared selection rule and summarize candidate-minus-parent differences. | Complete measurements, shortlist, exclusions, and unresolved calculations. |

## Evaluation Metrics

| Property | Required Prediction | Calculation Scope and Reporting |
| --- | --- | --- |
| Residue-volume descriptor | Calculate the physical-descriptor component representing residue volume. | Report CDR1 and the full CDR3 analysis segment separately. Record the amino-acid coefficient table, normalization, aggregation rule, and descriptor scale. This descriptor must remain distinguishable from a geometric molecular-volume calculation. |
| Hydrophilicity descriptor | Calculate the physical-descriptor component representing hydrophilicity. | Use the same segment boundaries and descriptor definition for parent and candidates. Record the coefficient table and normalization; identify any alternative hydropathy measure separately. |
| Net charge | Calculate segment charge under the declared physiological-pH condition. | Record the exact pH, ionization constants, terminal-group treatment, method, and charge in elementary-charge units. Use identical conditions for parent and candidates. |

Use one-based positions **26–33** for CDR1 analysis and **94–110** for the full CDR3 analysis segment. Keep calculations over the designable mask separate from calculations over the full segment. Whole-antibody descriptors may be supplied separately, with their scope clearly labeled.

For every property, retain the candidate result, freshly calculated parent result, difference, units or descriptor scale, calculation conditions, method version, sequence hash, and raw-artifact path. Missing results must remain explicitly unavailable. Do not assume that increasing or decreasing a descriptor is beneficial without a declared objective.

## Expected Output

**Format:** `antibody_design_bundle`\
**Directory:** `08_results/huj3_gp120_fixed_framework_design/<run_id>/` outside the task-definition directory

- `designed_sequences.fasta`: generated full-length candidate sequences with configuration identifiers.
- `property_predictions.csv`: candidate and parent property results, segment boundaries, differences, units/scales, conditions, and missing-result status.
- `metrics.json`: the three requested property predictions, input/design validity checks, methods, parameters, hashes, and exclusions.
- `shortlist.csv`: eligible unique candidates selected using the declared property-based rule.
- `report.md`: input preparation, actual execution, property comparisons, selection rationale, and limitations.
- Supporting structures, residue maps, native calculation outputs, and execution logs.

## Important Instructions

- Use actual calculations. Keep all generated sequences traceable to the native parent and their permitted edits.
- Use only the three listed physicochemical properties as comparison objectives.
- Do not consult prior designed candidate sequences, output mutation lists, historical rankings, or precomputed outcome tables during generation or selection.
- Keep generated outputs frozen before an independent evaluator performs later comparisons.
- Record actual calculation definitions and conditions so subsequent comparisons can establish whether the same quantities were evaluated.
- Run long calculations in a persistent screen session with logging enabled and record how to attach to it.
- Keep execution artifacts outside this task-definition directory and preserve native inputs.
