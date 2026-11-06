# SC09 — Pregabalin Continuous-Flow Synthesis: Time & Impurity Reduction

**Environment:** `SC09_pregabalin_flow` · **Series:** Synthetic chemistry B — API synthesis, process improvement & cost reduction
**Tools:** condition recommendation (flow-constrained) · impurity prediction · retrosynthesis

---

## 1. Paper Under Comparison

| Field | Value |
|---|---|
| Curation entry | Pregabalin synthesis using continuous flow (2024) |
| Original paper objective | Develop an efficient continuous-flow synthesis process with improved impurity control. |
| Full citation | **To fill:** authors, journal, volume/pages, DOI (retrieve via "pregabalin continuous flow synthesis 2024") |

## 2. What We Want to Work On (Objective)

From this paper we work on **reaction time and impurity reduction in API synthesis under flow** — the agent scientist must:

1. Given the pregabalin route's key step(s) (from `input/route.yaml`), optimize **flow rate/residence time, temperature, and reagent concentration** — predicting conversion and impurity at each design point, blind.
2. Predict the **impurity profile** of the flow process vs. the batch baseline: which impurities shrink (thermal/exposure control) and which could grow (mixing sensitivity, accumulation of reactive intermediates)?
3. Identify the **time-quality frontier**: minimum total processing time that keeps impurity ≤ target spec and isolated yield ≥ baseline.
4. Flag **safety-critical process risks** (exotherm management, hazardous reagent handling in flow) that motivate the flow switch.

## 3. Expected Outputs

- Reduced **processing time** vs. the paper's batch baseline (≥ 30% reduction target) while **maintaining isolated yield** (within −5 pp).
- **Controlled impurities**: predicted impurity register with the top impurity ≤ paper's final spec level.
- A flow process definition: parameter set + robustness margins.

## 4. Ground Truth to Capture

- Batch vs. flow comparison data (yield, time, impurity %).
- Flow optimization tables (residence time × T × concentration).
- Final optimized process + impurity results.

## 5. Environment Setup

```
sci_paper/env/SC09/
├── input/route.yaml + flow_space.yaml
├── ground_truth/batch_vs_flow.csv   # fill from paper
├── runs/
└── scores/
```

## 6. Scoring

| # | Metric | Pass threshold |
|---|---|---|
| 1 | Impurity trend prediction | flow vs. batch direction correct for ≥ 2 impurities |
| 2 | Yield prediction MAE | ≤ 12 pp |
| 3 | Top impurity structure | paper's main impurity in top-3 predicted |
| 4 | Time-quality frontier | proposed operating point meets time + impurity targets |
| 5 | Safety flags | exotherm/hazard rationale present |

## 7. Notes

- Instantiates problem statement **SC-P04 (impurity reduction)** with a flow twist; compare outcomes with SC06's flow benchmark.
