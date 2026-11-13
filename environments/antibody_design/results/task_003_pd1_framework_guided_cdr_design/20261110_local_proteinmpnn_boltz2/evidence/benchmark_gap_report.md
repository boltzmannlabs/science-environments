# Missing-metric benchmark report — Task 003

Benchmark selected: the task-specific PD-1 tFold benchmark from PMC12815924, not the LCAT or PD-L1 benchmarks.
Published anchors: virtual-screening AUROC 0.76 on 745 antibodies with 27 positives; top-1% enrichment 7.41 on the same panel; design-campaign AUROC 0.95 on a separate campaign; epitope-informed CDR-H3 AAR 0.317 on the SAbDab-22-DesignAb aggregate.

## Missing or non-reproducible metrics

| Metric | Exact benchmark method/data | Our result | Comparison |
|---|---|---|---|
| Virtual-screening AUROC | Original labelled panel: 745 antibodies, 27 positives; original score orientation and top-1% rule | Not computed | Cannot reproduce without the original labelled panel and scoring definition. A single candidate cannot yield AUROC. |
| Top-1% enrichment | Same 745-antibody panel; two positives among seven selected | Not computed | Cannot reproduce without the panel and exact ranking score. |
| Design-campaign AUROC | Separate tFold design-campaign labelled set | Not computed | Cannot reproduce without campaign labels and score definitions. Do not substitute candidate ipTM. |
| CDR-H3 AAR 0.317 | SAbDab-22-DesignAb aggregate, epitope-informed mask | Not computed for the held-out dataset | Cannot reproduce without the exact dataset, mask and reconstruction protocol. |
| Candidate-level structural/interface comparison | Candidate-level tFold metrics are not published as a matching benchmark table | Historical local Boltz-2 values available: H965 ipTM 0.878; cand2 0.760; cand9 0.671; cand11 0.652 | These are local candidate-level predictions, not AUROC/enrichment/AAR and do not establish superiority. |

The platform six-CDR run remains pending; the historical local CDR-H3-only run is kept separate. No candidate-level metric is assigned to the unsubmitted platform workflow.

Tools/status: the retained local Boltz-2 confidence artifacts were inspected; no valid open-source route exists to reconstruct the missing labelled panel metrics from the available files.
