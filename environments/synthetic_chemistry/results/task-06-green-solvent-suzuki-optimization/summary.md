# Task 06 — comprehensive results summary

[Task and inputs](../../tasks/task-06-green-solvent-suzuki-optimization/README.md) · [Literature benchmark](../../benchmarks/task-06-green-solvent-suzuki-optimization/README.md) · [Result inventory](README.md) · [Focused comparison](comparison_report.md)

## 1. Scope and evidence status

This task evaluated a multi-tool computational workflow for replacing a conventional solvent with a greener medium in a microwave-assisted Suzuki–Miyaura coupling. Benchmark reaction: bromobenzene `Brc1ccccc1` + 4-methoxyphenylboronic acid `COc1ccc(B(O)O)cc1` → 4-methoxybiphenyl `COc1ccc(-c2ccccc2)cc1`. Nine stages were actually executed: RDKit validation, Boltzmann retrosynthesis, forward prediction, two condition-recommendation attempts, impurity prediction, a local BayBE design campaign, frozen ReactionT5 yield estimation, and a curated-recipe search. Literature comparison was performed only after outputs were frozen. **No laboratory experiment was performed; no measured yield or measured E-factor exists.** Literature values are from the verified Salami et al. 2025 paper (DOI 10.1002/open.202500138); model outputs are from named jobs recorded in [run_log.md](run_log.md). User-reported 85%/38% yields were disclosed before the runs and were never passed to a tool, so full blinding was compromised; training-data provenance is unknown.

## 2. Consolidated outcome table — all executed stages

| # | Stage | Objective | Parameters / inputs | Key output | Status |
|---:|---|---|---|---|---|
| 1 | RDKit validation | Parse and canonicalize all structures | 17 SMILES: reactants, product, 10 media components, DES components, impurity candidates | 17/17 valid; exact canonical matches | PASS |
| 2 | Retrosynthesis | Derive routes from target only | `target_mol=COc1ccc(-c2ccccc2)cc1` | 55 routes; top route uses supplied reactants; raw yield field 75.177% (basis undocumented) | PASS for route consistency |
| 3 | Forward prediction | Predict product without target | `Brc1ccccc1.COc1ccc(B(O)O)cc1` | Top-1 = target, score 0.99999998; feasibility 0.99975 | PASS exact string match |
| 4 | Condition recommendation (attempt 1) | Get catalyst/base/solvent/conditions | same reactants + product | Failed: 3× HTTP 429 + 300 s backup timeout | FAILED (transient) |
| 5 | Condition recommendation (retry) | Same, distinct new job | same inputs | 10 candidates, all dioxane/water; top Pd(dppf)Cl₂/Na₂CO₃, 100–110 °C, yield field 52.63% (basis undocumented) | PARTIAL |
| 6 | Impurity prediction | Candidate side products | reactants + product | 12 condition-blind candidates including biphenyl; Pd-black not representable | NOT EVALUABLE for direction |
| 7 | Local design campaign | Full condition-space optimization | 4 catalysts × 2 bases × 10 media × 3 temps × 2 times = 480 candidates | 12-run diverse batch; all DES ratios included | PASS for design |
| 8 | Frozen ReactionT5 yields | Attach yield estimates | catalyst/base SMILES supplied | 13 numeric estimates (32.1–72.0%); model input has no solvent/temp/time | SOLVENT-BLIND |
| 9 | Curated recipe search | Retrieve experimental precedent | ORD v2 SQLite | 0 matching recipes; `unsupported` | NO DATA |

## 3. Consolidated comparison against literature benchmarks

