# Benchmark: Gal-3BP: Glycan-Aware Antibody Interface Refinement

**Task ID:** `task_005_gal3bp_glycan_aware_interface_refinement`

**Task:** [Gal-3BP: Glycan-Aware Antibody Interface Refinement](../../../tasks/monoclonal_antibody_design/task_005_gal3bp_glycan_aware_interface_refinement.md)

## Published Results

**Source:** [Overcoming structural complexity in Galectin-3BP through an integrative computational antibody design workflow, Computers in Biology and Medicine 204 (March 2026)](https://doi.org/10.1016/j.compbiomed.2026.111550); [full-text manuscript](https://repositorio.usp.br/directbitstream/383020dc-ab48-4ab6-9bf9-81898eee73c7/3292201.pdf), Methods 2.1, 2.6–2.8 and Section 3.2/Figure 3.

| Published metric | Reported value | Scope and interpretation |
| --- | ---: | --- |
| Unique reference-complex interactions | **161** | Paper's reference Gal-3BP/scaffold complex, using its interaction analysis. |
| Unique Mut1-complex interactions | **165** | Mut1 comparison; a count, not an affinity measurement. |
| Hydrogen-bond share of contacts | Approximately **67%** | Reported E1 interaction analysis; retain its contact-counting definition. |
| Interface RMSD selection boundary | **5 Å** | Stability-selection threshold, not a reported mean or best RMSD. |
| Mut1 interface-stability outcome | **No replica exceeded 5 Å** | Selected outcome across the three heated simulations; the result is a replica-level threshold outcome. |
| Independent simulation replicas per modified system | **3** | Replication count, not a quality score. |
| E1 glycan-associated ΔSASA | **2.9 Å²** | Antigen epitope accessibility change, not antibody binding energy. |
| E2 glycan-associated ΔSASA | **7.0 Å²** | Other epitope in the paper; contextual comparison only. |
| Global glycan-associated SASA reduction | Approximately **1,299 Å²** | Whole-antigen accessibility change. |

The reported interface-stability criterion and contact counts are the relevant comparison anchors; neither alone proves improved affinity.

## Evaluation Criteria

| Criterion | Comparison requirement | Acceptance boundary |
| --- | --- | --- |
| Interface stability | Match interface-atom definition, alignment, sampling conditions and replicate treatment before comparing with the reported 5 Å boundary. | A threshold is not a reported mean; preserve all replicate outcomes. |
| Contact network | Apply the same interaction definitions to reference and variant trajectories. | More contacts alone do not demonstrate improved affinity. |
| Accessibility and sequence integrity | Preserve target/glycan context, paired-chain identity and permitted edits. | Antigen ΔSASA is not antibody binding energy; retain its epitope and glycan definitions. |

## Saved workflow results

See [comparison.md](comparison.md) for the consolidated comparison across saved run IDs.
