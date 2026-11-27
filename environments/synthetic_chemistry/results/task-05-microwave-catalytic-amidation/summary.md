# Task 05 — comprehensive results summary

[Task](../../tasks/task-05-microwave-catalytic-amidation/README.md) · [Benchmark](../../benchmarks/task-05-microwave-catalytic-amidation/README.md) · [Results inventory](README.md) · [Metrics](../../benchmarks/task-05-microwave-catalytic-amidation/achieved_metrics.json)

## 1. Executive summary

Task 05 set out to evaluate a multi-tool workflow for a blind, microwave-assisted, **catalytic** direct amidation of a hindered aryl amine/aryl acid pair. All work conducted was **computational and documentary** — one internal condition-recommendation job, five verified literature sources, a literature comparison, and two runs of a local Bayesian design-of-experiments tool. **No wet-laboratory experiment, measured yield, or model training was performed**, so no experimental superiority can be claimed.

The central finding is negative but clear: the internal condition tool **failed the task's defining constraint** — every one of its ten recommendations had an empty catalyst identity and no microwave mode or time — so it cannot satisfy a catalytic-microwave objective regardless of its yield numbers. The workflow's real strengths were in *detection and handling*: the constraint failure was caught and recorded, contextual literature was verified, predicted yields were prevented from contaminating optimizer measurements, and a catalytic design space was compiled. Overall benchmark status is **`partial / NOT_EVALUABLE`** because the designated 2025 HTE paper was never identified and no measured rows exist.

## 2. What was actually "conducted" (scope of evidence)

| Run | Type | What it was | What it was not |
|---|---|---|---|
| `condition_recommendation` job `6b05bcdf8b9d410520f9a7b3` | Model inference (internal platform) | Ten ranked conditions + native scores/predicted yields | Not an experiment; no measured validation |
| PubMed/Crossref/PMC retrieval + `grounded-citations` | Documentary | Five verified contextual sources with verbatim evidence | Not the designated HTE paper |
| `reaction-optimize` catalytic campaign (BayBE v1) | Local software design | 192 candidates → 6 diverse initial designs; persistent campaign, 4 reserved | No measurements; no Bayesian fit |
| Prior-yield seeded campaign | Local software design | 10 QC-flagged excluded priors → 8 untested designs | Priors never treated as measurements |

## 3. Consolidated results — all outcomes

| # | Outcome | Evidence / value | Source |
|---:|---|---|---|
| 1 | Condition job completed without duplicate submission | status `completed`, one submit + one poll | [run_log.md](run_log.md) |
| 2 | Ten conditions returned | 10 ranked records | [condition_summary.json](condition_summary.json) |
| 3 | Catalyst constraint failed | `catalyst_name: []` in all 10 | [achieved_metrics.json](../../benchmarks/task-05-microwave-catalytic-amidation/achieved_metrics.json) |
| 4 | Microwave/time fields missing | no heating mode, no time; temp 20–80 °C only | [condition_summary.json](condition_summary.json) |
| 5 | Native predicted yields | 53.52–60.67%; only 5 distinct values across 10 rows | [condition_summary.json](condition_summary.json) |
| 6 | Top-1 native score / feasibility / yield | 0.6664 / 0.86 / 56.81% (pyridine, pyridine, 20–30 °C) | [achieved_metrics.json](../../benchmarks/task-05-microwave-catalytic-amidation/achieved_metrics.json) |
| 7 | Five literature sources verified | L1–L5, DOI/PMID/PMC + verbatim quotes | [papers.md](../../benchmarks/task-05-microwave-catalytic-amidation/papers.md) |
| 8 | Contextual comparison produced | criteria audit + literature comparison | [comparison_report.md](comparison_report.md) |
| 9 | Catalytic design space compiled | 192 candidates; 3 catalyst families; 4 solvents; 4 temps; 4 times | [optimizer_campaigns.json](optimizer_campaigns.json) |
| 10 | Diverse initial designs selected | 6 in stateless run; 4 reserved in persistent campaign `cc551cb41…` | [optimizer_campaigns.json](optimizer_campaigns.json) |
| 11 | Prior predicted yields seeded safely | 10 rows, `status: excluded`, 2 QC flags, 20 QC messages, 0 reviewed | [optimizer_campaigns.json](optimizer_campaigns.json) |
| 12 | Second batch of untested designs selected | 8 candidates from 32-condition space | [optimizer_campaigns.json](optimizer_campaigns.json) |
| 13 | No Bayesian fit | 0 reviewed measurements in both campaigns | [achieved_metrics.json](../../benchmarks/task-05-microwave-catalytic-amidation/achieved_metrics.json) |
| 14 | All experimental metrics unavailable | MAE, top-5, solvent top-3, class floor, time, impurity = `null` | [achieved_metrics.json](../../benchmarks/task-05-microwave-catalytic-amidation/achieved_metrics.json) |
| 15 | Repository integration validated | 16/16 workspace tests pass; all JSON valid; diff clean | [validation_receipt.md](validation_receipt.md) |

