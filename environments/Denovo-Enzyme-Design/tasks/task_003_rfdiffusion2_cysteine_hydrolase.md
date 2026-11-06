# Task 003 — Reproduce RFdiffusion2 cysteine-hydrolase design and assessment

## Objective

Repeat the published computational workflow for the cysteine hydrolase, beginning with motif and published-model recovery. Compare calculated structural and catalytic-site metrics with their source values before considering experimental activity.

## Publication and sources

[Ahern et al., RFdiffusion2, Nature Methods 23, 96–105 (2026)](https://doi.org/10.1038/s41592-025-02975-x): cysteine-hydrolase campaign, Fig. 4b, supplementary methods, and linked source data. Recover the corresponding configuration from the [author implementation](https://github.com/RosettaCommons/RFdiffusion2).

The reaction is 4MU-butyrate hydrolysis; motif geometry was derived from [PDB 1PPN](https://www.rcsb.org/structure/1PPN). The campaign is an esterase design task. Do not replace its substrate with a peptide and call the result the same reproduction.

## Inputs

| Input | Required identity |
| --- | --- |
| Catalytic motif | Released protein/ligand atoms, catalytic mapping, and local backbone constraints |
| Ligand | Exact 4MU-butyrate conformer and any alternative modeled state |
| Published design | Sequence, generated structure, and available predicted assessment model |
| Settings and reference scores | Campaign-specific sequence/prediction/filter configuration and computed outputs |
| Structural reference | The reported nearest structure and original comparison convention |

Inspect full assembly and sequence correspondence. Distinguish source numbering from generated indices. Preserve protonation, ligand topology, and any covalent representation rather than silently converting all structures to a noncovalent pose.

## Published computational pipeline

The published method uses a catalytic motif with nucleophile/acid-base and oxyanion-hole interactions, followed by scaffold generation, sequence design, prediction, and filtering. [Primary paper](https://pmc.ncbi.nlm.nih.gov/articles/PMC12791007/)

1. Recover the reference-derived motif and the source ligand placement.
2. Prepare the exact motif constraints and generator inputs.
3. Generate backbones using the campaign configuration.
4. Design sequences with the intended catalytic identities preserved.
5. Predict and filter structures using the campaign-specific assessment.
6. Calculate the reported structural comparison and inspect the catalytic arrangement in the selected design.

Recover the numerical campaign filters from the supplement/code. AME thresholds are not automatically the filters used in this campaign.

## Computational reference results

| Quantity | Published reference | Type |
| --- | --- | --- |
| Similarity of the depicted design to 5K7V | TM-score 0.53 | Computed structural outcome |
| Per-design confidence, geometry, and clash values | Extract released campaign/supplementary results | Detailed numerical baseline to recover |
| Generation and computational filtering counts | Recover original stage definitions and logs/data where available | Campaign-level comparison |

The TM-score comes from Fig. 4b. [Source](https://pmc.ncbi.nlm.nih.gov/articles/PMC12791007/) It is distinct from the reported experimental activity. Do not use the number of proteins screened in the laboratory as the denominator of a computational success rate.

## Reproduction and comparison

Apply the [shared procedure](README.md#how-to-execute-a-task), then:

1. Recover exact motif, sequence, model, and score-file identities.
2. Recompute the published structural-pair metric with the matching chain selection and normalization.
3. Repeat prediction and catalytic-site assessment for the published sequence using disclosed coordinate/template/MSA inputs.
4. Compare native metric values against published per-design outputs where recoverable.
5. If repeating generation, retain every scaffold-to-sequence-to-prediction relationship and compare distributions at the declared sample scale.
6. Report cysteine approach geometry, donor/acceptor mapping, oxyanion stabilization, and clashes separately where the original evaluator defines them.
7. Record missing numerical references explicitly; a newly calculated geometry value without a source baseline is additional characterization, not numerical reproduction.

For a closest-structure claim, keep the historical search library separate from a current-database search. Freeze all alignments and atom selections before scoring. Avoid postprocessing that forces the desired catalytic geometry into the evaluated model.

## Execution requirements

Verify connected-tool support for the atomic motif, preserved residue identities, local backbone context, ligand handling, and full sequence/assembly. A similarly named enzyme model is not proof of the same representation or implementation.

Use the permitted platforms under the [tool policy](../MODELS_AND_TOOLS.md). Preserve original output coordinates and capture mapping transformations. Report unavailable original methods; record any substitution as a platform adaptation.

Complete covalent-state or reaction-path calculations only when required by the selected original computational protocol or a separately declared evaluation. Do not add a new chemistry method and present its values as reproducing the original structure filter.

## Expected outputs and acceptance

Return source manifests, exact design/motif mappings, recovered computation settings, reference and calculated metrics, raw models/receipts, stage denominators, and the comparison report.

A valid comparison identifies which specific published computations were repeated, which methods changed, and which source values remain unavailable. Use numerical tolerances based on the actual metric implementation, precision, and sampling. Keep structural agreement separate from a claim about the full catalytic cycle.

## Experimental context

The paper reports an acylation-step efficiency of 248 ± 34 M⁻¹s⁻¹ and multiple-turnover evidence; Fig. 4b rounds the efficiency to 250. [Paper](https://pmc.ncbi.nlm.nih.gov/articles/PMC12791007/) These are supporting observations for the published construct. They do not replace the computational reference data above.
