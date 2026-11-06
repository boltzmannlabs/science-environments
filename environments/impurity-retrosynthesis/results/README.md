# Results and case-study register

| Case | Execution and literature comparison | Evidence available in this package |
|---|---|---|
| Ibuprofen impurity A | Completed computational run and literature comparison | 12 paths / 38 reaction-labelled nodes in screening_summary.json and screening_routes.csv |
| Ibuprofen impurity M | Completed computational run and literature comparison | 7 paths / 21 reaction-labelled nodes in screening_summary.json and screening_routes.csv |
| Racemic ibuprofen | Completed run and literature comparison, confirmed by project owner | Completion recorded in case_studies.json; original export, reference mapping and numerical metrics not present in this checkout |
| Osimertinib impurity label/CAS proposal | Historical proposal held for identity reconciliation; not the racemic ibuprofen task | No generated paths in the published snapshot |

The A/M aggregates cover only their two exported route sets. They do not count racemic ibuprofen and must not be presented as totals for all completed project tasks. Racemic ibuprofen is the para-isobutyl parent compound and must not be conflated with meta-substituted impurity A or alpha-hydroxy impurity M. Lack of a linked artifact is a reproducibility gap, not evidence that the owner-confirmed run did not happen.

All model-generated values remain distinct from measured results. No literature superiority, experimental yields, purity qualification or 100 g INR estimate is inferred for racemic ibuprofen from the available A/M summaries. Link its original result/report and exact literature comparison before reporting numerical performance.

Raw account-scoped service exports, local machine paths, credentials and signed links are excluded. The audit flags missing element sources among *listed* precursors only, not full atom-balance failure. See [research notes](../../../research/impurity-retrosynthesis/research-notes.md) for scientific interpretation.


## Files and what they contain

| Output file | Content and scope |
|---|---|
| [screening_summary.json](screening_summary.json) | A/M per-target route/node/root-match/evidence-field totals; computational only |
| [screening_routes.csv](screening_routes.csv) | Every original A/M route ID, node count, structural/evidence flags and model ranking field; all decisions held |
| [case_studies.json](case_studies.json) | Distinct completion and artifact status of A, M, racemic ibuprofen and the original osimertinib proposal |
| [literature_findings.md](literature_findings.md) | What our paths achieved compared with each target's literature, and where equivalence/performance was not established |
| [benchmark achieved_metrics.json](../benchmark/achieved_metrics.json) | Observed computational metrics; null experimental metrics; separately labelled patent-reported results |
| [benchmark literature_comparison.md](../benchmark/literature_comparison.md) | Full named comparator list, source links, verification levels and route mappings |

## Achieved versus expected

A/M: all 19 paths were accounted for and root-matched to provisional targets; 59 reaction nodes were screened. Direct A-product patent routes were located, but generated A top5/top3 reproduce only related reaction families/topology. M top4 shares a cyanohydrin class, not a verified OH-retaining literature synthesis. No project measured isolated yield, ≥95% purity result, INR quote or experimentally validated lead is available. The numerical counts above do not include the owner-confirmed racemic case. These outcomes meet the computational inventory objective, not full chemical/process qualification.
