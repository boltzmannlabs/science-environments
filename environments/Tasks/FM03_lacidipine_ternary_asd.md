# FM03 — Lacidipine Ternary Solid Dispersions: Supersaturation & Precipitation Control

**Environment:** `FM03_lacidipine_ternary_asd` · **Series:** Pharmaceutical formulation A — composition & dissolution improvement
**Tools:** formulation-optimisation environment (agent scientist + DoE) · dissolution/stability environment

---

## 1. Paper Under Comparison

| Field | Value |
|---|---|
| Curation entry | Ternary solid dispersions of lacidipine (2024) |
| Original paper objective | Improve dissolution and maintain supersaturation using ternary solid dispersions. |
| Full citation | **To fill:** authors, journal, volume/pages, DOI (retrieve via "lacidipine ternary solid dispersion supersaturation 2024") |

## 2. What We Want to Work On (Objective)

From this paper we work on **supersaturation maintenance and precipitation inhibition** — the agent scientist must:

1. Optimize **polymer combinations** (binary vs. ternary: polymer identity + ratio) and **drug loading** against: apparent solubility, dissolution profile, **supersaturation extent/duration**, and precipitation onset.
2. Predict the blinded matrix responses, including the kinetic ones (para-solubility at fixed time points, precipitation index).
3. Identify the **polymer mechanism axes** (crystallization inhibition vs. solubilization) and recommend the pairing rationale — which polymer classes should synergize and why.
4. Define a **drug-loading ceiling**: maximum load retaining amorphous stability + supersaturation performance.

## 3. Expected Outputs

- Improved **apparent solubility and dissolution** vs. binary/baseline (Δ ≥ +10 pp or match paper optimum).
- **Precipitation resistance**: predicted supersaturation maintained over the paper's test duration at the optimum.
- Polymer-selection rationale grounded in interactions (H-bond donor/acceptor complementarity to lacidipine).
- Drug-loading ceiling with stability justification.

## 4. Ground Truth to Capture

- Polymer screen (identities, ratios) × responses (solubility, dissolution, supersaturation/precipitation curves).
- Solid-state characterization outcomes (XRD/DSC amorphous confirmation).
- Stability data if reported.

## 5. Environment Setup

```
sci_paper/env/FM03/
├── input/factor_space.yaml + blinded_matrix.csv
├── ground_truth/full_doe.csv + optimum.yaml   # fill from paper
├── runs/
└── scores/
```

## 6. Scoring

| # | Metric | Pass threshold |
|---|---|---|
| 1 | Best polymer pair in top-3 predicted | yes/no |
| 2 | Response prediction MAE (blind) | solubility ≤ 15%; dissolution ≤ 10 pp |
| 3 | Supersaturation trend | correct ranking of formulations by precipitation resistance |
| 4 | Mechanism rationale | consistent with paper's discussion (qualitative) |
| 5 | Drug-loading ceiling | within ± 10% of paper's supported maximum |

## 7. Notes

- Instantiates **FM-P03 (dissolution improvement)** with a kinetic-response dimension; the precipitation-inhibition scoring axis is unique in this series.