| Metric | Literature / benchmark | Our result | Comparability | Verdict |
|---|---|---|---|---|
| Reaction identity | Exact Suzuki coupling | 55 routes; exact forward match | Direct | PASS |
| Solvent screen (Table 1) | 10 media, NMR yields at 120 °C/30 min/Pd(OAc)₂; DES 1:2/1:4 = 72%, 1:8 = 64%; best choline chloride/EG 83%; DMF 62% | No solvent ranking; tool returned dioxane only | No matched rows | FAIL / NOT ACHIEVABLE via SMILES-only interface |
| DES in top 3 | DES 1:4 = 72% fixed conditions | DES present in batch, not ranked | — | NOT EVALUABLE |
| Yield MAE ≤15 pp | Requires matched rows | 0 matched rows; naive gaps −3.57 pp (DES) and −26.99 pp (DMF) are invalid | Conditions differ | NOT EVALUABLE (n=0) |
| Green vs conventional | DES 72 − DMF 62 = +10 pp (Table 1) | No comparable pair | — | NOT EVALUABLE |
| Catalyst family | Table 2 dppf 80–82%; Pd(OAc)₂ 72%; Pd(PPh₃)₄ 49% | Pd(dppf)Cl₂ top-ranked; local prior favors Pd + carbonate | Qualitative | ALIGNED |
| Base | Na₂CO₃ 1.25 equiv | Na₂CO₃ top-ranked; equivalents 1.25 | Direct for base | ALIGNED |
| Optimized protocol | 1:4 DES, dppf·CH₂Cl₂ 1.5 mol%, 129 °C/15 min; 85% NMR / 75% isolated | 129 °C/15 min rows exist; no selected protocol | Partial | PARTIAL |
| Impurity direction | No row-level observations supplied | Condition-blind candidates; Pd-black not representable | — | NOT EVALUABLE |
| ICH Q3C exclusion | DMF/MeCN Class 2, EtOH Class 3 stated; official table not retrieved | Dioxane default likely violation | Unresolved | UNRESOLVED |
| E-factor / waste | CHEM21/PMI assessed; no masses supplied | 22.54 scenario (0% recovery), 3.29 (95%) | Scenario only | SCENARIO ONLY |
| Substrate scope | Scheme 3 / SI scope not transcribed | Only model reaction | — | NOT EVALUABLE |
| Duration | 15 min optimized; 30 min gram scale | Grid includes both; no experimental comparison | Partial | PARTIAL |
| Blinding | Ground truth withheld during prediction | User yields disclosed before runs | — | COMPROMISED |

## 4. Key improvements and where results performed better

1. **Structure and reaction recovery (strongest result).** Both retrosynthesis and forward prediction independently recovered the exact benchmark coupling; the forward top-1 matched the target SMILES exactly with a model score near 1.0. This is the most reliable positive outcome.
2. **Catalyst-family and base alignment.** Without literature input, the tool ranked a dppf palladium catalyst and Na₂CO₃ first, matching the paper's best catalyst family (PdCl₂dppf 80%, PdCl₂dppf·CH₂Cl₂ 82%) and its chosen base.
3. **Condition-space coverage.** Unlike the SMILES-only Boltzmann tool, the local optimizer compiled a 480-candidate grid and a 12-run diverse batch covering all three DES ratios (1:2, 1:4, 1:8), all greener media and all conventional controls. This is a real advance in experimental design over the first condition tool.
4. **Transparent uncertainty handling.** Every uncomputable metric was labelled (`NOT EVALUABLE`, `NOT ACHIEVABLE`, `SCENARIO ONLY`, `UNRESOLVED`) rather than filled with assumed values; no literature yield was used as a campaign measurement.
5. **Quantified model-behavior diagnostic.** The yield model's solvent blindness was measured, not merely asserted: within-pair spread ≤0.117 pp versus 39.73 pp across catalyst identity.
6. **Waste sensitivity made explicit.** An E-factor scenario with a declared boundary and recovery sweep (22.54 → 3.29) was produced instead of a fabricated single number.

## 5. Performance gaps and shortcomings

