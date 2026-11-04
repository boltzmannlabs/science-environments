# SC12 — Practical DoE for Synthetic Chemists: Systematic Optimization Benchmark

**Environment:** `SC12_doe_methodology` · **Series:** Synthetic chemistry B — API synthesis, process improvement & cost reduction
**Tools:** DoE environment (agent scientist) · condition recommendation (as hypothesis generator)

---

## 1. Paper Under Comparison

| Field | Value |
|---|---|
| Curation entry | Practical start-up guide for synthetic chemists to implement DoE (2025) |
| Original paper objective | Explain practical implementation of DoE in synthetic chemistry. |
| Full citation | **To fill:** authors, journal, volume/pages, DOI (retrieve via "practical guide design of experiments synthetic chemists 2025") |

## 2. What We Want to Work On (Objective)

From this paper we work on **systematic reaction optimization using DoE** — a methodology benchmark run on real screening data (from SC01–SC08 or the paper's own worked examples). The agent scientist must:

1. **Contrast strategies**: for one chosen dataset, execute (a) one-factor-at-a-time (OFAT), (b) fractional factorial screening, (c) response-surface optimization — as simulated experiment sequences, where each "experiment" costs one query against the ground-truth dataset.
2. **Identify important parameters** with the fewest experiments: declare the significant factors and interactions after each strategy and compare against the dataset's true effects.
3. **Establish optimized conditions** and quantify the total experimental budget each strategy needed to get there.
4. Produce a **practitioner-style report**: factor effects, interactions, design-space plot description, and recommended next experiments.

## 3. Expected Outputs

- **Important-parameter identification** matching the dataset's true significant factors (≥ 70% precision/recall).
- **Optimized conditions** equivalent to the full-data optimum, reached with **fewer experiments** (target: DoE strategy reaches optimum with ≤ 50% of the full-matrix run count; OFAT baseline documented for contrast).
- A quantitative **OFAT vs factorial vs RSM comparison** (experiments-to-optimum, risk of missing interactions).

## 4. Ground Truth to Capture

- The paper's worked DoE examples (factors, responses, matrices, conclusions) — or substitute datasets from SC01–SC08 tasks.
- Its practical rules of thumb (screening resolution, center points, replication) as reference for the agent's design choices.

## 5. Environment Setup

```
sci_paper/env/SC12/
├── input/dataset.yaml           # full ground-truth matrix (hidden from agent)
├── runner/oracle.py             # serves one "experiment" per query (row reveal)
├── ground_truth/analysis.md     # true effects + paper's methodology guidance (fill)
├── runs/                        # per-strategy experiment logs + conclusions
└── scores/
```

## 6. Scoring

| # | Metric | Pass threshold |
|---|---|---|
| 1 | Effect identification | ≥ 70% precision/recall vs true effects |
| 2 | Experiments-to-optimum (DoE) | ≤ 50% of full matrix |
| 3 | Interaction detection | ≥ 1 true interaction found; OFAT comparison shows its blind spot |
| 4 | Optimum quality | within 5 pp of full-data optimum response |
| 5 | Report quality | design choices justified per the paper's practical guidance |

## 7. Notes

- The oracle-query design makes this a **budgeted-information** benchmark — it scores experimental efficiency, not just prediction, and is reusable across every dataset in this curation (SC + FM).
- Serves as the shared engine for SC08, SC10 and the FM-series DoE tasks.
