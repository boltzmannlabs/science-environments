# Missing-metric benchmark report — Task 002

Benchmark selected: the task-specific PD-L1 Germinal benchmark, not another antibody benchmark.
Source: Germinal, Nature Biotechnology 2026, PMC13366713. Principal structural benchmark: H5 predicted-versus-experimental global Cα RMSD = 1.25 Å, using the Germinal-generated H5/PD-L1 complex against cryo-EM PDB 35TL/EMDB EMD-77181. Campaign yield (470 passing designs), CDR identity (~40%, <52%) and interface similarity (IS ≤ 0.2) are dataset/campaign-level metrics, not candidate-level acceptance thresholds.

## Missing or non-matched metrics

| Metric | Benchmark method/scope | Our result | Comparison |
|---|---|---|---|
| H5 global Cα RMSD | Germinal prediction vs experimental 35TL H5/PD-L1 coordinates | 14.942 Å for the H5 Boltz-2 re-prediction; H5 pTM 0.9437, ipTM 0.9262 | Below the published structural result numerically, but not like-for-like: Germinal generator vs Boltz-2 predictor and different structure-generation protocol. |
| Candidate global Cα RMSD vs independent experimental structures | Requires an experimental structure for each new candidate | Not available; no experimental candidate structures | Cannot reproduce. |
| Exact interface-similarity IS | Paper/database-defined structural similarity calculation | Not reproduced; definition/database implementation unavailable in the retained package | Cannot reproduce without the paper's exact database, alignment and IS implementation. Do not replace with contact count or sequence identity. |
| Campaign yield: 470 passing designs | Full Germinal PD-L1/IL3 campaign and filter definitions | 20 RF-Antibody records generated; 10 evaluated; 5 shortlisted | Not comparable to a campaign yield. |
| Dataset-level CDR identity (~40%, <52%) | Germinal novelty analysis over the PD-L1/IL3 design context | Existing retained per-candidate CDR3-H identities: 6.9–27.6% | Candidate-level sequence novelty is lower than the dataset-level identity summary, but populations and exact identity procedure are not identical. |

The retained `novelty_recomputed.json` uses `difflib.SequenceMatcher`; it is not the paper's exact IS metric. No fabricated IS value is reported.

Tools actually verified: local Boltz-2 v2.2.1 was already used for the retained H5 and candidate structures; the retained local analysis scripts provide the RMSD and novelty records. No independent Germinal implementation is available locally.
