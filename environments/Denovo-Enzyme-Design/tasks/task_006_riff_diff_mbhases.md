# Task 006 — Reproduce Riff-Diff MBHase computational results

## Objective

Repeat the computational workflow for the published Morita–Baylis–Hillman designs and compare per-design predicted-structure and catalytic-array metrics. Keep the two source catalytic-array cohorts separate.

## Publication and sources

[Braun et al., Computational enzyme design by catalytic motif scaffolding, Nature 649, 237–245 (2026)](https://doi.org/10.1038/s41586-025-09747-9). The MBH section identifies computational metrics in Supplementary Fig. 12 and sequence records in Supplementary Table 6.

Use the [author pipeline](https://github.com/mabr3112/riff_diff_protflow), [catalytic arrays](https://doi.org/10.5281/zenodo.15979364), and [design models](https://doi.org/10.5281/zenodo.15494858). Recover the distinct BH32.14-derived and BH1.8-derived configurations.

## Inputs

| Input | Required information |
| --- | --- |
| Source catalytic arrays | Exact atoms, residue identities, rotamers, and array family |
| Reactants/model ligand | Source chemical structures, connectivity, and coordinate representations |
| MBH candidate cohort | Sequences, generated models, and prediction identities |
| Supplementary Fig. 12 data | Actual per-design computational values and metric definitions |
| Supplementary methods and code | Scoring, prediction, generation, sequence/refinement, and sampling settings |

Verify canonical-residue, cofactor, and assembly scope for the selected input. Do not substitute a residue or remove a component and retain the original task identity. Keep a crystallographic analogue distinct from the ligand used in the published computation.

## Published computational pipeline

The Riff-Diff implementation provides the following method sequence; recover its MBH-specific parameterization from the source supplement. [Author code](https://github.com/mabr3112/riff_diff_protflow)

1. Prepare artificial motifs for the selected MBH catalytic array.
2. Generate backbones with the source pocket/channel construction.
3. Assign sequences with the declared catalytic identities fixed.
4. Iterate constrained refinement, sequence design, and structural prediction.
5. Apply the selected final ligand-interaction/sequence-design branch.
6. Predict final structures with AlphaFold2.
7. Calculate the MBH cohort's structure-quality and active-site metrics.
8. Rank/filter according to the published computational procedure and inspect substrate access.

The chemical context is a multi-reactant coupling. Reproduce the actual modeled representation; do not invent a two-ligand docking stage if the original calculation used a different representation.

## Computational reference results

| Quantity | Source of the computational baseline | Required comparison |
| --- | --- | --- |
| Per-design prediction confidence | Supplementary Fig. 12 and corresponding data | Same predictor/settings and aggregation |
| Catalytic-array recovery/structure metrics | Supplementary Fig. 12 and metric definitions | Same atoms, alignment, and coordinate version |
| Energy metrics included in that panel | Extract exact native labels/units from the source | Compare only the metrics actually reported |
| Computational filtering/selection | Source workflow records | Same cohort, denominator, and selection definition |

The main article points to the supplement rather than providing a complete numerical MBH computational table. [MBH results](https://pmc.ncbi.nlm.nih.gov/articles/PMC12727513/) Extract that table from raw source data or carefully annotated figure values before claiming numerical reproduction. Do not insert a guessed pLDDT/RMSD threshold.

The published 0.78 Å backbone and 1.07 Å sidechain RMSDs for MBH48 are comparisons to a crystal structure. They belong to experimental structural validation, not the primary predicted-model baseline.

## Reproduction and comparison

Use the [shared procedure](README.md#how-to-execute-a-task).

1. Recover Supplementary Fig. 12, its underlying values where available, and all metric definitions.
2. Bind reference values to exact MBH design IDs and sequences.
3. Freeze the array family, computation versions, sample counts, and evaluator.
4. Recalculate released-model scores to establish a consistent analysis implementation.
5. Repeat prediction/scoring on published sequences and compare values and selection decisions.
6. Rerun the scaffold/sequence workflow separately if full generation is selected.
7. Compare each array cohort independently, then summarize only after preserving its distinct protocol.
8. Report extraction uncertainty, invalid predictions, and any unrecoverable source values.

For numerical metrics, report signed and absolute differences, precision, and uncertainty. For selection, report pass/fail agreement only after reproducing the actual rule. If only final selected designs are released, do not infer a whole-campaign retention rate from that selected subset.

## Execution requirements

Inspect the actual platform interfaces for the source motif and ligand representation, fixed sequence identities, and the chosen refinement/prediction methods. A generic docking result is not automatically a replacement for the paper's final assessment.

Apply the [tool policy](../MODELS_AND_TOOLS.md). Mark method replacements as adaptations. A failure to recover supplementary numerical baselines prevents a quantitative result for that endpoint, while input recovery and supported calculations can still be reported.

Keep results and receipts in a separate experiment directory. Do not expand the reproduction into unreported chemistry/property calculations and then describe those as published pipeline steps.

## Expected outputs and acceptance

Return exact source references, a machine-readable supplementary computational table, source-bound sequences/models, the recovered pipeline settings, raw outputs, per-design calculated values, and a comparison report separated by catalytic array.

A comparable result requires a recovered numerical baseline and matching metric definitions. This task cannot be completed quantitatively using only the published enzyme activities or crystal RMSDs.

## Experimental context

MBH18 and MBH48 have reported measured kcat values of 0.0077 and 0.025 min⁻¹. [Primary study](https://pmc.ncbi.nlm.nih.gov/articles/PMC12727513/) These values can accompany the computational results as context for the original constructs. They are not targets for this first reproduction.
