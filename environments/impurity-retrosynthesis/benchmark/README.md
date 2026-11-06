# Literature benchmark and achieved metrics

This folder contains the actual comparators and observed computational metrics, not only a proposed evaluation protocol. The comparison is documentary; no chemical-performance superiority has been demonstrated.

- [Papers and patents compared](literature_comparison.md): all supplied references, verification level, corresponding generated routes and conclusions.
- [Achieved metrics](achieved_metrics.json): machine-readable counts and unavailable experimental metrics.
- [Observed result interpretation](../results/literature_findings.md).

## Achieved results

| Metric | Ibuprofen impurity A | Ibuprofen impurity M | Meaning |
|---|---:|---:|---|
| Generated paths reviewed | 12 | 7 | All available original route IDs retained |
| Reaction-labelled nodes screened | 38 | 21 | Graph nodes, not experimentally executed reactions |
| Root structures matching provisional target | 12/12 | 7/7 | RDKit canonical root match, not step feasibility |
| Nodes with traceable citation in export | 0/38 | 0/21 | Empty exported citation fields, not proof of absent literature |
| Nodes with procedure text in export | 0/38 | 0/21 | No conditions supplied in those fields |
| Nodes with absent element source among listed precursors | 9 | 1 | Omitted reagent source possible; not full atom-balance failure |
| Experimentally validated lead routes | 0 | 0 | No wet-lab confirmation in this evidence set |
| Measured isolated yield / purity / 100 g INR cost | Not established | Not established | Model yield/cost fields cannot replace measurements or quotes |

Racemic ibuprofen: run and literature comparison completed according to the project owner; numerical output and exact comparator mapping are not available in this checkout, so metrics are null rather than zero. It is excluded from the A/M totals above. Osimertinib is an original held proposal, not the racemic task.