## 4. Consolidated comparison against literature benchmarks

Each row states what the literature reports, what our workflow produced, and whether a like-for-like comparison was possible. No cell conflates a model score with a measured yield.

| Dimension | Literature benchmark (verified) | Our workflow output | Comparison status |
|---|---|---|---|
| Reaction class | Direct catalytic amidation of acids + amines [1][2][3] | Same class targeted; illustrative hindered pair | Comparable at class level |
| Catalyst identity | CAN [1]; borate ester [2]; borane–pyridine 5 mol% [3]; fluorous boronic acid [4]; ortho-aminophenylboronic acid [5] | `catalyst_name: []` in all 10 tool conditions; catalyst families present only in local optimizer design space | **FAIL** for tool; optimizer covers families as hypotheses |
| Heating mode | Open microwave (L1) [1]; thermal 20 h (L2) [2] | Not returned by tool; not encoded as microwave in optimizer | **NOT COMPARABLE** |
| Reaction time | 20 h thermal (L2) [2] | Not returned by tool; optimizer space 0.25–20 h | **NOT EVALUABLE** |
| Solvent | Solvent-free (L1) [1]; t-BuOAc / toluene (L2) [2] | Pyridine, dioxane, DCM reagent sets; optimizer includes t-BuOAc, toluene, dioxane, none | No matched catalytic-microwave grid; no ranking possible |
| Hindered / electron-poor anilines | Explicitly tolerated by borate catalyst (L2) [2] | Substrate is hindered; no experimental result | Context only |
| Yield | >80% isolated for specific amides after 20 h (L2) [2] | 53.52–60.67% native model estimates for a *different* pair | **NOT COMPARABLE** — different substrate and basis |
| Functional-group tolerance | Halo/nitro/alkene tolerance (L3) [3] | None assessed | Not evaluated |
| Side products | Named target-paper products required for scoring | None returned or measured | Not evaluated |
| Exact-pair result | No source reports this acid + amine | No measured yield | **NO REFERENCE ROW** |

Literature sources: [1] https://doi.org/10.3390/molecules25081761 · [2] https://doi.org/10.1039/d4sc07744j · [3] https://doi.org/10.3390/molecules29010268 · [4] https://doi.org/10.1039/D3RA03300G · [5] https://pmc.ncbi.nlm.nih.gov/articles/PMC13449423. Product-class precedents: [6] https://pubmed.ncbi.nlm.nih.gov/29786439 · [7] https://pubmed.ncbi.nlm.nih.gov/9010628.

## 5. Key improvements and areas where our work performed better

These are genuine strengths of the *workflow*, not claims of chemical superiority:

1. **Constraint detection succeeded where the tool failed.** The audit identified the empty-catalyst defect explicitly rather than accepting high nominal scores. A naive review would have reported the 0.86-feasibility top hit as a success; our audit classified it `catalyst_constraint_met: false` — the correct call against the task.
2. **Prior-yield handling avoided measurement contamination.** Reusing earlier predicted yields as true observations would have made the Gaussian process fit on predictions. We attached them as `excluded` with QC flags, generated 20 QC messages, and confirmed zero reviewed measurements and zero BO fits — a demonstrably sound data-hygiene outcome, including an explicitly rejected `reviewed` variant.
3. **Catalytic coverage restored after tool failure.** The local optimizer compiled a condition space containing all three verified catalyst families (CAN, borane–pyridine, ortho-aminophenylboronic acid) and the solvents used by the closest precedent (t-BuOAc, toluene) — recovering catalytic options the internal tool never proposed.
4. **Evidence tiers kept distinct.** Every claim is labelled as model prediction, heuristic design score, verified literature fact, or unavailable; no score was relabelled as a percentage yield, and all missing metrics are `null`.
5. **Reproducibility and hygiene.** One job submitted and polled (no duplicate), full call log, sanitized artifacts, all three repository folders linked and validated (16/16 tests), no credentials or signed URLs redistributed.

## 6. Performance gaps and shortcomings

1. **Primary objective not met:** the internal tool produced no catalyst-bearing, microwave-timed condition, so the core deliverable — a ranked catalytic-microwave protocol — does not exist from that tool.
2. **No quantitative performance:** no measured yield, matched literature yield, MAE, top-5 optimum retrieval, solvent top-3, steric-class floor, time comparison or side-product match; all are `null`.
3. **Yields non-discriminating:** five values repeat across ten chemically distinct conditions, so ranking by predicted yield is not meaningful.
4. **No optimizer learning:** both campaigns reached zero reviewed measurements; every selected condition is a diverse cold-start design, not an optimized recipe. Some designs (e.g., CAN/toluene/30 °C/20 h) are chemically questionable.
5. **Benchmark unresolved:** the designated 2025 HTE paper is unidentified; none of L1–L5 supplies the exact-pair matrix, so paper-specific scoring is impossible.
6. **Literature coverage partial:** Europe PMC timed out and Crossref was intermittently unreachable; retrieval was PubMed/PMC-only. No exact-pair yield exists anywhere in the retrieved set.

