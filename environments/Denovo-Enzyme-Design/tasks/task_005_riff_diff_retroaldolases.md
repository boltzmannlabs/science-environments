# Task 005 — Reproduce Riff-Diff retro-aldolase computational results

## Objective

Reproduce the motif-to-design workflow and computational evaluation of the published RAD cohort. Compare predicted-structure metrics, structural novelty, and dynamics before using experimental activity as secondary validation.

## Publication and sources

[Braun et al., Computational enzyme design by catalytic motif scaffolding, Nature 649, 237–245 (2026)](https://doi.org/10.1038/s41586-025-09747-9), online in 2025. Relevant sources are Supplementary Fig. 1, Fig. 4, supplementary metric definitions, and the molecular-dynamics Methods.

Retrieve the [catalytic arrays](https://doi.org/10.5281/zenodo.15979364), [design models](https://doi.org/10.5281/zenodo.15494858), and [author implementation](https://github.com/mabr3112/riff_diff_protflow). The reference motif comes from RA95.5-8F, PDB 5AN7.

## Inputs

| Input | Required information |
| --- | --- |
| Catalytic tetrad and artificial motifs | Atom selection, rotamers, backbone fragments, and ligand identity |
| RAD cohort | Original sequences, models, and candidate-to-backbone/motif relationships |
| Prediction/scoring records | Per-design pLDDT, active-site RMSD, Rosetta scores, and associated definitions |
| Dynamics inputs | Topologies, protonation, force field, water/ions, equilibration and sampling |
| Complex/intermediate assessment | Published substrate and covalent-state representations and metric formula |

Create a stable join between each design, sequence, prediction, and metric row. Keep generation, restrained refinement, independent prediction, and later complex assessment as separate coordinate versions.

## Published computational pipeline

The [released implementation](https://github.com/mabr3112/riff_diff_protflow) connects these operations:

1. Build artificial motif libraries from catalytic functional groups and compatible fragments.
2. Generate scaffolds with a pocket/channel construction and the source custom potential.
3. Assign sequences with LigandMPNN.
4. Refine the backbone/catalytic arrangement with constrained FastRelax.
5. Redesign sequences and assess them with ESMFold through iterative cycles.
6. Refine ligand interactions through the selected CoupledMoves or final LigandMPNN branch.
7. Predict final structures with AlphaFold2 and calculate design metrics.
8. Evaluate dynamics and substrate/intermediate geometry through the separately described assessment protocols.

Recover branch choices and settings for the selected cohort from the supplement; do not merge alternate final sequence-design routes.

## Computational reference results

| Quantity | Published reference | Comparison |
| --- | --- | --- |
| Mean maximum TM-score to PDB for the selected RAD cohort | 0.49 | Match the cohort, structure-search library, and score definition |
| Predicted pLDDT, active-site RMSD, Rosetta energy | Supplementary Fig. 1 | Extract per-design numeric data before comparison |
| Apo-state MD sampling | 20 replicas ×20 ns | Match the protocol; sampling is not an outcome |
| Catalytic dynamics | Fig. 4c, RMSF and interaction deviations | Recover values/distributions from source data or annotated figure extraction |
| Bound/intermediate active-site metric | Supplementary formula and Fig. 4d | Compare per-design computed values first |

The cohort novelty value and computational analyses are described in the [primary article](https://pmc.ncbi.nlm.nih.gov/articles/PMC12727513/). Do not replace predicted-structure scores with design-to-crystal RMSDs.

## Reproduction and comparison

Follow the [shared procedure](README.md#how-to-execute-a-task).

1. Recover the complete per-design computational table, distinguishing raw data from figure estimates.
2. Recalculate metric values on released models to test mapping and scoring independently of stochastic generation.
3. Repeat the original prediction protocol for published sequences; compare local/global agreement and confidence.
4. Recompute structural novelty with the historical library, or label a current-library search separately.
5. Reproduce the MD/state assessment where supported and compare per-residue/per-design distributions.
6. Rerun the generative workflow as a separate cohort if generation is part of the selected reproduction.
7. Report per-stage retention and all failures at matched budgets.

The source MD protocol uses GROMACS 2023.4, amber99sb-ildn, and SPC/E; recover the remaining setup and equilibration parameters from Methods before execution. [MD Methods](https://pmc.ncbi.nlm.nih.gov/articles/PMC12727513/) Another engine or force field defines an adapted condition.

Freeze coordinate alignment, averaging, replicas, and the active-site formula before scoring. If reference data exist only as plots, document the extraction and its uncertainty. Matching a cohort mean cannot establish per-design agreement.

## Execution requirements

Verify source custom-potential/refinement support in the permitted platforms. Do not patch local inference to imitate the paper. Preserve input and output versions at every iteration.

Apply the [tool policy](../MODELS_AND_TOOLS.md). Mark unavailable original tools and method substitutions explicitly. Coordinate-conditioned complex/intermediate assessments are different from independent sequence-only folding.

The initial comparison concerns published computational metrics. Any newly fitted ranking model is a distinct development activity and cannot be evaluated on its own training cohort.

## Expected outputs and acceptance

Return the source/model manifest, recovered per-design baseline, settings, native computational outputs, comparison tables for each metric, cohort summaries, sampling uncertainty, and resource accounting.

Report which stages and values are numerically comparable, which use different methods, and which remain missing. No arbitrary activity threshold is part of this computational reproduction.

## Experimental context

The paper reports activity above background for 32/35 expressed designs and a Spearman correlation of −0.64 between an active-site metric and measured rates. [Results](https://pmc.ncbi.nlm.nih.gov/articles/PMC12727513/) The correlation is a mixed computational/experimental validation statistic. Reproducing it is secondary to reproducing the computational metric itself.