- No comparable solvent yield ranking; DES top-3 cannot be assessed.
- No MAE (0 matched rows), no green-vs-conventional yield claim.
- No selected optimized protocol from predictions.
- No impurity direction; Pd-black cannot be represented as SMILES.
- No official ICH classification for most components; dioxane default not excluded.
- No measured E-factor; no mass-balance/recovery data.
- No substrate-scope predictions.
- Full blinding compromised; training-data provenance unknown.
- Self-assessed objective completion ≈43% (6/14 fully achieved, 2 partial, 7 not achieved) — internal rubric, not an official score.

## 6. Possible reasons for underperformance

1. **Interface gap:** the four Boltzmann synthesis tools accept only reactant/product SMILES; solvent, ratio, loading, temperature and time cannot be supplied, so all 10 condition candidates defaulted to dioxane/water.
2. **Model-input gap:** frozen ReactionT5 encodes only reactants, catalyst/reagent SMILES and product; solvent/temperature/time changes cause ≤0.117 pp yield variation, so the yield column cannot discriminate media.
3. **Data gap:** zero curated ORD v2 recipes matched the exact pair; bundled seeds are illustrative and excluded from precedent retrieval.
4. **Measurement gap:** Bayesian optimization learns condition effects only from reviewed lab measurements; none exist, and literature yields must not be used as observations.
5. **Boundary gap:** no workup masses, recovery or water policy; E-factor can only be a labelled scenario.
6. **Blinding gap:** user-reported outcomes were disclosed before the runs; training/corpus cutoff versus the 2025 paper is unresolved.
7. **Operational notes:** one condition job failed on rate limiting/timeout and succeeded only as a distinct retry; a notebook-kernel Python environment shadowed the local tool's RDKit and was resolved by clean shell invocation.

## 7. Important metrics at a glance

| Metric | Value |
|---|---|
| Structures validated | 17/17 |
| Retrosynthesis routes / correct top route | 55 / yes |
| Forward top-1 model score | 0.99999998 |
| Condition candidates returned (Boltzmann) | 10 (all dioxane/water) |
| Local candidates compiled | 480 |
| Local diverse batch size / DES rows | 12 / 4 |
| Yield estimates / solvent-blind | 13 / confirmed |
| Within-pair vs across-catalyst yield spread | 0.117 pp vs 39.73 pp |
| E-factor scenario (0% / 95% recovery) | 22.54 / 3.29 |
| Matched rows for MAE | 0 |
| Project-measured yield | none |

## 8. Limitations and conclusion

All chemical-performance numbers here are tool predictions, design heuristics or literature observations — none is a measured experimental result. The workflow successfully reproduced the benchmark reaction and proposed chemically sensible catalyst/base conditions, and its local design tool achieved broad condition coverage including DES. It did not achieve the core quantitative objectives because no available yield model encodes the variables the task asks to optimize and no reviewed measurements exist to train the optimizer. Literature values were deliberately kept out of prediction inputs. The designated acceptance targets remain PASS for structure/route consistency, PARTIAL for protocol parameters, and NOT EVALUABLE or NOT ACHIEVABLE for all yield-, hazard-, impurity-, waste- and scope-dependent metrics.

## 9. Future improvement opportunities

1. Acquire or validate a condition-aware yield model that accepts solvent components, composition ratio/basis, catalyst loading, temperature and time.
2. Execute the designed 12-run batch under a preregistered protocol with matched NMR or isolated basis; record reviewed measurements and run Bayesian optimization rounds.
3. Retrieve official ICH Q3C(R9) classifications for every component and define whether the exclusion covers the precatalyst-associated CH₂Cl₂.
4. Record all input/workup/recovery masses and water policy to compute a measured E-factor/PMI.
5. Curate Table 2/3, response-surface and Scheme 3 scope rows; evaluate only matched rows with explicit denominators.
6. Require experimental evidence for impurity directions and track Pd-black as a materials event.
7. Freeze predictions and hashes before any future unblinding; keep literature-only information behind the evaluation boundary.
