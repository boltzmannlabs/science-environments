# SC04 — Organocatalytic Desymmetrization of Planar Chiral Paracyclophanes: Yield & Stereoselectivity

**Environment:** `SC04_paracyclophane_desym` · **Series:** Synthetic chemistry A — reaction yield & condition improvement
**Tools:** condition recommendation (catalyst ranking) · forward reaction (selectivity) · impurity prediction (competing pathways)

---

## 1. Paper Under Comparison

| Field | Value |
|---|---|
| Curation entry | Organocatalytic desymmetrization of planar chiral paracyclophanes (2024) |
| Original paper objective | Develop an enantioselective catalytic route to planar chiral compounds. |
| Full citation | **To fill:** authors, journal, volume/pages, DOI (retrieve via "organocatalytic desymmetrization planar chiral paracyclophane 2024") |

## 2. What We Want to Work On (Objective)

From this paper we work on **catalyst-dependent yield and stereoselectivity improvement** — the agent scientist must:

1. **Rank catalyst structures** (organocatalyst family from the paper: chiral acid/base or phase-transfer scaffold) by predicted yield **and** enantiomeric excess, using catalyst descriptors (steric map, H-bonding geometry, pKa).
2. Optimize the **oxidant and base** axes: predict how each combination shifts (a) conversion, (b) ee, (c) competing-reaction share.
3. Predict the **major product and enantiomer** for the model substrate (planar-chiral sense of induction) — the forward-selectivity test.
4. Predict **competing reactions** (over-oxidation, non-selective background desymmetrization, meso-pathway leakage) and which condition levers suppress each.

## 3. Expected Outputs

- A catalyst/oxidant/base condition set with **improved yield and ee** vs. the paper's optimized entry (Δ yield ≥ +5 pp and/or Δ ee ≥ +5 pp, or match if paper is already optimal).
- Catalyst-structure → selectivity relationship (predicted trend across ≥ 5 catalyst variants).
- Suppression plan for the dominant competing pathway, with predicted purity gain.

## 4. Ground Truth to Capture

- Catalyst screening table: catalyst → yield + ee.
- Oxidant/base optimization tables.
- Competing-pathway product structures and their levels.

## 5. Environment Setup

```
sci_paper/env/SC04/
├── input/substrate.smi + catalyst_space.yaml
├── ground_truth/catalyst_screen.csv    # catalyst → yield, ee (fill from paper)
├── runs/
└── scores/
```

## 6. Scoring

| # | Metric | Pass threshold |
|---|---|---|
| 1 | Paper's best catalyst in top-3 predicted | yes/no |
| 2 | ee prediction (direction + magnitude) | correct enantiomer sense; |Δee| ≤ 15 pp on ≥ 3 catalysts |
| 3 | Yield MAE across catalyst set | ≤ 15 pp |
| 4 | Competing pathway | dominant side reaction predicted + suppression lever identified |
| 5 | Selectivity logic | predicted structure–selectivity trend matches paper's SAR discussion (qualitative) |

## 7. Notes

- ee prediction is beyond most condition tools — if the tool cannot output ee, score yield axis only and log stereoselectivity as a capability gap (that gap is itself a benchmark result).
- This task is the pilot for the derived topic **Catalyst loading reduction / selectivity control** (`SC-C_derived_research_topics.md`).
