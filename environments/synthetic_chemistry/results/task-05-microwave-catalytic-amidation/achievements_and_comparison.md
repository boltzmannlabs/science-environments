# Task 05 — achievements and comparison

[Task](../../tasks/task-05-microwave-catalytic-amidation/README.md) · [Benchmark](../../benchmarks/task-05-microwave-catalytic-amidation/README.md) · [Detailed comparison](comparison_report.md)

## Achievements by objective

1. **Condition recommendation:** one internal job was submitted once, polled to terminal completion, and returned ten numeric condition sets. All numbers were preserved with native semantics in [condition_summary.json](condition_summary.json).
2. **Constraint audit:** the catalytic-microwave requirement was checked explicitly. Every candidate had an empty catalyst name, no heating mode and no time; the output is non-compliant before yield comparison. This is a concrete negative result, not a missing datum.
3. **Literature verification:** five contextual sources were retrieved and checked; the key experimental facts were transcribed with exact DOI/PMID/PMC provenance and match-vs-analogy status in [papers.md](../../benchmarks/task-05-microwave-catalytic-amidation/papers.md).
4. **Comparison:** a criterion-by-criterion audit and contextual literature comparison was produced in [comparison_report.md](comparison_report.md), with all unavailable experimental metrics set to `null`.
5. **Optimizer execution:** a 192-candidate catalytic condition space was compiled and eight diverse initial designs were selected; a persistent campaign was created and a four-experiment batch reserved with zero measurements.
6. **Prior-yield handling:** earlier model-predicted yields were seeded into a second campaign as `excluded`, QC-flagged observations, blocking re-selection without contaminating the Bayesian fit; eight untested conditions were selected.
7. **Provenance:** all artifacts are sanitized; no credentials, signed URLs, personal paths or raw service exports are redistributed.

## Comparison summary

Against the task's stated objective, the internal tool output is not a good answer: it fails the catalytic requirement outright and does not supply microwave timing. Against the contextual literature, the target molecule is plausible but the proposed reagent-only conditions are not the catalytic systems used for this substrate class. The optimizer produced design hypotheses only; with zero measured observations, no candidate is empirically supported.

## Limitations

No experimental yield, exact-pair literature yield, MAE, optimum retrieval, solvent ranking, steric-class floor, time objective or impurity match exists. The designated 2025 HTE paper remains unidentified, so paper-specific scoring is impossible. The local optimizer's heuristic scores are not calibrated yields, and its yield model (where available) does not encode solvent, temperature, time, concentration or equivalents. All agent numbers are predictions, not experimental results.
