# Task 004 — Reproduce serine-hydrolase filtering and multistate assessment

## Objective

Reproduce the computational fold filters and reaction-state ensemble analysis of a selected serine-hydrolase design cohort. Compare per-design computational outputs first; retain laboratory activity and structures as separate validation context.

## Publication and sources

[Lauko et al., Computational design of serine hydrolases, Science 388, eadu2454 (2025)](https://doi.org/10.1126/science.adu2454). Use Methods/Filtering, the PLACER analysis, and supplementary definitions for the selected design round.

The [author repository](https://github.com/laukoag/serine-hydrolase-design) documents motif generation, RFdiffusion, repeated LigandMPNN/FastRelax, AlphaFold2 assessment, and PLACER state analysis. Recover the [archived release](https://doi.org/10.5281/zenodo.14642126) and paper-specific configuration before execution.

## Inputs

| Input | Required identity |
| --- | --- |
| Design cohort | One source-defined round, substrate, motif type, and prediction regime |
| Motifs and constraints | Catalytic atom maps, substrate parameters, and geometry restraints |
| Sequences/models | Exact identities and all available prediction outputs |
| State models | Apo, substrate-bound, TI1, acyl-enzyme intermediate, and TI2 representations |
| Reference computations | Per-design confidence/RMSD scores, ensemble geometry statistics, and filter counts |

Choose one cohort before expanding. Keep standard single-sequence prediction separate from later template-assisted prediction. Do not merge substrates or rounds with different selection criteria into one success rate.

## Published computational pipeline

1. Build catalytic motifs with the chosen nucleophile, acid/base interactions, and oxyanion-hole geometry.
2. Generate and refine protein backbones around those motifs.
3. Run three LigandMPNN/FastRelax cycles with the declared catalytic identities and geometry constraints.
4. Screen relaxed models for motif recovery and substrate-pocket compatibility.
5. Predict structures with the source AlphaFold2 regime.
6. Apply the published confidence and global/local RMSD filters.
7. Generate PLACER ensembles for the five chemical states.
8. Evaluate the specified hydrogen bonds and catalytic geometry in every ensemble member.
9. Apply the round-specific state-compatibility analysis and preserve the surviving cohort.

The repository describes the iterative design steps and the distinction between ordinary prediction and initial-guess/template-assisted runs. [Author pipeline](https://github.com/laukoag/serine-hydrolase-design)

## Computational reference results

| Quantity | Published value | Type/source |
| --- | --- | --- |
| Global Cα RMSD to design | <1.5 Å | AlphaFold2 filter |
| Mean pLDDT | >75, on the 0–100 scale | AlphaFold2 filter |
| Catalytic-residue Cα RMSD | <1.0 Å | AlphaFold2 filter |
| Prediction regime for standard runs | Model 4, three recycles | Method setting |
| State ensemble | 50 models per state for five states | PLACER setting |
| Spatial crop | 600 atoms near the active site | PLACER setting |
| Per-design scores and contact frequencies | Extract from source output/supplement | Required computed baseline |
| Round-specific surviving counts | Recover corresponding cohort records | Required aggregate baseline |

These definitions are reported in [Methods/Filtering and PLACER analysis](https://pmc.ncbi.nlm.nih.gov/articles/PMC12288761/). Thresholds and sampling settings alone are not measured success rates; retrieve the actual score distributions and cohort counts before claiming reproduced performance.

## Reproduction and comparison

Use the [shared procedure](README.md#how-to-execute-a-task).

1. Freeze the design round, sequence/model bindings, prediction information, and state chemistry.
2. Recalculate the published global and catalytic-residue RMSDs using identical alignment/atom definitions.
3. Repeat prediction on the selected published sequences and compare confidence, RMSD, and filter decisions.
4. Generate every declared state ensemble with the specified seeds/sample count.
5. Recompute each source-defined contact/geometry statistic for every model.
6. Compare per-state frequencies, distributions, and round-specific retention against source values.
7. Report missing atoms, invalid chemical states, failed ensemble members, and unresolved source rows.

Preserve all ensemble members; choosing one favorable model does not reproduce a frequency-based assessment. Keep a coordinate-conditioned state ensemble separate from an independent sequence-input folding calculation.

## Execution requirements

Verify that the connected PLACER service exposes the paper's multistate ensemble functionality. A ligand-placement service with a similar name may implement a different operation. Record exact models, state connectivity, conditioning, and outputs.

Apply the [platform policy](../MODELS_AND_TOOLS.md). Unavailable original implementations or template controls must be recorded before a supported adaptation is compared. A reduced ensemble is a different sampling condition.

Use the released evaluation definitions and applicable reference controls. Test atom mapping, state bonds, and geometry calculations independently before scoring. Do not add a new arbitrary cutoff to obtain a passing cohort.

## Expected outputs and acceptance

Return source/sequence/state manifests, software and parameter records, native predictor scores, all state-ensemble outputs, per-model geometry, per-state statistics, cohort filter decisions, and a published-versus-calculated table.

A comparable result preserves the prediction regime, chemical representations, atom selections, and denominator. Distinguish reproduction of a filter predicate from reproduction of the observed pass rate. Matching structural-state analysis does not establish a reaction free-energy barrier.

## Experimental context

The study reports maximum measured efficiency of 4.3×10³ M⁻¹s⁻¹ and experimental structure agreement below 1 Å Cα RMSD. [Paper](https://pmc.ncbi.nlm.nih.gov/articles/PMC12288761/) These remain supporting observations with their original construct identities; neither is the primary computational target.
