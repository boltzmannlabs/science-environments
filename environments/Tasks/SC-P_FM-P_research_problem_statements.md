# Research Problem Statements — SC-P & FM-P Series

**Status:** Recommended independent research problems developed from the SC01–SC12 / FM01–FM14 papers' limitations and findings — *not* reproductions of the original experiments.

Each statement is the generic problem; the paper task files are concrete instances. Use this file as the master mapping when reporting cross-instance results.

---

## Synthetic chemistry problems

### SC-P01 — Reaction condition optimization
- **Main scientific question:** Which combination of catalyst, solvent, base, and temperature produces the best reaction outcome?
- **Measurable outcome:** Isolated yield, conversion, selectivity.
- **Instances:** SC01, SC02, SC03, SC04, SC05, SC06 — primary instances in bold: **SC01**, **SC02**.
- **Success criterion across instances:** tool's top-5 conditions contain the paper optimum in ≥ 50% of instances; prediction MAE ≤ 15 pp aggregate.

### SC-P02 — Yield improvement
- **Main scientific question:** Why is the reaction producing a lower-than-expected yield, and which parameters can improve it?
- **Measurable outcome:** Yield improvement over baseline (Δ pp).
- **Instances:** **SC02**, SC04, SC05, SC06.
- **Success criterion:** a diagnosed cause (side reaction, equilibrium, mass transfer, kinetics) that the paper's data supports, plus a proposed change with predicted Δ ≥ +10 pp.

### SC-P03 — Cost-effective API synthesis
- **Main scientific question:** Can an existing API process be redesigned to reduce manufacturing cost?
- **Measurable outcome:** Cost per kg, step count, material consumption.
- **Instances:** **SC07**, SC11, (SC03 for the solvent-cost axis).
- **Success criterion:** redesigned route/condition set reduces predicted cost ≥ 30% or steps ≥ 1 with yield within 3× of paper's; cost model assumptions explicit.

### SC-P04 — Impurity reduction
- **Main scientific question:** Which reaction parameters are responsible for impurity formation?
- **Measurable outcome:** Impurity percentage and product purity.
- **Instances:** **SC09**, SC07, SC04 (+ SC-C4 module across hosts).
- **Success criterion:** dominant impurity identified with mechanistic driver; suppression proposal reduces predicted impurity to spec without > 10% yield loss.

### SC-P05 — Green synthetic chemistry
- **Main scientific question:** Can hazardous solvents or expensive catalysts be replaced without sacrificing performance?
- **Measurable outcome:** Yield, solvent E-factor, catalyst consumption.
- **Instances:** **SC03**, SC01 (loading axis), (+ SC-C2/SC-C3 modules).
- **Success criterion:** green/low-loading recommendation within −5 pp yield of optimum; E-factor and mol% catalyst reduced; no Class 1–2 solvents.

## Formulation problems

### FM-P01 — API–excipient compatibility
- **Main scientific question:** Which excipients are compatible with the selected API, and what interactions can occur?
- **Measurable outcome:** Compatibility, degradation, impurity profiles.
- **Instances:** **FM08**, FM09, FM14 (herbal extract axis).
- **Success criterion:** ≥ 70% of paper's incompatibilities flagged; no incompatible excipient in final recommendation.

### FM-P02 — Formulation composition optimization
- **Main scientific question:** Which excipient combination produces the desired product quality?
- **Measurable outcome:** Dissolution, hardness, friability, disintegration.
- **Instances:** **FM01**, **FM02**, FM04, FM05, FM06, FM14.
- **Success criterion:** multi-CQA optimum found within paper's design space; all CQAs predicted in spec.

### FM-P03 — Dissolution improvement
- **Main scientific question:** What formulation changes improve dissolution of poorly soluble APIs?
- **Measurable outcome:** Dissolution percentage and profile.
- **Instances:** **FM01**, FM03, FM07 (profile control), FM13 (dissolution protection).
- **Success criterion:** predicted dissolution ≥ +10 pp over baseline or target profile met (f2 ≥ 50) at proposed formulation.

### FM-P04 — Stability improvement
- **Main scientific question:** Which formulation and storage conditions minimize API degradation?
- **Measurable outcome:** Assay, impurity growth, degradation kinetics.
- **Instances:** **FM03** (amorphous stability), FM09 (aggregation/LLPS), FM08.
- **Success criterion:** stability ranking of formulations correct; proposed storage/packaging condition keeps predicted degradation within spec over shelf-life target.

### FM-P05 — Manufacturing process optimization
- **Main scientific question:** Which manufacturing parameters influence finished-product quality?
- **Measurable outcome:** Content uniformity, granule properties, tablet quality.
- **Instances:** **FM10**, **FM12**, FM11, FM13.
- **Success criterion:** significant process parameters identified (≥ 70% overlap with paper); robust operating space defined; predicted variance under noise acceptable.

---

## Reporting template (per problem statement)

```
problem_id: SC-P03
instance:   SC07_adagrasib_process
date/run:   <timestamp>
metrics:    cost_per_kg_delta: -38% | steps: -2 | yield_ratio: 0.92
verdict:    pass | partial | fail
notes:      <divergence from paper, caveats>
```

Aggregate each problem statement across its instances into a capability matrix (problem × instance → verdict) — this is the top-level deliverable of the whole SC/FM benchmark curation.
