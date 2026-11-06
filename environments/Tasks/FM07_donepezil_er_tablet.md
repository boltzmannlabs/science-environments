# FM07 — Donepezil Extended-Release Tablet: Release-Profile Optimization

**Environment:** `FM07_donepezil_er` · **Series:** Pharmaceutical formulation A — composition & dissolution improvement
**Tools:** formulation-optimisation environment (agent scientist + DoE) · release-profile modeling

---

## 1. Paper Under Comparison

| Field | Value |
|---|---|
| Curation entry | Donepezil extended-release tablet development (2025) |
| Original paper objective | Develop an extended-release formulation using DoE and physiologically based modeling. |
| Full citation | **To fill:** authors, journal, volume/pages, DOI (retrieve via "donepezil extended release design of experiments PBPK 2025") |

## 2. What We Want to Work On (Objective)

From this paper we work on **extended-release profile optimization** — the agent scientist must:

1. Optimize **polymer concentration (release-controlling matrix), matrix composition, and compression force** against the **release profile** (multi-timepoint dissolution, f2 similarity to target profile) plus tablet quality attributes.
2. Model the release kinetics: fit/choose mechanism (diffusion vs. erosion dominated) and predict full profiles, not just single time points.
3. **Dose-dumping risk**: predict release under alcohol-dose-dumping-style stress conditions (hydro-alcoholic medium) for the proposed optimum; verify the margin.
4. Connect dissolution to biology: given the paper's PBPK framing, map the achieved in-vitro profile to the in-vivo target (e.g., Cmax/Tmax expectations) at reasoning level.

## 3. Expected Outputs

- A **controlled release profile** matching the target (f2 ≥ 50 vs. target profile or paper's optimum).
- **No dose dumping**: predicted release in stress medium within accepted bounds.
- Release-kinetic model with mechanistic parameters (n exponent / erosion fraction).
- Optimized formula + process with predicted quality attributes.

## 4. Ground Truth to Capture

- DoE tables: factors × multi-timepoint dissolution + quality attributes.
- Target release profile and paper's optimized formulation.
- PBPK modeling assumptions and any IVIVC/level-A correlation claims.
- Dose-dumping test results if reported.

## 5. Environment Setup

```
sci_paper/env/FM07/
├── input/factor_space.yaml + blinded_matrix.csv + target_profile.csv
├── ground_truth/full_doe.csv + optimum.yaml   # fill from paper
├── runs/
└── scores/
```

## 6. Scoring

| # | Metric | Pass threshold |
|---|---|---|
| 1 | Profile prediction (blind) | mean deviation ≤ 10 pp at each timepoint |
| 2 | f2 vs. target | ≥ 50 at proposed optimum |
| 3 | Kinetic model | mechanism call consistent with paper |
| 4 | Dose-dumping margin | stress-release prediction conservative (no unsafe optimum proposed) |
| 5 | Experiment efficiency | ≤ paper's run count via oracle protocol |

## 7. Notes

- The dose-dumping metric is a **safety gate**: an optimum that predicts well but passes an unsafe stress profile fails the task outright.
