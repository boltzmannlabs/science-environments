# SC02 — Microwave-Assisted Catalytic Amidation of Aryl Amines and Aryl Acids: Yield & Protocol Generalization

**Environment:** `SC02_mw_amidation` · **Series:** Synthetic chemistry A — reaction yield & condition improvement
**Tools:** condition recommendation (primary) · forward reaction · impurity prediction

---

## 1. Paper Under Comparison

| Field | Value |
|---|---|
| Curation entry | Microwave-assisted catalytic amidation of aryl amines and aryl acids (2025) |
| Original paper objective | Develop an effective catalytic amidation protocol using high-throughput experimental (HTE) screening. |
| Full citation | **To fill:** authors, journal, volume/pages, DOI (retrieve via "microwave catalytic amidation aryl amine carboxylic acid 2025 high-throughput") |

## 2. What We Want to Work On (Objective)

From this paper we work on **amide-bond-formation yield improvement and protocol generalization** — the agent scientist must:

1. Recommend a ranked condition grid for direct catalytic amidation: **catalyst, activator/additive, solvent, microwave temperature, time**.
2. Predict yield across a substrate matrix spanning **sterically hindered** (2,6-substituted anilines, ortho-substituted acids) and **electronically diverse** (electron-poor amines vs. electron-rich acids) pairings, blind to the paper's results.
3. Check **catalyst compatibility** — flag condition sets where the catalyst or additive conflicts with sensitive functional groups (free phenols, nitro, halides) using forward + impurity tools.
4. Solve the **solvent-effect axis**: recommend the best 3 solvents and predict ranking.
5. Propose one **generalized protocol** (single condition set) with predicted yield floor across the substrate matrix.

## 3. Expected Outputs

- A generalized amidation protocol with **improved yield** vs. paper baseline (Δ ≥ +10 pp on the worst-performing substrate class) and **reduced reaction time** (≤ paper's µw time).
- Predicted yield matrix (substrates × top conditions) with accuracy metrics vs. paper.
- Compatibility/exclusion map: which substrate classes need protocol deviations.

## 4. Ground Truth to Capture

- HTE screening matrix: catalyst × solvent × T × time → conversion/yield.
- Substrate scope table (incl. hindered pairs) with isolated yields.
- Reported side products (imides, ureas, anhydrides, decarboxylation) → impurity distractors.

## 5. Environment Setup

```
sci_paper/env/SC02/
├── input/substrates.smi        # amine × acid pairs from paper
├── ground_truth/hte_matrix.csv # screening + scope yields (fill from paper)
├── runs/
└── scores/
```

## 6. Scoring

| # | Metric | Pass threshold |
|---|---|---|
| 1 | Paper optimum in tool's top-5 conditions | yes/no |
| 2 | Yield MAE on substrate matrix | ≤ 15 pp |
| 3 | Hindered-substrate prediction | correct identification of lowest-yield class |
| 4 | Side-product flags | ≥ 1 of the paper's reported side products predicted |
| 5 | Generalized protocol | predicted pass on ≥ 70% of matrix |

## 7. Notes

- Amide bond formation is the highest-volume reaction class in pharma — good headline benchmark for condition tools.
- Watch for the tool defaulting to coupling reagents (EDC/HATU) when the paper's axis is *catalytic* activation — mechanism-class mismatch is a scoring failure (see Task 3 of the literature suite).
