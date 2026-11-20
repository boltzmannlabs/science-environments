# Clarithromycin 500 mg Immediate-Release Tablet — Computational Formulation Optimization Benchmark

**Version:** 1.0 | **Date:** 14 November 2026 | **Use:** Agent-scientist benchmark / dry-lab formulation R&D | **Status:** Benchmark specification, not validated product development

> **Integrity statement:** The candidate formulations below are mathematical design points, **not lab-tested formulations**. No dissolution percentages, stability outcomes, compatibility assertions, manufacturability scores, or top-three efficacy rankings have been generated or verified. Any model outputs must be labeled *predicted*, with calibrated uncertainty and evidence provenance; missing models/data must yield *unknown*, not fabricated measurements.

## 1. Clear objective and expected benefit

**Objective:** Identify three experimentally promising, risk-balanced immediate-release (IR), film-coated tablet compositions containing **exactly 500 mg clarithromycin** and **only the eight named excipients**, from at least ten unique mathematically valid formulation candidates, prioritizing robust release performance while minimizing degradation/compatibility and manufacturing risk.

**What is optimized?** The relative concentrations of MCC, crospovidone, povidone K30, colloidal silicon dioxide, magnesium stearate, hypromellose (HPMC), titanium dioxide and PEG 4000; optionally relevant *process settings as separately reported variables* (not silently conflated with compositions). API dose is never an optimization variable. The excipients include core and film coat; core and coating masses must be represented separately and sum to the tablet total.

**Why optimize?** To improve the probability of meeting a benchmark dissolution profile, avoid undesirable delayed release caused by wetting/gelation/polymorphism, reduce chemical/physical degradation risk, maintain flow/compression/coating feasibility, and make the choice of small experimental batches more informative. Optimization does **not** establish therapeutic equivalence, bioavailability, shelf life, GMP suitability, or regulatory approval.

**Primary end-product:** 3 **provisional** candidates with full mg/tablet and %w/w, modeled dissolution profiles and uncertainty **only where a trained and applicable model exists**, explanatory evidence, risk flags, and tests required to confirm claims. If no validated predictive models or relevant experimental observations are supplied, report *unrankable on efficacy* and rank only on transparent design heuristics, explicitly labeling the result.

## 2. Scientific context and critical failure modes

- Clarithromycin is poorly water soluble; dissolution and tablet behavior depend on drug solid form, medium, disintegration, and manufacturing method. Published evidence shows that citrate/carboxylate buffers may induce surface gelation and impede tablet release [R2].
- Another study reports delayed release in tablets containing metastable form I despite faster intrinsic dissolution, associated with phase transition and surface crystal formation [R3]. Thus an API's isolated solubility prediction cannot establish a tablet's dissolution profile.
- A published immediate-release film-coated clarithromycin study [R1] is a useful *nearest formulation-workflow comparator*, but its excipient selection differs (e.g., croscarmellose rather than crospovidone) and its data must not be transferred as though the test composition were identical.
- Marketed 500 mg products establish that MCC, PVP, silica, Mg stearate, hypromellose and titanium dioxide are plausible components, but listed inactive ingredients do **not** disclose quantitative compositions or validate this specified eight-excipient design [R4].
- Published extended-release and gastroretentive formulations are *mechanistic/compatibility references only*, not release-profile targets for IR tablets [R5].

## 3. Inputs that the benchmark must fix before scientific performance comparisons

| Input | Proposed benchmark default | Why needed |
|---|---|---|
| API | Clarithromycin 500 mg/tablet | Non-negotiable dose |
| Target tablet mass | **800 mg/tablet**, including film coat | **Illustrative benchmark assumption**; not specified by the original problem |
| Core/coat allocation | Hypromellose, TiO2 and PEG 4000 designated coating components; remaining ingredients core | Prevent comparing coating material as if core disintegrant |
| Manufacturing route | Wet granulation with PVP K30 **or** direct compression; choose one and record it before comparison | Route changes feasibility and dissolution; cannot assume equivalent |
| API attributes | Form/polymorph, PSD, lot, water content, assay, density | Drives dissolution and manufacturability |
| Excipients | Grades, supplier and PSD, especially MCC, crospovidone, HPMC and PEG 4000 | Grades affect predictions |
| Dissolution method | Defined apparatus, medium/pH, agitation, temperature, sampling times, assay, reference product | “% dissolved at 30 min” is meaningless without method |
| Stability conditions | Packaging, temperature/RH/timepoints, degradants and assay method | Enables comparability |
| RLD or reference | Documented reference product and test profile | Needed for f2/reference similarity |

