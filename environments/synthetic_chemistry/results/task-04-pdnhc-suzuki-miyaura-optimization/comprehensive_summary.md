# Task 04 — comprehensive experimental summary

[Task](../../tasks/task-04-pdnhc-suzuki-miyaura-optimization/README.md) · [Benchmark](../../benchmarks/task-04-pdnhc-suzuki-miyaura-optimization/README.md) · [Results inventory](README.md) · [Focused comparison](comparison_report.md)

This document consolidates every recorded computational run for **task-04-pdnhc-suzuki-miyaura-optimization**. It covers objectives, setup, methodology and parameters per experiment; consolidated comparison tables; quantitative metrics; achievements, shortcomings and their causes; and evidence-based conclusions and next steps. **Blind boundary:** no withheld benchmark yield, measured optimum, original paper or exact-reactant-pair literature record was accessed. Literature rows are general reaction-class/catalyst-family expectations, not exact-pair measurements. All reported numbers are model outputs or counts; none is a laboratory result.

---

## 1. Objective and experimental scope

Blind multi-tool evaluation for the Suzuki–Miyaura coupling of 4-chloroanisole (`COc1ccc(Cl)cc1`) with 4-(trifluoromethyl)phenylboronic acid (`OB(O)c1ccc(C(F)(F)F)cc1`) to target `COc1ccc(-c2ccc(C(F)(F)F)cc2)cc1`, under a Pd-NHC catalyst constraint. Goals: product prediction, route recovery, condition/catalyst recommendation, yield ranking, loading optimization, side-product identification and full provenance. Fourteen tool calls were recorded across internal platform tools, an external open-source model and a local optimizer pipeline.

---

## 2. Experiment-by-experiment objectives, setup, methodology and parameters

| # | Experiment | Objective | Setup / tool | Parameters / input | Output |
|---:|---|---|---|---|---|
| 1 | Input validation | Verify structures | RDKit 2025.09.6, local | three supplied SMILES | all valid, canonical identity preserved |
| 2 | Retrosynthesis | Generate routes from target | internal `retrosynthesis` `6b053cb3a…` | `target_mol` = target SMILES | 5 routes (top0–top4), 917 KB scoring JSON |
| 3 | Forward prediction | Predict product without target hint | internal `forward_reaction` `6b053cb8…` | dot-separated reactants; empty intermediates | 30 ranked products; top-1 = target |
| 4 | Impurity prediction | Identify side products | internal `impurity_prediction` `6b0540db…` | reactants + validated product | 15 candidates; 9 distinct side products retained |
| 5a–c | Condition recommendation | Rank ≤10 conditions | internal `condition_recommendation` `6b0540e0…`, `6b0543a9…`, `6b058bc6…` | reactants + product; identical payload each retry | three failures: GLM HTTP 429; third also Discovery RSI 300 s timeout |
| 5d | Condition recommendation | Rank ≤10 conditions | internal `condition_recommendation` `6b07c97c…` | same payload | 10 conditions; yields 31.285–47.447% |
| 6 | Order-sensitivity probe | Test yield robustness | internal `condition_recommendation` `6b07dac0…` | reversed reactant order | yields 22.066–77.420%; catalyst/base absent; rejected |
| 7 | Condition optimization | Select best condition | post-hoc ranking, local | score × feasibility; validation-reason sanity filter | C1 selected; C9 rejected |
| 8 | Parrot inference | Independent external conditions | Parrot USPTO-Condition, conda `parrot_sc01`, torch 2.2.2+cpu, transformers 4.30.2, compatibility shims | `reactants>>product` | 15 predictions; top-1 toluene log score −1.3208 |
| 9 | Parrot Reaxys attempt | Temperature prediction | Parrot Reaxys config | same reaction SMILES | unavailable: license-gated weights |
| 10 | Literature similarity | Compare routes/catalyst/side products to literature | public Pd-NHC Suzuki papers, post-hoc | general reaction-class context | family/class consistency; no exact-pair data |
| 11 | Pd-NHC-constrained design | Enforce Pd-NHC via explicit space | local `reaction-optimize`, BayBE v1 | 6 Pd-NHC families × base × solvent × T × t × conc | 1,944 candidates; 8 all-Pd-NHC recommendations |
| 12 | Pd-NHC yield attempt | Attach frozen yields | local `reaction-optimize --yield-model` | 8 Pd-NHC candidates, no resolved SMILES | 9/9 yields unavailable |
| 13 | Loading-aware yield run | Encode loading, attach yields | local `reaction-optimize --yield-model` | loading 0.005/0.02/0.05 equiv (=0.5/2/5 mol%) + resolved catalyst/base SMILES | 144 candidates; 9/9 yields 8.105–8.886% |
| 14 | Persistent campaign | Snapshot grid, reserve HTE runs | `campaign_cli create/next` | loading-aware campaign JSON | campaign `a19bfc94…`, 6 reserved experiments, zero measurements |

