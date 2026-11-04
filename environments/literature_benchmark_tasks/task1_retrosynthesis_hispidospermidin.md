# Task 1 — Retrosynthesis vs. Literature: 14-Step "Inside-Out" Total Synthesis of Hispidospermidin

**Environment:** `task1_retrosynthesis_hispidospermidin`
**Tool under test:** Retrosynthesis planner
**Benchmark class:** Route proposal vs. recently published total synthesis

---

## 1. Paper Under Comparison

| Field | Value |
|---|---|
| Title | An "Inside-Out" Strategy Enables a 14-Step Total Synthesis of Hispidospermidin |
| Authors | Charis Amber, T. Nakamura, M. Amoako, N. Settineri, … Richmond Sarpong (Sarpong Group, UC Berkeley) |
| Journal | *JACS Au* **2026**, *6*(1), 600–606 |
| DOI | 10.1021/jacsau.5c01567 |
| PMID | 41614197 |
| Published | 2026-01-06 (open access) |
| Links | [ACS article](https://pubs.acs.org/jaaucr/article/6/1/600/5079634/An-Inside-Out-Strategy-Enables-a-14-Step-Total), [PubMed](https://pubmed.ncbi.nlm.nih.gov/41614197) |

## 2. Why This Paper

- Hispidospermidin is a structurally complex polycyclic sesquiterpenoid alkaloid with **four previous total syntheses** (Danishefsky; Overman; Sorensen; and one earlier route — confirm exact set from the introduction). This gives an unusually rich comparison set: 5 independent human strategies.
- The new route is the **shortest to date: 14 steps, protecting-group-free**, built on an "inside-out" logic — constructing the central polycyclic core first, then elaborating outward, deliberately avoiding complexity-building moves that only incrementally advance the target.
- Route-level metrics (step count, overall yield, protecting-group usage) are explicitly discussed in the paper, which is exactly what a retrosynthesis benchmark needs to score against.

## 3. Ground Truth from the Paper

> ⚠️ Publisher full text was not accessible from the benchmark-authoring machine. Values below were extracted from abstracts and indexing summaries. **Confirm all values and copy per-step yields into `ground_truth/route.yaml` from the paper + SI before running the benchmark.**

| Route | Steps | Overall yield (approx.) | Notes |
|---|---|---|---|
| Danishefsky | longer (confirm) | ≈ 0.91% | confirm |
| Overman | longer (confirm) | ≈ 2.81% | enantioselective (confirm) |
| Sorensen | longer (confirm) | ≈ 0.32% | confirm |
| 4th prior route | confirm | confirm | confirm |
| **This paper ("inside-out")** | **14** | ~0.3–0.9% band (read exact value from paper) | protecting-group-free; core-first strategy |

Key strategic content to extract from full text into ground truth:
- Retrosynthetic disconnection map (Fig. 1/2 of paper) and the order of ring constructions.
- The key complexity-generating step(s) that build the core (identify name/reaction class).
- Per-step yields for the 14 steps (from SI) → exact overall yield.

## 4. Objective of the Task

The agent scientist, using only the **retrosynthesis tool** (literature/publisher data **after 2025-12-31 must be masked** from the tool's corpus to avoid leakage), must:

1. Take hispidospermidin as input (SMILES/InChI pulled from the paper SI or PubChem; store in `input/target.smi`).
2. Generate the **top 10 ranked routes** with full disconnection trees, step counts, longest linear sequence (LLS), predicted per-step and overall yields, and starting-material availability flags.
3. Write a short strategy annotation for each route (which bond disconnections define the strategy; core-first vs. periphery-first logic; protecting-group count).

**Exclusions:** the agent must not be given the paper, DOI, or any of the prior-route references.

## 5. Environment Setup

```
sci_paper/
└── env/task1_retro/
    ├── input/target.smi              # hispidospermidin structure
    ├── ground_truth/
    │   ├── route.yaml                # 14-step route, per-step conditions + yields (fill from paper+SI)
    │   ├── prior_routes.yaml         # Danishefsky/Overman/Sorensen/etc. metrics
    │   └── strategy_notes.md         # "inside-out" disconnection map description
    ├── runs/                         # tool outputs (top-K routes), one JSON per run
    └── scores/                       # scored comparisons (see §6)
```

Tool interface (adapt to the actual planner API):

```
retro_plan --target input/target.smi --topk 10 \
           --corpus-cutoff 2025-12-31 \
           --out runs/run_<timestamp>.json
```

## 6. Expected Results & Scoring

| # | Metric | Expected / pass threshold |
|---|---|---|
| 1 | Step count of the tool's best route | ≤ 20 steps (paper: 14; human prior routes all longer) |
| 2 | Strategy match | ≥ 1 of top-10 routes reproduces a published strategy class (inside-out core-first **or** one of the 3 prior strategies), judged by shared key disconnections |
| 3 | Route-level overlap | Jaccard overlap of key disconnection set vs. paper route ≥ 0.3 for the best-matching route |
| 4 | Yield estimate | Predicted overall yield of best route within 3× of the paper's reported overall yield |
| 5 | Protecting groups | Tool routes should use ≤ 2 protecting groups on the best route (paper uses 0) |
| 6 | Chemical validity | 100% of proposed steps pass the `retro_check` chemistry-validation skill (no impossible disconnections) |

**What "good" looks like:** the planner proposes a convergent, sub-20-step route whose strategic disconnection set overlaps at least one published human strategy — demonstrating it recovers expert-level strategic logic, not just any chemically valid route.

**Expected failure modes to log:** periphery-first linear routes (>25 steps), heavy protecting-group reliance, or high predicted yields (>20% overall) that misjudge the strain/selectivity issues of the core-forming step.

## 7. Sources

- [ACS JACS Au article page](https://pubs.acs.org/jaaucr/article/6/1/600/5079634/An-Inside-Out-Strategy-Enables-a-14-Step-Total)
- [PubMed 41614197](https://pubmed.ncbi.nlm.nih.gov/41614197)
- [Sarpong Group publications](https://sarponggroup.com/publications)
- [JoVE visualization entry (confirms target name)](https://visualize.jove.com/41614197-an-inside-out-strategy-enables-a-14-step-total-synthesis-of-hispidospermidin)