### Proposed concentration bounds — *benchmark design assumptions, not regulatory limits*

All percentages are **w/w of finished coated tablet**. Define bounds before generation and do not revise them to favor particular candidates.

| Component | Lower bound (% w/w) | Upper bound (% w/w) | Role / location |
|---|---:|---:|---|
| Clarithromycin | Fixed 62.50 | Fixed 62.50 | Core API, 500/800 mg |
| MCC | 15.0 | 32.5 | Core filler/compression aid |
| Crospovidone | 2.0 | 6.0 | Core disintegrant |
| Povidone K30 | 1.5 | 4.5 | Core binder |
| Colloidal silicon dioxide | 0.25 | 1.25 | Core glidant |
| Magnesium stearate | 0.25 | 1.25 | Core lubricant |
| Hypromellose | 1.0 | 3.0 | Film-coat polymer |
| Titanium dioxide | 0.5 | 1.5 | Film-coat pigment |
| PEG 4000 | 0.5 | 2.0 | Film-coat plasticizer |

**Important:** These are synthetic, operational screening bounds adopted to make the test executable. A formulation scientist must approve them; suitability for the selected process, grade, coating solids ratio and jurisdiction must be checked independently. A TiO2-containing film coat also requires a market-specific regulatory assessment.

### Hard constraints

1. `API_mg == 500.0` per tablet, after accounting for assay/potency conventions where applicable.
2. Exactly 8 allowed excipient identities; no unlisted additives. Process solvent, if used and subsequently evaporated, is tracked separately and is not part of final finished-tablet composition.
3. Every excipient within its approved benchmark min/max; candidates with values outside any bound are rejected.
4. Finished tablet sum `abs(sum(w_w_percent) - 100.0) <= 0.1`; ideal mass-balanced candidates sum exactly 100.000%.
5. Mass conservation of core and film coat; all ingredient masses nonnegative.
6. ≥10 unique vectors with meaningful differences (e.g., at least 1 mg in some non-API ingredient); reject duplicates and near-duplicates under declared tolerance.
7. No claim of experimentally verified stability/dissolution without primary lab records; missing evidence must never silently pass an experimentally defined gate.
8. Manufacturing route and film-coat assignment must be fixed or separately stratified.

## 4. Twelve candidate *composition designs* (no predicted response values)

**Unit: mg per finished coated 800 mg tablet**; the API is 500 mg in every row. MCC is the balancing component. All rows satisfy the **illustrative** bounds above. These candidates are exploratory starting points, **not** the ranked final three.

| ID | API | MCC | Crospovidone | PVP K30 | SiO2 | Mg stearate | HPMC | TiO2 | PEG 4000 | Total mg | Total % |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| F01 | 500 | 208 | 25 | 24 | 5 | 6 | 16 | 8 | 8 | 800 | 100.0 |
| F02 | 500 | 198 | 35 | 24 | 5 | 6 | 16 | 8 | 8 | 800 | 100.0 |
| F03 | 500 | 188 | 45 | 24 | 5 | 6 | 16 | 8 | 8 | 800 | 100.0 |
| F04 | 500 | 206 | 35 | 16 | 5 | 6 | 16 | 8 | 8 | 800 | 100.0 |
| F05 | 500 | 190 | 35 | 32 | 5 | 6 | 16 | 8 | 8 | 800 | 100.0 |
| F06 | 500 | 200 | 35 | 24 | 3 | 6 | 16 | 8 | 8 | 800 | 100.0 |
| F07 | 500 | 196 | 35 | 24 | 7 | 6 | 16 | 8 | 8 | 800 | 100.0 |
| F08 | 500 | 200 | 35 | 24 | 5 | 4 | 16 | 8 | 8 | 800 | 100.0 |
| F09 | 500 | 196 | 35 | 24 | 5 | 8 | 16 | 8 | 8 | 800 | 100.0 |
| F10 | 500 | 202 | 35 | 24 | 5 | 6 | 12 | 8 | 8 | 800 | 100.0 |
| F11 | 500 | 194 | 35 | 24 | 5 | 6 | 20 | 8 | 8 | 800 | 100.0 |
| F12 | 500 | 196 | 35 | 24 | 5 | 6 | 16 | 6 | 12 | 800 | 100.0 |

**Normalization:** `%w/w = 100 × ingredient_mg / 800`. Film coat is HPMC + TiO2 + PEG 4000. The range of total coat weights in this design is a *benchmark variable* requiring practical assessment, not a validated coating process.

