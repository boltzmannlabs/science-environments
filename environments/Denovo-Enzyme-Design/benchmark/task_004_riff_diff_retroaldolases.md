
**Task ID:** `task_004_riff_diff_retroaldolases`

**Task:** [Retro-aldolase catalytic-array scaffolding and dynamics](../tasks/task_004_riff_diff_retroaldolases.md)

## Published Results

**Source:** [Braun et al., *Computational enzyme design by catalytic motif scaffolding*, Nature 649, 237–245 (2026)](https://doi.org/10.1038/s41586-025-09747-9), retro-aldolase design section and Figure 4c,d; [Supplementary Information](https://static-content.springer.com/esm/art%3A10.1038%2Fs41586-025-09747-9/MediaObjects/41586_2025_9747_MOESM1_ESM.docx), Supplementary Figure 1 and active-site metric methods.

| Published metric | Reported value or outcome | Scope and interpretation |
| --- | --- | --- |
| Mean per-residue AlphaFold2 pLDDT | **All 36 selected sequences were assigned high confidence**. | Supplementary Figure 1 caption. Exact numerical pLDDT values and cohort median are not tabulated in the caption; do not invent a numerical cutoff from this statement. |
| Catalytic-sidechain recovery | **Average sidechain RMSD below 1 Å** to the catalytic geometry. | Supplementary Figure 1 caption, selected RAD models. This is a cohort-level outcome, not a guarantee that every candidate is below 1 Å. |
| Maximum structural-neighbour TM-score | **Mean maximum TM-score 0.49** for the **36 selected sequences**. | Main text. The cohort comprises 12 unique backbones; Foldseek identifies PDB matches and TM-align supplies the structural score. The mean is over the reported design cohort, not 12 independently weighted backbones. |
| Surface aggregation propensity per residue | Published as a distribution of individual-design scores and a median. | Supplementary Figure 1. An exact numerical reference is unavailable from the caption. |
| Total Rosetta energy per residue | Published as a distribution of individual-design scores and a median. | Supplementary Figure 1. Retain the native score function and residue-count normalization; no exact numerical reference is established by the caption. |
| Catalytic RMSF and interaction-distance deviations | Reported for the dynamics assessment. | Figure 4c and associated methods. Exact per-design numerical references require the underlying simulation records; no values are inferred from plot positions. |
| Two-state active-site metric | Reported for Michaelis-complex and hemiaminal predictions. | Figure 4d and supplementary methods. No exact candidate score is established here without the component measurements and reference ensembles. |

For the active-site metric, use the task's seven ordered atom measurements and its complete equation: reference-median centering, unscaled median absolute deviation, signed component averaging, and the sum of the independently selected state minima from 20 predictions per state. Reference medians and MADs are calculated from matched source-enzyme ensembles, not fitted to the generated candidates. The published cohort mean TM-score is not such a normalization reference.

## Evaluation Criteria

| Criterion | Comparison requirement | Acceptance boundary |
| --- | --- | --- |
| Confidence and catalytic recovery | Match predictor, sidechain reconstruction, equivalent-atom selections and alignment; retain native confidence scale. | The selected cohort’s average catalytic-sidechain RMSD is below 1 Å. This does not establish a per-design cutoff; “high confidence” supplies no exact numerical pLDDT threshold. |
| Structural novelty | Retain PDB snapshot, neighbour search, alignment, normalization and sequence/backbone weighting. | Mean maximum TM-score 0.49 applies to 36 selected sequences from 12 backbones; it is not an individual candidate target or an equally weighted 12-backbone mean. |
| Surface aggregation and structural energy | Normalize SAP and total structural energy by the actual scored residue count under matched preparation and score definitions. | Compare on native scales. Exact reference values are unavailable from the caption; do not infer them from plotted positions. |
| Catalytic dynamics | Match apo state, replica sampling, force field, alignment and catalytic atom pairs; report individual replicas and uncertainty. | RMSF and interaction-distance deviation require ensemble/trajectory evidence; static geometry does not replace dynamics. |
| Two-state active-site metric | Retain all seven ordered measurements, state-matched reference medians/unscaled MADs, signed averages and independently selected state minima. | Use the full task equation and 20 predictions per state. A zero MAD, invalid atom map or incomplete required ensemble leaves the canonical score unavailable; no epsilon substitution or silent component omission. |
| Input and design validity | Preserve catalytic roles, separate LLK from methodol/hemiaminal chemistry, and retain pre/post-repacking structures. | Only compatible state and atom mappings support direct comparison; source-array agreement does not by itself demonstrate reaction performance. |