No wet-lab experiment, model training or new service job was run while packaging these folders.

---

## 3. Consolidated comparison tables

### 3.1 Product, routes and side products

| Aspect | Our outcome | Literature / benchmark expectation | Assessment |
|---|---|---|---|
| Top-1 product | `COc1ccc(-c2ccc(C(F)(F)F)cc2)cc1`, model score 1.0, feasibility 0.9934 | Expected Suzuki coupling product | **Better/met** |
| Routes | 5: Suzuki ×3, Negishi ×2 | Suzuki is standard biaryl disconnection | **Comparable** |
| Exact supplied pair in top-5 | No; R2 partially compatible (boronic acid recovered) | Direct aryl chloride + boronic acid is obvious | **Underperformed** |
| Native route scores | Null/placeholder | Ranked native confidence expected | **Unavailable** |
| Side products | 9: over-coupling, homocoupling, protodehalogenation, demethylation | Three canonical Suzuki side classes | **Comparable** (demethylation lower plausibility) |

### 3.2 Conditions and Pd-NHC constraint

| Parameter | Our outcome | General literature expectation | Assessment |
|---|---|---|---|
| Catalyst from yielding tools | generic "palladium catalyst"; Parrot top-6 no Pd | Pd + NHC ligand for aryl chloride | **Underperformed / partial** |
| Base | generic "base" | K2CO3 / K3PO4 / Cs2CO3 typical | **Missing identity** |
| Solvent (internal top) | water/1,4-dioxane | Aqueous dioxane is standard | **Comparable** |
| Temperature | 100–110 °C (internal); 60–110 °C (design) | Elevated T for aryl chlorides | **Comparable** |
| Native predicted yield | 32.338% (8/10); 47.447% rejected | No matched measurement available | **Unverifiable** |
| Pd-NHC candidates | 8 named families from local optimizer | IPr / IPent / chloro-dimer / indenyl / DMS are literature-supported | **Met at family level** |
| Catalyst loading | 0.5 / 2 / 5 mol% encoded in equivalents | reduced loading with ≥90% retention is target | **Encoded, not validated** |
| Loading-aware frozen yield | 8.105–8.886%, identical across loadings for same catalyst/base | yield model should respond to loading | **Underperformed** |

### 3.3 Quantitative metrics

| Metric | Value | Semantics |
|---|---:|---|
| Top-1 exact target match | 1/1 | canonical identity |
| Forward model score / feasibility | 1.0 / 0.9934252567071588 | model scores, not yield |
| Forward candidates returned | 30 | ranked list |
| Routes / Suzuki / Negishi | 5 / 3 / 2 | counts |
| Conditions returned | 10 | 3 distinct yield values |
| Recommended condition (C1) yield | 32.33824074268341% | native model field |
| C1 feasibility / native score / composite | 0.78 / 0.6170 / 0.4813 | native and derived scores |
| Rejected nominal high yield (C9) | 47.446632385253906% | feasibility 0.20 |
| Unique internal yields | 31.285 / 32.338 / 47.447% | 8/10 share 32.338 |
| Order-sensitive invalid-run range | 22.066–77.420% | no catalyst/base |
| Parrot predictions / top log score | 15 / −1.3208 | log score, not yield |
| Pd-NHC design candidates | 1,944 → 8 (all Pd-NHC) | heuristic scores 0.55/0.75 |
| Loading-aware candidates | 144 → 8 recommended | 0.5/2/5 mol% |
| Loading-aware frozen yields | 9 available, 8.105–8.886% | structure-based only |
| Persistent campaign | 6 reserved experiments | 0 reviewed measurements |
| Matched experimental yield / MAE / retention / top-5 accuracy | null | withheld data unavailable |

---

## 4. Key improvements and where results performed better

1. **Product prediction:** top-1 forward prediction matched the target by RDKit canonical identity with the maximum native score (1.0) and high feasibility (0.9934), without supplying the intended product to the predictor.
2. **Side-product classes:** over-reaction/poly-arylation, homocoupling and protodehalogenation predictions align with the three canonical Suzuki side reactions.
3. **Pd-NHC constraint:** satisfied by the local optimizer's explicit `condition_space`; all eight recommendations named Pd-NHC precatalyst families. No yielding tool could supply this.
4. **Loading encoding:** corrected an earlier limitation — catalyst loading was successfully created and fed through `Condition.equivalents` at 0.5/2/5 mol%, and the optimizer enumerated it across 144 candidates.
5. **Attaching yields to organometallics:** supplying resolved SMILES via `condition_component_smiles` turned 9/9 previously unavailable frozen-model yield predictions into numeric outputs.
6. **Reliability discipline:** rejected the nominal highest-yield condition (C9) for low feasibility and rejected the entire order-reversed high-yield run as chemically invalid; three HTTP 429 failures were recorded rather than hidden.

