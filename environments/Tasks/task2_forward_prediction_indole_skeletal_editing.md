# Task 2 — Forward Reaction Prediction vs. Literature: Precision Indole Skeletal Editing (Single-Carbon Editing of Tryptamines)

**Environment:** `task2_forward_indole_skeletal_editing`
**Tool under test:** Forward reaction prediction
**Benchmark class:** Product/outcome prediction on a brand-new (2026) reaction discovery

---

## 1. Paper Under Comparison

| Field | Value |
|---|---|
| Title | Precision indole skeletal editing for single-carbon replacement/deletion *(verify exact title from PubMed record)* |
| Authors | L. Zhang et al. (Chinese team; confirm full author list from paper) |
| Journal | *Science* — published online **2026-04-30** |
| DOI | 10.1126/science.aec3587 |
| PMID | 42060754 (already ~20 citations) |
| Links | [Science](https://www.science.org/doi/10.1126/science.aec3587), [PubMed](https://pubmed.ncbi.nlm.nih.gov/42060754), [NSFC news item](https://www.nsfc.gov.cn/english/site_1/news/A2/2026/07-07/550.html) |

## 2. Why This Paper

- Skeletal editing (deleting/replacing a single atom in an intact ring system) is one of the hardest possible tests for a forward-prediction tool: the correct product is **structurally non-obvious** and the transformation had essentially no precedent before 2023–2025.
- The reaction is **intramolecular editing of tryptamine derivatives**, driven by a photoreaction of a pendant amide — a mechanistically distinctive pathway that a tool trained on classical indole chemistry (C2/C3 functionalization) will systematically mispredict.
- The paper includes an application to **quebrachamine** synthesis, where the editing step collapses a longer classical sequence (best prior route: 9 steps, 17.8% overall) — giving a second, route-level comparison axis.
- Very recent (April 2026) → near-zero chance of leakage into training data.

## 3. Ground Truth from the Paper



Verified at abstract/indexing level:
- Transformation: **single-carbon skeletal editing of indoles in tryptamine derivatives**, enabled by **photoreaction of a pendant amide** (photochemical activation; intramolecular).
- Application: **shortened synthesis of quebrachamine** (prior best route: 9 steps, 17.8% overall yield).

To extract from full text into `ground_truth/reactions.yaml`:
1. Model substrate (tryptamine-derived amide) structures → SMILES.
2. Exact product structure(s) of the editing event (which carbon is deleted/replaced; what the indole becomes).
3. Conditions: light source/wavelength, sensitizer or catalyst if any, solvent, temperature, time.
4. Yields: model reaction yield + substrate scope range (min/median/max) + quebrachamine sequence yields.
5. Competing outcomes reported (unreacted SM, side products) — these become the tool's "distractor" answers.

## 4. Objective of the Task

The agent scientist, using only the **forward reaction prediction tool** (no access to the paper), must:

1. For each of N substrates (start with the model substrate; scale to 5–10 scope entries from SI):
   - Predict the **major product structure** (top-3 ranked, with scores).
   - Predict the **reaction class** label.
   - Flag **confidence/precedent level** (has the tool seen anything like this?).
2. For the quebrachamine intermediate: predict whether the tool identifies the skeletal-editing disconnection/product or defaults to classical indole reactivity.
3. (Stretch) Predict a plausible condition class (photochemical vs. thermal/metal-catalyzed) for the model reaction.

**Input format:** reactant SMILES (+ reagent field left deliberately generic/empty to test product prediction, not condition recall).

## 5. Environment Setup

```
sci_paper/
└── env/task2_forward/
    ├── input/substrates.smi          # tryptamine-derived substrates (fill from SI)
    ├── ground_truth/
    │   ├── reactions.yaml            # true products, conditions, yields (fill from paper+SI)
    │   └── distractors.md            # reported side products / competing outcomes
    ├── runs/                         # tool predictions per substrate
    └── scores/
```

Tool interface (adapt):

```
forward_predict --substrate input/substrates.smi \
                --topk 3 \
                --out runs/pred_<substrate_id>.json
```

## 6. Expected Results & Scoring

| # | Metric | Expected / pass threshold |
|---|---|---|
| 1 | Top-1 exact product match (model substrate) | Stretch goal: correct. Baseline expectation: **miss** — log the failure explicitly |
| 2 | Top-3 contains exact product | Strong result if achieved; indicates the tool explores low-precedent chemistry in its beam |
| 3 | Reaction-class sanity | Tool should NOT predict mundane C3-functionalization/addition products with high confidence; overconfident wrong answers are the key failure signal to quantify |
| 4 | Precedent flagging | Tool should report low precedent / high novelty for this transformation (calibration test) |
| 5 | Scope trend | On the filled substrate set: rank correlation (Spearman ≥ 0.4) between predicted scores and experimental yields |

**What we expect honestly:** most current forward-prediction tools will fail top-1 on a 2026 skeletal-editing reaction — that is the point of the benchmark. The valuable outputs are (a) the *calibrated* failure (low confidence + novelty flag) vs. (b) *confident* misprediction of classical indole reactivity. Track both.

**Route-level bonus metric:** after revealing the answer, check whether the tool can validate the editing step as proposed (product + rough conditions) when run in "verify" mode — relevant to Task 5 integration.

## 7. Sources

- [Science DOI page](https://www.science.org/doi/10.1126/science.aec3587)
- [PubMed 42060754](https://pubmed.ncbi.nlm.nih.gov/42060754)
- [NSFC news coverage (2026-07-07)](https://www.nsfc.gov.cn/english/site_1/news/A2/2026/07-07/550.html)
- [ScienceOpen record](https://www.scienceopen.com/document?vid=5465447d-3c51-4471-87b3-fc5ac2dc141e)
- Related context: [C&EN skeletal-editing feature (2025)](https://cen.acs.org/synthesis/Skeletal-editing-cutpaste-chemistry/103/web/2025/07)