## 7. Possible reasons for underperformance

- **Tool-contract mismatch (most direct cause):** `condition_recommendation` accepts only reactant and product SMILES and returns reagent/score fields; it has no catalyst-domain, heating-mode or time inputs, so it cannot express a catalytic-microwave answer. This is a capability limitation, not a prompting failure.
- **Substrate difficulty:** the doubly ortho-substituted pair is sterically hindered; the literature treats anilines as poor dehydrative-amidation substrates [2], making a successful reagent-only prediction chemically unlikely in the first place.
- **Yield-head design:** the internal yield field appears substrate-typical (few repeated values), consistent with a model that estimates a representative yield rather than resolving condition effects.
- **Missing ground truth and measurements:** without the designated paper/SI and without reviewed measurements, neither the tool nor the optimizer had the data needed to rank or improve conditions empirically.
- **Blind-stage integrity rules:** prohibiting exact-pair and reference-paper lookups during generation deliberately withheld the information that could have corrected the recommendations — a correct constraint of the benchmark that nevertheless limits apparent performance.

## 8. Important metrics at a glance

| Metric | Value | Basis |
|---|---|---|
| Conditions returned | 10 | internal tool |
| Catalyst constraint met | No (0/10) | audit |
| Microwave/time returned | No | audit |
| Predicted yield range | 53.52–60.67% | native model, not measured |
| Distinct predicted yields | 5 across 10 conditions | audit |
| Top-1 score / feasibility | 0.6664 / 0.86 | native model |
| Literature sources verified | 5 (L1–L5) | post-hoc |
| Design candidates compiled | 192 | local optimizer |
| Designs selected (stateless / seed) | 6 / 8 | local optimizer |
| Reserved experiments / reviewed measurements | 4 / 0 | persistent campaign |
| Bayesian fits performed | 0 | no measured data |
| Yield MAE / top-5 / solvent top-3 / impurity match | `null` | no ground truth |
| Overall status | `partial_not_evaluable` | — |

## 9. Successful outcomes

- Internal job submitted once, polled to a terminal state, with all native numbers preserved.
- The defining constraint failure detected and correctly classified.
- Five contextual sources verified with exact provenance and verbatim evidence (`citations OK`).
- A 192-candidate catalytic design space covering verified catalyst families and solvent precedents.
- Prior predicted yields reused without contaminating measurements; an unsound alternative explicitly rejected.
- Complete, sanitized, link-valid results package; 16/16 repository tests passing; task integrated into `tasks/`, `benchmarks/`, `results/` without altering earlier tasks.

## 10. Limitations

No experimental validation of any kind. Predictions, heuristic scores and literature facts are distinct and must stay distinct. The designated 2025 HTE paper, the real substrate matrix, the pass cutoff, the reference microwave time and the side-product answers were all withheld or unavailable, so benchmark-specific performance cannot be stated. The optimizer's heuristic scores (0.35 / 0.75) are not calibrated yields; where a frozen yield model is available it does not encode solvent, temperature, time, concentration or equivalents. Coverage is PubMed/PMC-only.

## 11. Future improvement opportunities

1. Identify and register the designated 2025 HTE paper (`SC02_PRIMARY`), extract exact pairs, conditions, isolated yields and side products from tables/SI, and freeze them behind the blind boundary.
2. Supply the real substrate matrix with class labels, allowed catalyst/additive/solvent domains, temperature/time bounds and a prespecified yield cutoff; retire the illustrative `DEMO_01` pair.
3. Re-run condition recommendation only with a catalyst-bearing, microwave-aware tool; reject catalyst-free proposals at intake.
4. Record reviewed measured yields for at least four distinct reserved candidates via `campaign_cli measure/review`, then perform a genuine BayBE fit and evaluate batch performance.
5. Keep all predicted priors excluded and QC-flagged until independently measured; never train the optimizer on predictions.
6. Compare only source-matched rows on the same measurement basis (isolated vs assay); compute MAE, top-5 retrieval, solvent top-3 and impurity coverage only after unblinding.
7. Any laboratory implementation requires qualified safety review; no experiments are proposed or claimed here.

## 12. Overall evidence-based conclusion

The workflow did not produce a valid catalytic-microwave recommendation, and it produced no experimentally supported performance metric; on the task's own criteria the tool output is a **failure** and the benchmark is **NOT_EVALUABLE**. What the workflow did achieve is a rigorous, well-documented negative result: it caught the constraint failure that a superficially plausible output would have hidden, verified the relevant catalytic literature, and built a clean, uncontaminated design pipeline ready for measured data. The highest-value next step is not another prediction run but obtaining the designated ground truth and measured yields, after which the existing campaign infrastructure can be used for genuine optimization and fair scoring.
