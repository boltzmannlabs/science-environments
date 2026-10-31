# Task 002 — Reproduce RFdiffusion2 retro-aldolase design and assessment

## Objective

Recover the published retro-aldolase computational inputs, repeat the design/assessment steps, and compare structural metrics with the released models and campaign results. Begin with the published design before comparing a newly generated cohort.

## Publication and sources

[Ahern et al., RFdiffusion2, Nature Methods 23, 96–105 (2026)](https://doi.org/10.1038/s41592-025-02975-x): retroaldolase campaign, Fig. 4a, source data, and supplementary section D. Use the [author code](https://github.com/RosettaCommons/RFdiffusion2) to recover the campaign's exact generation, sequence-design, and prediction/filter configuration.

The catalytic reference is [RA95.5-8F, PDB 5AN7](https://www.rcsb.org/structure/5AN7). Recover the actual supplied motif rather than treating the entire reference structure as the design input.

## Inputs

| Input | Required information |
| --- | --- |
| Reaction and ligand | Methodol identity/stereochemistry, products, and the modeled ligand or analogue |
| Published motif | Selected catalytic atoms and their coordinates |
| Published candidate | Exact sequence, design model, and predictor output if released |
| Computational configuration | Generation, sequence, prediction, filter, and structure-search settings |
| Reference result files | Campaign-specific computational scores and structure-comparison records |

Resolve the selected design's complete sequence and assembly. Preserve differences between the motif-source enzyme, a generated scaffold, and any analog-containing reference structure. Record atom/residue transformations and sequence-index correspondence.

## Published computational pipeline

The campaign uses motif-conditioned backbone generation, sequence assignment, structure prediction, and task-specific filtering. [Primary campaign description](https://pmc.ncbi.nlm.nih.gov/articles/PMC12791007/)

1. Extract the released catalytic functional-group arrangement from the reference.
2. Prepare the matching substrate/ligand representation.
3. Generate scaffolds with the released RFdiffusion2 campaign configuration.
4. Assign sequences while preserving the specified catalytic identities.
5. Run the campaign's structure-prediction assessment and apply its filters.
6. Compare the selected design with the reported closest reference structure.

Recover the exact predictor, settings, number of samples, and filters from the campaign supplement. Do not copy AME settings merely because it uses the same generator.

## Computational reference results

| Quantity | Published reference | Comparison requirement |
| --- | --- | --- |
| Structural similarity for the depicted design | TM-score 0.47 to 6SU3 | Recompute the same pair and normalization/search convention |
| Campaign-specific prediction confidence and motif metrics | Extract from supplementary methods/results or released output files | Bind values to the exact published design |
| Computational retention/pass counts | Recover if supplied with campaign data | Preserve original filtering stage and denominator |

The 0.47 value is a computed structural comparison, not a catalytic score. [Fig. 4a](https://pmc.ncbi.nlm.nih.gov/articles/PMC12791007/) If the campaign does not release per-design prediction scores, identify that missing baseline rather than substituting the AME success threshold or a measured activity value.

## Reproduction and comparison

Follow the [shared procedure](README.md#how-to-execute-a-task).

1. Recover and hash the published design, motif, ligand, and computational reference rows.
2. Recompute the structural comparison on the published design using the declared alignment and TM-score convention. Keep pairwise comparison and a whole-database nearest-neighbor search separate.
3. Repeat prediction/geometry assessment on the published sequence with the original information basis wherever supported.
4. Compare per-design confidence, global agreement, catalytic recovery, and clashes only where published values are available.
5. Rerun generation from the same motif under a separate identity if full design reproduction is selected.
6. Compare the new cohort's distributions, retention rates, and structural diversity with the campaign data at matched sampling.
7. Report missing samples, alternate mappings, and every method substitution.

For nearest-structure reproduction, recover the original search library and search/alignment settings. Searching today's PDB can return a closer match and therefore changes that benchmark.

## Execution requirements

Verify the actual hosted generator's motif/ligand controls and sequence designer's fixed-residue support. Preserve raw coordinates before conversion. Inspect whether the predictor uses sequence alone, templates, or other coordinates.

Use the [tool policy](../MODELS_AND_TOOLS.md). If a required original implementation is unavailable through Boltzmann/ToolUniverse, record the exact step and evaluate any supported adaptation separately. Keep full-environment qualification requirements separate from reproducing the paper's computational endpoint.

Before declaring quantitative reproduction, recover the missing campaign settings and reference score rows. If access to those data fails, return the completed model/method audit and the specific unresolved comparison.

## Expected outputs and acceptance

Return a published-design identity table, recovered settings, reference computational values with source locations, raw outputs/receipts, per-design calculated metrics, structural-search records, and a comparison report.

Separate three outcomes: reproduction of a published design's metric; reproduction of the computational filtering procedure; and results of fresh generation. Matching one does not establish the others. Use tolerances justified by rounding, implementation identity, and sampling uncertainty.

## Experimental context

The characterized published enzyme had measured kcat/KM 6.34 ± 0.92 M⁻¹s⁻¹. [Fig. 4a and text](https://pmc.ncbi.nlm.nih.gov/articles/PMC12791007/) Retain this as supporting context for that exact sequence; it is not the initial computational target and cannot be assigned to a new design.
