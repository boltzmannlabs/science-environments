# Benchmark: papers, metrics and achieved comparisons

## Literature actually compared

Read [papers.md](papers.md) for paper titles, DOI/source links, comparison step, substrate-match status, accessible experimental numbers and access limitations. [papers.json](papers.json) is the machine-readable source catalog. No publisher PDFs are redistributed. The two patent entries are screened broad-query hits, not positive route evidence.

## Metrics achieved

[achieved_metrics.json](achieved_metrics.json) records the denominator and interpretation for every computed metric. The observed/derived results are 16 generated routes, 56 reaction-node occurrences across routes, one separately checked route (three steps), and two of those three expected products ranked first by forward prediction. This is descriptive model agreement, **not experimental accuracy**.

No target-specific measured yield or selectivity exists; exact same-target experimental routes established in the screened sources: zero. Literature yield error and experimentally achieved improvement are unavailable, not zero.

## Comparison tables

- [Tool versus literature and all-route yields](../../results/task-01-fluorinated-quinoline-retrosynthesis/achievements_and_comparison.md).
- [All-route numeric CSV](../../results/task-01-fluorinated-quinoline-retrosynthesis/route_yield_comparison.csv).
- [All generated route steps and inputs](../../results/task-01-fluorinated-quinoline-retrosynthesis/route_summary.json).
- [Selected route reaction-level audit](../../results/task-01-fluorinated-quinoline-retrosynthesis/top0_validation.json).

The literature 32% isolated deprotection yield belongs to a different compound. Neither model percentages nor their illustrative products may be called observed target yield or an improvement over that reference.

## Reproduce

From the repository root, run `python environments/synthetic_chemistry/scripts/build_comparisons.py` and `python -m unittest discover -s environments/synthetic_chemistry/tests -v`. No external service is contacted. Tests assess data consistency, not chemistry or literature ground truth.