---

## 5. Performance gaps, shortcomings and reasons

| Gap | Reason / evidence |
|---|---|
| Exact reactant pair absent from top-5 retrosynthesis | Model explored bromide/iodide/boronic-ester alternatives; native scores were placeholders; direct branch kept separately |
| Three condition-recommendation failures | GLM rate limiting (HTTP 429) on all tokens; Discovery RSI backup timeout; success only on 4th attempt |
| Weakly discriminating yield | 8/10 conditions share 32.338%; yield is largely reaction-level |
| Yield input-order sensitivity | Reversing reactants changed yields up to 77.420% for catalyst-free records; tool output unstable to ordering |
| No Pd-NHC from yielding tools | Internal tool returned generic strings; Parrot returned no catalyst in top 6 and copper later; only design tool produced NHC families |
| Loading-blind yield model | `pipeline.py:74`: frozen ReactionT5 encodes reactants, catalyst/reagent structures, product only; identical yields at 0.5 and 5 mol% for same catalyst/base |
| No validated low-loading optimum | Tool does not run lab hardware; operating windows need ≥3 preregistered independent runs/point; campaign has zero measurements |
| Benchmark comparison impossible | Blindness forbids accessing withheld measured yields/optimum; no exact-pair literature value obtained |
| Parrot chemical mismatch | Trained on broad USPTO conditions; predicted toluene/ether/THF and no Pd for an aryl-chloride Pd-NHC coupling |
| External-model contamination risk | Cannot be excluded despite no prohibited lookups |

---

## 6. Limitations

- All yields are model fields, not measurements; score semantics differ across tools and were not converted into common probabilities.
- Literature references are catalyst-family/class analogies; no exact-pair yield, optimum or measured catalyst ranking was consulted.
- Parrot weights ran under compatibility shims in an isolated environment; its Reaxys temperature weights were license-gated.
- Local optimizer design candidates have identical heuristic scores and zero verified precedents for this pair.
- The frozen yield advisor ignores loading, solvent, temperature, time, concentration and workup; its numbers cannot support condition- or loading-specific claims.
- No experimental superiority, MAE or improvement is claimed; `achieved_metrics.json` leaves these values `null`.
- Raw service exports, account-scoped identifiers and signed URLs are deliberately excluded from this repository.

---

## 7. Major findings

1. Correct product connectivity was top-ranked in a blind forward prediction.
2. Chemically valid Suzuki/Negishi routes and canonical side-product classes were recovered, but the supplied reactant pair was not retrosynthetically top-ranked.
3. Condition prediction required four attempts due to service failures and produced weakly discriminating, generic-catalyst results.
4. Yield rankings based on native scores can be artifacts: high yields came from chemically invalid, catalyst-free records.
5. The Pd-NHC constraint was achievable only by a locally supplied optimizer with an explicit design space, not by the yielding models.
6. Catalyst loading is expressible as equivalents, but a structure-only yield model cannot evaluate reduced-loading retention.
7. A persistent campaign now snapshots the NHC × loading grid with six reserved runs; validation awaits real measurements.

---

## 8. Future improvement opportunities

1. **Measured HTE campaign:** execute the six reserved experiments under an approved protocol, then supply real assay yields with unique execution/analytical references via `campaign_cli measure` and `review`; BayBE fits after ≥4 reviewed distinct candidates.
2. **Preregistered operating-window study:** ≥3 independent runs per point at 0.5 vs 5 mol% for the best catalyst/base to test ≥90% measured yield retention.
3. **Loading-aware yield model:** train/connect a model with mol%, base, solvent and temperature features; the frozen ReactionT5 cannot support loading claims.
4. **Authentic Pd-NHC descriptors:** add steric/electronic or computed complex descriptors so catalyst ranking moves beyond equal heuristic scores.
5. **Benchmark validation:** compare frozen predictions with withheld data only in the separate non-blind evaluation stage.
6. **Service robustness:** re-run condition recommendation with normalized reactant order once quota allows, preserving the failure log.

---

## 9. Conclusion

The workflow achieved its computational prediction objectives — correct product, credible routes and side products, a defensible condition ranking, Pd-NHC design candidates and a loading-aware frozen-yield design set — while preserving full provenance and refusing to fabricate unavailable data. It did **not** achieve a validated low-loading, yield-optimal recipe: the yield model is blind to loading and no measured campaign data exist. Overall status remains **partial**; no experimental superiority is claimed. See [achievements](achievements_and_comparison.md), [gaps](gaps_and_improvement_plan.md), [metrics](../../benchmarks/task-04-pdnhc-suzuki-miyaura-optimization/achieved_metrics.json) and [run log](run_log.md).
