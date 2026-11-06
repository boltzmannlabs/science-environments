# Task 001 — Reproduce the AME atomic motif benchmark

## Objective

Reproduce the published atomic-motif scaffolding evaluation and compare computational case coverage, motif recovery, and ligand clashes. Evaluate the original method and any permitted platform adaptation as separate conditions.

## Publication and sources

[Ahern et al., Atom-level enzyme active site scaffolding using RFdiffusion2, Nature Methods 23, 96–105 (2026)](https://doi.org/10.1038/s41592-025-02975-x). Computational benchmark: Fig. 3, AME Methods, supplementary section B, and Fig. 3 source data. The paper appeared online in 2025.

Use the [author implementation](https://github.com/RosettaCommons/RFdiffusion2) and [official documentation](https://rosettacommons.github.io/RFdiffusion2/) to recover the paper configuration. Pin the actual revision; a current default is not automatically the published setting.

## Inputs

| Input | Required identity |
| --- | --- |
| Released AME case inventory | Original case IDs and complete motif/ligand representations |
| Atomic motif and ligand files | Catalytic atom selection, residue correspondence, and ligand connectivity |
| Original evaluation outputs | Per-case/sample data behind Fig. 3 |
| Generation and evaluation configuration | Checkpoint/version, settings, seeds, sequence and predictor sampling |
| Scope inventory | Required cofactors, assembly, and any exclusions |

AME includes different chemical requirements. Select only cases compatible with the environment's supported scope, or explicitly identify an unsupported case. Preserve the denominator and exclusion reasons; a subset result is not full-benchmark coverage.

## Published computational pipeline

1. Construct the released atomic-motif task with catalytic groups and ligand coordinates.
2. Generate backbones with RFdiffusion2; run the published RFdiffusion baseline separately if that comparison is in scope.
3. Assign sequences with LigandMPNN.
4. Predict the designed sequences with Chai-1.
5. Map generated motif residues to predicted residues and align the specified motif backbone atoms.
6. Evaluate catalytic-atom recovery and ligand clashes using the original definitions.
7. Aggregate predictor samples and sequences into backbone success, then aggregate backbones into case coverage.

The reported evaluation used 100 backbones per case, eight sequences per backbone, and five Chai-1 samples in the backbone-success definition. Recovery required a sample below 1.5 Å catalytic heavy-atom RMSD; the ligand-clash boundary was 1.5 Å. RFdiffusion2 covered 41/41 cases and RFdiffusion 16/41. [Paper, AME Methods and Fig. 3](https://pmc.ncbi.nlm.nih.gov/articles/PMC12791007/)

## Computational reference results

| Quantity | Published reference | Type |
| --- | --- | --- |
| Cases with a successful RFdiffusion2 backbone | 41/41 | Computed aggregate outcome |
| Cases with a successful RFdiffusion backbone | 16/41 | Computed baseline outcome |
| Catalytic heavy-atom RMSD | <1.5 Å | Filter threshold |
| Ligand-clash boundary | 1.5 Å | Filter definition |
| Sampling | 100 backbones × eight sequences per case; predictor-sample selection as above | Protocol setting |
| Per-case/backbone success rates | Recover Fig. 3 source data | Required detailed baseline |

Preserve the exact atom sets and clash-pair definition from the supplement/code. The main text and Methods describe the atom selections at different levels of detail; record the resolved implementation rather than inventing a new evaluator.

## Reproduction and comparison

Execute the [shared procedure](README.md#how-to-execute-a-task), then:

1. Freeze case IDs, sampling, release identities, and the evaluator before inference.
2. Verify residue/atom mapping with a reference calculation and rigid-body transformation checks.
3. Keep every generation, sequence, and prediction result with its parent identity.
4. Compute per-sample recovery and clashes; apply the published at-least-one-sample aggregation.
5. Report per-sequence and per-backbone success separately from case coverage.
6. Compare matching case/sample counts. Include technical failures, missing atoms, invalid structures, and budget-truncated cases.
7. Report coverage difference and per-case rate differences; quantify variability when repeated campaigns are available.

Do not minimize or copy motif coordinates into a predicted model before calculating an independent recovery score. Record symmetry-equivalent atom mapping and alignment choices explicitly.

## Execution requirements

Verify that the connected generator supports the released motif representation. Verify sequence-design constraints and predictor output/conditioning before dispatch. A substituted predictor defines a different evaluation regime and needs its own comparison table.

The original campaign scale exceeds the fallback pilot. A reduced task can demonstrate integration and give sample-level measurements; it cannot reproduce the original success statistics. Apply actual authorized quotas.

Coordinate-conditioned prediction used for a literature comparison remains distinct from the environment's independent sequence-only fold gate. No additional property or chemistry stage should be invented as part of the original AME protocol.

## Expected outputs and acceptance

Return the input/source manifest, tool settings, raw models/receipts, per-sample atom mappings and scores, per-backbone success table, per-case coverage table, and published-versus-calculated differences.

A comparable result requires the same task subset, metric implementation, sampling denominator, and information basis. Report an adapted or incomplete comparison when those differ. AME success measures computational scaffolding; it does not establish catalytic activity.

## Experimental context

The paper also reports laboratory enzyme campaigns. Those experiments are separate from this task's computational benchmark and are addressed in the reaction-specific tasks.
