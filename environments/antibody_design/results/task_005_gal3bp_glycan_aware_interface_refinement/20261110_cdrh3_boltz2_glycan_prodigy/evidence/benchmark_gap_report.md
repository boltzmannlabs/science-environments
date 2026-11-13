# Missing-metric benchmark report — Task 005

Benchmark selected: the task-specific Gal-3BP glycan-aware interface benchmark from the Computers in Biology and Medicine 2026 study. Published anchors: reference interactions 161, Mut1 interactions 165, H-bond share approximately 67%, interface-RMSD selection boundary 5 Å, no heated-MD replica exceeding 5 Å, E1 glycan-associated ΔSASA 2.9 Å², E2 ΔSASA 7.0 Å² and global glycan-associated SASA reduction approximately 1,299 Å².

## Available matched-condition calculations

The retained open-source Prodigy results and local contact/glycan calculations were inspected. Our matched-condition values are:

| Candidate | Prodigy ΔG (kcal/mol) | Prodigy Kd (M) | Interface residue pairs | H-bond share | Glycan clashes | Interpretation |
|---|---:|---:|---:|---:|---:|---|
| BDBV-43 reference | -11.2 | 6.1e-09 | 32 | 4.98% | 0 | Computational reference under our model |
| cand17 | -14.5 | 2.3e-11 | 54 | 3.61% | 0 | Strongest Prodigy estimate, not a matched paper result |
| cand11 | -11.1 | 7.3e-09 | 59 | 1.31% | 0 | Highest retained Boltz2 ipTM, not strongest Prodigy |
| cand7 | -10.8 | 1.2e-08 | 39 | 3.27% | 0 | Lower-confidence contrast |

Tool: Prodigy CLI, selection A,B versus C; exact executable version was not exposed by the installed CLI, so version is recorded as unavailable. Local contact definitions are documented in the task metrics.

## Missing or non-comparable metrics

| Metric | Benchmark requirement | Our status | Comparison |
|---|---|---|---|
| Paper interaction counts 161/165 | Same mature construct, glycan model, epitope mapping and interaction definitions | Not reproduced; our reference has 32 residue pairs under a different matched model | Not comparable. |
| H-bond share ≈67% | Paper-specific contact/trajectory analysis | Our values 1.31–4.98% under static heavy-atom proxy | Not comparable; lower values do not establish worse binding. |
| Interface RMSD and 5 Å stability boundary | Three independent heated-MD replicas per system | Not run; no validated MD system/replicas and exact paper setup available | Cannot reproduce. |
| Replica outcome: no replica >5 Å | Three heated-MD simulations for Mut1 | Not run | Unresolved. |
| E1/E2 glycan ΔSASA 2.9/7.0 Å² | Paper's exact E1/E2 mapping and glycan model | Our approximate BACK-domain model gives 34.2 Å² | Not comparable; exact epitope/glycan definition unavailable. |
| Global glycan SASA reduction ≈1,299 Å² | Full paper antigen/glycan system | Not reproduced | Exact glycan model and construct unavailable. |

The retained 34.2 Å² value is a matched-condition approximation, not a reproduction of the paper's 2.9 Å² E1 value.
