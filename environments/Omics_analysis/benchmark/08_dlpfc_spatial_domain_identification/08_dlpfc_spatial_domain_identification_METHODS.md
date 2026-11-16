# dlpfc_spatial_domain_identification: reference and metrics

## Reference

The agent's spatial domains are compared with the manual layer annotation of human DLPFC sample 151673 from Maynard et al. 2021, *Nature Neuroscience* (doi 10.1038/s41593-020-00787-0). The comparison measures agreement with that annotation, not correctness against an external truth. The annotation is itself a manual assignment of spots.

- Files in this folder:
  - `DLPFC_151673_hidden_labels.csv`: columns `spot_id` and `truth`, one row for each of the 3,639 spots. The labels are `Layer_1` to `Layer_6` and `WM`. 28 spots have no label.
  - `benchmark_result.json`: the comparison for this run.
- Reference label counts: Layer_3 989; Layer_6 692; Layer_5 673; WM 513; Layer_1 273; Layer_2 253; Layer_4 218; no label 28.
- What the paper reports (from its text): 12 Visium samples from 3 neurotypical adult donors, 47,681 spots in total, with spots assigned manually to the six cortical layers or white matter. The paper names SNAP25 (gray matter), MOBP (white matter) and PCP4 (layer 5) as markers used to confirm section orientation. It uses the adjusted Rand index against the manual annotation as its measure of performance, with the values shown in its Figure 7F. Those values were not extracted.
- Agent input: `DLPFC_151673_agent_input.h5ad`, with expression, spot identifiers and spatial coordinates, and no labels.

## How to score

There are no weights, no overall score and no pass/fail. Each metric is reported on its own. `benchmark_result.json` is the direct output of `scripts/08_dlpfc_spatial_domain_identification/compare_dlpfc.py` (command in the file header), run on the files in this folder and the agent's output files.

## Output files read

- `spatial_domains.csv` (required): `spot_id`, `domain_id`.
- `domain_markers.csv`: `domain_id`, `gene`, `effect_size`, `p_value`, `adjusted_p_value`, `rank`.
- `answers.json`: dataset id, spot counts, number of domains, interpretations, markers, evidence, model, limitations.
- `Analysis report.txt`: read and hashed. No metric depends on its text.

## Structure of `benchmark_result.json`

1. `reference`: the labels file and its counts.
2. `paper_reported`: what the paper reports about the design, the annotation and the metric.
3. `agent_reported`: what the agent reports (counts, number of domains, interpretations, markers, model, limitations).
4. `metrics`: how the agent's output compares with the reference.
5. `notes`: how to read the metrics.
6. `provenance`: SHA256 of every input file and of the script, and the software versions used.

## Definitions

Metrics that compare labels use the spots that have a reference label (3,611 of 3,639). The agent's domain numbers are arbitrary, so no metric needs domains matched to layers.

| Metric | What it measures | Calculation |
|---|---|---|
| `adjusted_rand_index` | Agreement of the two partitions, corrected for chance | scikit-learn `adjusted_rand_score` between agent domain and reference label |
| `normalized_mutual_information` | Information the domains share with the labels | scikit-learn `normalized_mutual_info_score` |
| `homogeneity` | Whether each agent domain holds one reference label | scikit-learn `homogeneity_completeness_v_measure` |
| `completeness` | Whether each reference label sits in one agent domain | same call |
| `contingency_agent_domain_by_reference_label` | The counts behind every agreement metric | number of spots for each pair of domain and label |
| `per_agent_domain` | What each agent domain contains | dominant label, its share of the domain, and the share of every label |
| `per_reference_label` | Where each reference label went | agent domain holding the most spots of the label, and the share it holds |
| `spatial_coherence` | Spatial smoothness of the agent's domains and of the reference | for each spot, the share of its 6 nearest spots by coordinate with the same label, averaged over spots. Reference spots without a label are skipped. |
| `interpretation_claims_that_name_a_layer` | Whether the agent's layer claims hold | for domain 2 ("white-matter-like"), the share of its labelled spots that are `WM`. For domain 1 ("upper/supragranular-like"), the share in `Layer_1`, `Layer_2` or `Layer_3`. |
| `paper_named_markers_in_agent_marker_tables` | Whether the markers the paper names appear in the agent's tables | domains and ranks in which SNAP25, MOBP and PCP4 are listed |
| `agent_file_consistency` | Whether the agent's files agree | domain count, spot count and domain sizes in `answers.json` against the CSV, and the reported coherence against the recomputed value |

## How the spec was made

- ARI and NMI do not need the agent's number of domains to equal 7, and the task says not to force a number.
- Agreement metrics are reported together and not combined. Homogeneity and completeness show which side of a mismatch a result falls on.
- Only the two agent claims that name a layer are tested. The agent's "uncertain" interpretations make no claim to test, and `per_agent_domain` shows what those domains contain.
- There are no weights and no pass/fail cutoffs, because none could be justified.

## Limits

- The reference is a manual annotation of one section, so the comparison cannot separate agent error from annotation choices.
- The 28 unlabeled spots are left out of the agreement metrics. The paper's text does not explain why they have no label.
- The paper's own ARI values are in a figure and were not extracted, so the agent's score is not compared with a published number.
- Only three marker genes named in the paper are checked, and the paper's layer-enriched gene tables were not used.
- The coherence metric uses spot coordinates, so it is not independent of the agent's own spatial smoothing.
- One sample, one run.
