# Task 05 — gaps and improvement plan

[Task](../../tasks/task-05-microwave-catalytic-amidation/README.md) · [Benchmark](../../benchmarks/task-05-microwave-catalytic-amidation/README.md) · [Results](README.md)

## Gaps

1. **Designated paper unresolved:** the task's 2025 microwave HTE source (catalyst/solvent/temperature/time matrix, sterically hindered substrates, isolated yields, side products) has no title, authors or DOI in the supplied material. No paper-specific score can be computed.
2. **Internal tool constraint failure:** `condition_recommendation` returned no catalyst identity, heating mode or time; it cannot satisfy a catalytic-microwave task by construction.
3. **Non-discriminating yields:** five distinct yield values repeat across ten chemically different conditions; these are substrate-typical estimates, not condition-resolved predictions.
4. **No measured observations:** both optimizer campaigns have zero reviewed measurements, so no Bayesian fit or empirical ranking occurred.
5. **Literature incompleteness:** Europe PMC timed out and Crossref was intermittently unreachable; coverage is PubMed/PMC-only. No exact-pair yield was found.
6. **Questionable conditions:** several tool candidates combine HCl with amines/pyridine or K2CO3 with HCl in one pot; viability was not established by the retrieved literature.

## Improvement plan

1. Obtain the designated 2025 HTE paper/SI; register it as `SC02_PRIMARY` and extract exact acid/amine pairs, catalyst, solvent, microwave temperature/time, isolated yields and side products with table/SI positions.
2. Supply the real substrate matrix, class labels, allowed catalyst/additive/solvent domains, temperature/time bounds and prespecified yield cutoff; replace the illustrative `DEMO_01` pair.
3. Re-run condition recommendation only when a catalyst-bearing, microwave-aware tool is available; reject catalyst-free proposals at intake.
4. Record reviewed measured yields for at least four distinct reserved candidates through `campaign_cli measure/review`, then run a genuine BayBE fit and compare selected batches.
5. Keep model-predicted priors excluded and QC-flagged until independently measured; never train the optimizer on predictions as observations.
6. Compare only source-matched rows with the same measurement basis (isolated vs assay); compute MAE, top-5 retrieval, solvent top-3 and impurity coverage only after unblinding.

No laboratory experiments are proposed or claimed here; implementation requires qualified safety review.
