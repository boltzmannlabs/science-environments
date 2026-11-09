# D2R peripheral candidate prioritisation benchmark

**Task:** `task_001_d2r_peripheral_candidate_prioritisation`  
**Task Format:** goal_oriented  
**Grading Mode:** manual_review_required

## Purpose

Assess whether the agent can obtain defensible D2R candidate recommendations from the supplied library and support its decisions with relevant evidence. Compare its computational outputs with the reference paper while allowing an independently chosen workflow.

Execution outcomes, numerical comparisons and evaluation reports belong in `results/`, not in this definition. Evaluator-only reference outcomes must not be supplied to the execution agent. The executed stage-by-stage comparison between the paper and the completed run is recorded separately in [task_001_d2r_peripheral_candidate_prioritisation_comparison.md](task_001_d2r_peripheral_candidate_prioritisation_comparison.md).

## Reference baseline

Kim et al. (2026), *Identification of novel peripherally restricted risperidone-like dopamine D2 receptor antagonists for prolactin-mediated neuroprotection through a multi-stage in silico screening*. [PLOS One, DOI 10.1371/journal.pone.0355997](https://doi.org/10.1371/journal.pone.0355997).

| Reference item | Baseline |
| --- | --- |
| Target | Human DRD2, UniProt P14416; primary crystal reference 6CM4 |
| Library | 400 deposited records, 398 distinct full InChIKeys; preserve all source IDs |
| Controls | Risperidone and domperidone; supporting native ligands provide structural context |
| Docking candidates | 226 listed rows; 225 numerical Vina scores; ID 380 has no numerical score |
| Risperidone Vina reference | −11.8 kcal/mol |
| Strict docking shortlist | 17, 21, 24, 27, 128, 321, 360, 381 |
| Contact-selected four | 27, 128, 360, 381 |
| Final priorities | 128, 381 |

The frozen library derives from the deposited source input SMILES, not from a new similarity search. The authors' modeled/prepared receptor and original candidate poses are not available. Four source ADME prediction payloads have conflicting identities; the input structures remain usable. The reference is computational, not experimental ground truth.

Source workbooks, article files and interpretation references are retained in `task_001_d2r_peripheral_candidate_prioritisation/reference/`. Input provenance is recorded in `input_provenance.json` and `papers.csv`.

## Evaluation method

1. Check source IDs, chemical identities, target inputs and reference controls against the supplied task inputs. Count library records separately from distinct chemical identities.
2. Establish what actually ran using retained outputs and execution records. Separate planned, attempted, successful and failed assessments; identify evidence recovered outside the supplied archive.
3. Check whether the chosen evidence addresses D2R, restricted brain access and intestinal absorption. Verify endpoint meanings, units, score direction, control source and limitations.
4. Assess whether the ranking and priorities follow from the evidence and the agent's declared decisions. The task permits fewer supported recommendations rather than filling output counts without evidence.
5. Compare equivalent numerical results with the paper where available. Document differences in preparations, protocols and score definitions before interpreting agreement.
6. Check that the report, CSV, assessment and supporting outputs agree, and that failures and uncertainty remain visible.

## Metrics and comparison criteria

| Metric | Definition | Interpretation |
| --- | --- | --- |
| Input integrity | Source ID/SMILES/ZINC/chemical-identity and target pairing checks | Different stereochemical entities and duplicate records must remain explicit |
| Numerical coverage | Unique library IDs with finite outputs for each named endpoint | An upload or failed row does not count as a numerical result |
| Output completion | Presence and content of ranked candidates, assessment, detailed report and supporting artifacts | File presence alone is not scientific success |
| Shortlist agreement | Intersection of paper and run shortlist ID sets; report the actual set sizes | Descriptive agreement, not biological accuracy |
| Priority agreement | Intersection of paper and run final-priority ID sets | Matching the paper is not mandatory |
| Comparable docking scores | Paired numerical values on common IDs; Pearson r and Spearman ρ | Protocol-dependent agreement; use available numerical pairs only |
| Within-run method agreement | Correlations between eligible paired outputs, with endpoint and score direction stated | Do not treat pose confidence as affinity or combine unlike score scales |
| Control-relative evidence | Candidate versus reference comparisons within the same predictor and verified scale | Mixed-provider raw values require reconciliation |
| Pose evidence | Source/export identity, receptor suitability, pose confidence and defined interaction geometry | Closest distances alone do not prove specific interactions |
| Decision quality | Suitability of chosen evidence, justification of thresholds, handling of missing data and trade-offs | Review reasoning as well as final rows |
| Reproducibility | Retained inputs, settings, raw outputs, mapping, receipts and provenance | Missing worker files or versions limit exact reconstruction |

Use minimum finite Vina score for the best returned Vina score and maximum finite DiffDock confidence for its best pose-quality score when those tools are used. These are endpoint-interpretation rules, not prescribed tools for execution. Do not assume physical units for a model score without evidence.

## Scientific acceptance and exclusions

Recommendations must have a defensible rationale relevant to the task's scientific criteria. Predictions must remain distinct from measurements and functional antagonism. Unknown values remain missing; no invented results, uncertainty intervals or aggregate pass score are permitted.

A different shortlist or low cross-method agreement is not independently a failure. A documented prediction that does not support the desired outcome must not be relabelled or replaced with an unrelated endpoint merely because the latter varies.

Molecular dynamics and the paper's optional off-target docking are outside this task's required execution scope. No missing-work penalty applies to those stages. Provider-only restrictions, if specified by an execution prompt, are assessed separately from the provider-agnostic task specification.