## 5. Publicly available tools and what each can actually deliver

| Layer | Public tool/resource and link | What it produces | What it **does not** prove | Priority |
|---|---|---|---|---|
| Source data | [PubChem PUG REST](https://pubchem.ncbi.nlm.nih.gov/docs/pug-rest) | API chemical descriptors, molecular identifiers and literature-linked records | Tablet release or excipient compatibility | Essential |
| Molecular features | [RDKit](https://www.rdkit.org/docs/Overview.html) | Structure standardization, molecular descriptors for a trained model | Macroscopic blend/film-coat behavior | Useful |
| Literature mining | [Europe PMC API](https://europepmc.org/RestfulWebService) / [PubMed E-utilities](https://www.ncbi.nlm.nih.gov/books/NBK25501/) | Papers, provenance, open full texts where licensed | Quality of an unseen experimental dataset | Essential |
| Literature/statistical analysis | [SciPy](https://scipy.org/) and [statsmodels](https://www.statsmodels.org/) | Dissolution curve fitting, regression, DoE analysis, uncertainty intervals | Predictive ability without trained data | Essential |
| Dissolution profile calculations | [PTCalc (2026)](https://zenodo.org/records/22957458) | 16 release-kinetics fits; f1/f2 and profile analysis **when measured profile data are provided** | Prospective dissolution predictions from recipe alone | Useful |
| Surrogate models | [scikit-learn](https://scikit-learn.org/) | RF/gradient boosting, validation splits, calibration utilities | Reliable generalization without target-domain data | Essential if data exist |
| Bayesian optimization | [BoTorch](https://botorch.org/) + [GPyTorch](https://gpytorch.ai/) | Candidate suggestion via surrogate models / acquisition functions, confidence estimates | Validated experimental results | Recommended |
| Multiobjective search | [pymoo](https://pymoo.org/) | NSGA-II/Pareto sets with explicit constraints | That Pareto points will work in a tablet press | Recommended |
| Search baseline | [Optuna](https://optuna.org/) | Reproducible constrained search and trial histories | Pharmaceutical predictions by itself | Recommended |
| Statistical DoE | [pyDOE3](https://pydoe3.readthedocs.io/) | Initial experimental designs / factorial sampling | Physical feasibility or release validation | Useful |
| Mechanistic particle simulation | [LIGGGHTS](https://www.cfdem.com/liggghts-open-source-discrete-element-method-particle-simulation-code) or [MercuryDPM](https://www.mercurydpm.org/) | Flow/packing trends *if calibrated particle inputs are provided* | Tablet hardness, content uniformity or stability by default | Optional / high effort |
| Solids/dissolution mechanism | [OpenFOAM](https://www.openfoam.com/) | Transport/flow models with specified physics | Validated clarithromycin dissolution without custom parameterization | Optional / high effort |
| Standards and assay methods | [FDA Dissolution Methods Database](https://www.fda.gov/drugs/drug-approvals-and-databases/dissolution-methods-database) / USP access as licensed | Method selection and relevant regulatory context | One universal acceptance criterion for every product | Essential |

**Recommended minimal open stack:** Python + pandas + NumPy + SciPy + scikit-learn + Optuna/pymoo + BoTorch (if real training data) + PTCalc for profile comparisons + PubChem/Europe PMC for auditable evidence. There is **no publicly established turnkey predictor shown here** that can reliably take these eight percentages and output experimentally accurate clarithromycin dissolution, degradation and compressibility simultaneously. Those predictors require proprietary or experimentally generated data, model training, and external validation.

## 6. Predictions, evidence and uncertainty — required outputs

| Dimension | Output requested | Evidence/measurement needed | Uncertainty and failure flag |
|---|---|---|---|
| Dissolution | D10, D15, D30, D45, D60; complete % release curve; t50/t80 where estimable; f2 against valid reference | Matched medium/apparatus/pH and replicate dissolution runs | 90/95% predictive interval; OOD alert, buffer/polymorph risk |
| Stability | API assay, total/individual degradants after specified exposures, change in dissolution | Stability-indicating HPLC and actual stress/storage results | Unknown if no relevant degradation model; track storage-condition extrapolation |
| API–excipient compatibility | Interaction hypotheses, severity and evidence tier | DSC, FTIR, XRPD, moisture sorption and stressed binary/mixture samples | Hypothesis ≠ demonstrated chemical incompatibility |
| Manufacturability | Flow proxy, compressibility, hardness, friability, sticking/capping, coat integrity, weight variation | Granule PSD, bulk/tapped density, press force, ejection force and actual tablet testing | Cannot infer robust manufacturability from composition alone |
| Model confidence | Model version, training provenance, domain coverage, held-out error and prediction interval | Cross-validation by batch/formulation and independent external set | Mark untrained/OOD outputs unavailable, not zero-risk |

**Validation tiers:** `DESIGN_ONLY` (constraint-checked composition); `LITERATURE_SUPPORTED` (analogous evidence, not direct confirmation); `IN_SILICO_PREDICTED` (named model + version + interval); `LAB_MEASURED` (traceable assay records); `INDEPENDENTLY_REPLICATED` (independent batch/site). A candidate can hold different tiers for different endpoints.

## 7. Pre-registered ranking and rejection logic

**Sequential filter:** hard composition checks → material/process feasibility screening → domain-of-applicability check → any validated predictive model → Pareto ranking → experimental confirmation. Never trade a hard constraint for a better score.

**Illustrative preference weights** (adjust only *before* results are observed): dissolution/reference similarity 40%, stability/degradation 25%, manufacturability 20%, compatibility 10%, and predictive confidence 5%. Use comparable, directionally correct normalized measures and propagate uncertainty; prefer constrained Pareto ranking over a single opaque scalar. Missing evidence is *not* scored as favorable.

**Three distinct finalists:** one best predicted dissolution profile, one best risk-adjusted stability/manufacturability profile, and one high-information/robustness candidate, subject to passing gates. If data are inadequate, provide no fake 'top 3' performance ranking: return three **candidate designs for testing** and mark performance `NOT_PREDICTED`.

**Uncertainty gate suggestion:** candidate must be inside model applicability domain; relevant external MAE/RMSE and interval coverage must be reported. A numeric threshold on model accuracy should be decided after pilot data; do not assert an arbitrary universal percent uncertainty criterion.

## 8. Success criteria (separate computational vs laboratory success)

| Level | Pass conditions | Meaning |
|---|---|---|
| L0 — Artifact completeness | ≥10 unique, valid vectors; 500 mg API; eight excipients only; all concentrations in bounds; total 100% ±0.1%; full provenance; ≥3 proposed experiment candidates | **Computational benchmark achieved** |
| L1 — Scientific evidence | ≥3 relevant primary clarithromycin studies correctly cited; method/polymorph/medium mismatches identified; all claims distinguish observation, inference, and prediction | Literature-grounded benchmark |
| L2 — Model quality | External held-out formulation/batch evaluation; MAE/RMSE and calibrated coverage reported, with honest OOD handling; benchmarked against simple baselines | Credible prediction framework, **not** physical proof |
| L3 — Lab feasibility | Confirm API identity/polymorph, blend/pressability and coating success; acceptable physical quality per pre-agreed pharmacopeial/product specs | Manufacturable prototype |
| L4 — Laboratory performance | Pre-agreed validated discriminatory dissolution method, reference similarity as applicable; acceptable assay/impurities, stability and compatibility under pre-agreed specs | Experimental candidate performance established |
| L5 — Reproducibility | Repeat batches/operators and stability timepoints, documented variability | Stronger product-development confidence |

**Suggested internal (nonregulatory) screening targets — NOT universal release specifications:** target D30 ≥80% **only if** method and reference establish this as appropriate; disintegration ≤15 min when suitable for method; friability ≤1.0% when applicable; robust hardness/flow/weight uniformity in validated process windows; f2 ≥50 only under appropriate reference sampling/variance conditions. FDA notes dissolution methods and acceptance criteria are product-specific [R6]. Binding actual regulatory specs must be obtained from the applicable monograph/product and quality team; an IR label alone does not justify these numbers.

## 9. Recommended experimental tests

1. **API and raw materials:** XRPD for API form, particle-size distribution, water content (KF), FTIR/DSC/TGA and supplier grade verification.
2. **Pre-formulation compatibility:** binary API–excipient accelerated stress tests plus targeted multi-component blends; stability-indicating HPLC, XRPD, FTIR, DSC; include moisture and temperature controls.
3. **Blend/granule properties:** bulk/tapped density, flow rate/shear, Hausner ratio/Carr index, PSD, moisture, content uniformity.
4. **Tablet core:** compression-force sweep; tensile strength/hardness, friability, porosity, ejection force, weight uniformity, disintegration.
5. **Coating:** coat weight gain, surface defects, adhesion, thickness, plasticizer effects and dissolution impact vs uncoated core.
6. **Dissolution:** validated discriminatory IR method; 6 or more units as justified; profiles at 5, 10, 15, 20, 30, 45 and 60 min; alternate media (including citrate-containing vs suitable non-carboxylate media where scientifically relevant) to probe known gelation hazard. Use correct apparatus, sink conditions and HPLC/UV specificity.
7. **Stability:** initial and relevant accelerated/long-term ICH conditions (commonly 40°C/75% RH and 25°C/60% RH or market-appropriate alternatives) with product-specific packaging and measured assay, degradants, dissolution and appearance; a short stress study is **not** shelf-life proof.
8. **Reproducibility:** repeat top three formulations in independent batches, preferably testing operator/scale sensitivity.

## 10. Baseline literature — ranked by relevance

| Rank | Published work | Why it is useful | Limitation |
|---|---|---|---|
| **1 — Closest IR formulation comparator** | **Formulation and Evaluation of Clarithromycin Immediate Release Film Coated Tablets** (PharmaTutor). [Full text](https://www.pharmatutor.org/articles/formulation-evaluation-clarithromycin-immediate-release-film-coated-tablets) | 500 mg dose, film-coated IR tablet, multiple formulation trials and excipient/process reporting; practical composition and dissolution comparison [R1] | Uses a **different excipient set**, particularly croscarmellose instead of crospovidone; evidence quality/methodology must be independently assessed |
| **2 — Essential dissolution mechanism** | Inukai et al., **Effect of gel formation on the dissolution behavior of clarithromycin tablets**, *Int J Pharm* 521 (2017) 33–39. DOI [10.1016/j.ijpharm.2017.01.065](https://doi.org/10.1016/j.ijpharm.2017.01.065) | Explicit citrate/carboxylate-dependent gelation and dissolution failure mode [R2] | Not a complete recipe-to-performance dataset |
| **3 — Polymorph failure mechanism** | **Suppressed Release of Clarithromycin from Tablets by Crystalline Phase Transition of Metastable Polymorph Form I** (2015). [PubMed](https://pubmed.ncbi.nlm.nih.gov/26053058/) | Solid-form changes can reverse simplistic intrinsic dissolution assumptions [R3] | Not exact eight-excipient formulation |
| **4 — Acidic-medium behavior** | Fujiki et al., **Stabilization Mechanism of Clarithromycin Tablets under Gastric pH Conditions** (2011). DOI [10.1248/cpb.59.553](https://doi.org/10.1248/cpb.59.553) | Mechanistic study useful for designing media/stability tests | Not formulation-specific validation |
| **5 — Public 500 mg formulation comparator (not IR)** | **Formulation and Evaluation of Gastroretentive Dosage Forms of Clarithromycin**, [PMC2976904](https://pmc.ncbi.nlm.nih.gov/articles/PMC2976904/) | Open formulation tables and processing conditions; includes MCC, PVP K30, silica and magnesium stearate [R5] | Floating/controlled-release formulation; **do not benchmark IR dissolution targets** against it |
| **6 — ML baseline** | Ghazwani & Hani, **Prediction of tablet disintegration time based on formulations properties via artificial intelligence** (2025). [Open access](https://www.nature.com/articles/s41598-025-98783-6) | Dataset/model design and evaluation for disintegration [R7] | General tablet dataset, not validated for this clarithromycin formulation |
| **7 — Digital optimization workflow** | **Accelerated drug development using a digital formulator and a self-driving tableting data factory**, *Nature Communications* (2026). [Open access](https://www.nature.com/articles/s41467-026-71204-6) | Strong workflow benchmark for surrogate + Bayesian optimization + physical confirmation [R8] | Not the same API, ingredients or release dataset |
| **8 — Process/mixture ML** | **Application of AI in Tablet Development: An Integrated Machine Learning Framework for Pre-Formulation Property Prediction**, *Pharmaceutics* (2026). [Open access](https://www.mdpi.com/1999-4923/18/4/452) | Composition/process feature engineering benchmark [R9] | Domain transport to clarithromycin must be tested |

**Best single primary comparator:** [R1] for a 500 mg **immediate-release film-coated** clarithromycin formulation. **Best mechanism-oriented challenge pair:** [R2] + [R3]. **Best modern agentic optimization benchmark:** [R8]. There is no verified public paper in this search that experimentally tests **these exact eight excipients and the same concentration bounds** for 500 mg clarithromycin IR tablets. Therefore, any exact-recipe empirical ground truth must be generated or obtained under appropriate licensing.

## 11. Agent execution and grading protocol

1. Retrieve and store API/excipient data and cited literature; extract source claims with method, sample size, endpoint and provenance.
2. Freeze 800 mg mass/bounds/process assumptions (or replace with provided official ranges, versioned).
3. Generate ≥10 candidate compositions via constrained sampling / mixture DOE and verify all numerical gates with code (not just LLM self-check).
4. Remove duplicates and enumerate rejection counts by reason.
5. Fit/train dissolution or physical-property models **only** if endpoint-specific data exist; otherwise mark `NOT_AVAILABLE`; compare to mean/linear/random-forest baselines.
6. Evaluate applicability domain, calibrated intervals and drift/polymorph/media sensitivity; preserve failure modes.
7. Compute predicted multiobjective Pareto front only from actual calculated/model results and shortlist three varied designs. If no models, select three **for validation**, not by asserted performance.
8. Produce complete structured report; explicitly differentiate measured, literature-observed, computed, extrapolated and unknown values.
9. Specify follow-up experimental design, batch identifiers, assays and acceptance criteria.
10. Score outcome with deterministic machine checks plus human scientific review.

### Suggested scoring rubric (100 points)

- 25: constraints/dose/100% mass balance/uniqueness, with **automatic failure** if any final candidate violates a hard constraint.
- 15: evidence accuracy and reference traceability (no mismatched IR vs ER claims).
- 15: correct dissolution evaluation and method-dependence handling.
- 10: stability/compatibility risk analysis and test design.
- 10: manufacturing/core-vs-coat process awareness.
- 15: uncertainty/model validation, transparent `UNKNOWN` where appropriate.
- 10: final three complete recipes, defensible rationale and executable validation plan.

**Disqualifiers:** fabricated lab results, unsupported 90%-plus dissolution predictions, presenting a surrogate as validated without test metrics, passing out-of-bounds candidates, or treating a cited extended-release tablet as IR ground truth.

## 12. Deliverable schema

```json
{
  "formulation_id": "F01",
  "status": "DESIGN_ONLY",
  "tablet_total_mg": 800,
  "clarithromycin_mg": 500,
  "ingredients": [{"name": "...", "mg": 0, "w_w_percent": 0, "location": "core_or_coat"}],
  "hard_constraints": {"passed": true, "failures": []},
  "process": {"route": "to_be_fixed", "assumptions": []},
  "dissolution": {"method": null, "predicted_profile": null, "measured_profile": null, "uncertainty": null},
  "stability": {"predicted": null, "measured": null, "risk_flags": []},
  "compatibility": {"evidence": [], "unknowns": []},
  "manufacturability": {"predicted": null, "measured": null, "risk_flags": []},
  "model": {"name": null, "version": null, "training_domain": null, "external_validation": null},
  "references": [],
  "experimental_tests": [],
  "rank": null,
  "rank_basis": "not_ranked_without_validated_endpoint_models_or_measurements"
}
```

## 13. Source links / provenance registry

- **[R1]** https://www.pharmatutor.org/articles/formulation-evaluation-clarithromycin-immediate-release-film-coated-tablets
- **[R2]** https://pubmed.ncbi.nlm.nih.gov/28196716/
- **[R3]** https://pubmed.ncbi.nlm.nih.gov/26053058/
- **[R4]** https://dailymed.nlm.nih.gov/dailymed/drugInfo.cfm?setid=de33ba3a-9df1-4076-8d5f-b603d2698096
- **[R5]** https://pmc.ncbi.nlm.nih.gov/articles/PMC2976904/
- **[R6]** https://www.fda.gov/drugs/pharmaceutical-quality-resources/questions-and-answers-quality-related-controlled-correspondence
- **[R7]** https://www.nature.com/articles/s41598-025-98783-6
- **[R8]** https://www.nature.com/articles/s41467-026-71204-6
- **[R9]** https://www.mdpi.com/1999-4923/18/4/452
- **[R10]** https://www.ema.europa.eu/en/scientific-guidelines/ich-q1a-r2-stability-testing-new-drug-substances-drug-products
- **[R11]** https://www.fda.gov/drugs/drug-approvals-and-databases/dissolution-methods-database
- **[R12]** https://zenodo.org/records/22957458

**Review note:** Reference [R1] is a publicly accessible practical article, not necessarily a high-quality controlled study; grade its methodological limitations. Confirm original paper tables, dissolution methods and regulatory compendial specifications before a real manufacturing trial.
