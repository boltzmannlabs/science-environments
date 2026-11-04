# Task 5 — Integrated End-to-End Benchmark: Total Synthesis Planning for Gregatin A (All Four Tools Chained)

**Environment:** `task5_integrated_gregatin_a`
**Tools under test:** Retrosynthesis + Forward reaction + Condition recommendation + Impurity prediction (full agent-scientist pipeline)
**Benchmark class:** Multi-tool route design & validation vs. the complete published route record for one target

---

## 1. Paper Under Comparison

| Field | Value |
|---|---|
| Title | Evolution of the Total Synthesis of Gregatin A and Related Natural Products |
| Authors | Y. Bai et al. |
| Journal | *Chemistry – A European Journal* **2026** (online January 2026) |
| DOI | 10.1002/chem.202503396 |
| PMID | 41543150 |
| Links | [Chemistry Europe](https://chemistry-europe.onlinelibrary.wiley.com/doi/10.1002/chem.202503396), [PubMed](https://pubmed.ncbi.nlm.nih.gov/41543150) |

**Supporting primary literature referenced by the review (the route ground truth):**

| Route | Reference | Key features |
|---|---|---|
| Brückner group (2012) | Burghart, Stoll & Brückner, *Angew. Chem.* (PMID-linked record; confirm) | Total syntheses of gregatins A–D + aspertetronin A; **structure revisions** of gregatins and related compounds |
| Kusakabe et al. (2013) | [PMID 24066736](https://pubmed.ncbi.nlm.nih.gov/24066736) | Total syntheses of (+)-gregatin B and E; **Pd-catalyzed cyclization–methoxycarbonylation** as the key step |
| Recent gram-scale route | described in the 2026 review | **6 steps, gram scale**, featuring an **intermolecular 1,3-dipolar (nitrone) cycloaddition + N–O bond cleavage** |

## 2. Why This Paper

- Gregatin A is a **chain-fused polyketide natural product** — small enough that every step matters, hard enough (dense stereocenters, polyene/enone motifs) that route quality differentiates.
- The target has an unusually well-documented **evolutionary record**: first syntheses with structure revisions (2012) → Pd-cyclization routes (2013) → a 6-step gram-scale nitrone-cycloaddition route (recent). The benchmark can therefore score a generated route against *a distribution of human strategies*, not a single route.
- It exercises **all four tools in sequence** on one problem — the capstone of this benchmark suite: plan (retro) → validate (forward) → resource (conditions) → de-risk (impurities).

## 3. Ground Truth from the Paper

> ⚠️ Transcribe from the review (and the primary papers it covers) into `ground_truth/` before running. Verified so far at abstract/indexing level:
- Review compares strategies and their evolution toward gregatin A and relatives.
- Recent best route: **6 steps, gram scale, intermolecular nitrone 1,3-dipolar cycloaddition followed by N–O bond cleavage**.
- 2012 work included **structure revision** — note: the *structure assignment history* itself is a subtle trap for structure retrieval (make sure `input/target.smi` carries the **revised, correct structure** of gregatin A).

To extract:
- Per-route: step count, LLS, overall yield, scale, key disconnections (→ `ground_truth/routes.yaml`).
- Per-step conditions and yields of the 6-step route (→ `ground_truth/route6_steps.yaml`).

## 4. Objective of the Task

The agent scientist runs the **full pipeline**, with all literature post-2025 masked from tool corpora:

1. **Retrosynthesis:** generate top-5 routes to gregatin A; select the best route by a declared utility function (steps × predicted yield × starting-material availability).
2. **Forward validation:** for every step of the selected route, run forward prediction to confirm the expected product (catching retro steps that don't survive forward scrutiny). Steps failing forward validation must be repaired or replaced.
3. **Condition recommendation:** for the 3 highest-risk steps of the final route, produce ranked condition sets with predicted yields.
4. **Impurity prediction:** for the final 2 steps, predict the top-5 impurities and the most scale-sensitive one.
5. **Deliverable:** a complete "proposed synthesis dossier" (route map, per-step products/conditions/predicted yields, impurity risk register) + an honest uncertainty annotation per step.

## 5. Environment Setup

```
sci_paper/
└── env/task5_integrated/
    ├── input/target.smi                # gregatin A (REVISED structure)
    ├── ground_truth/
    │   ├── routes.yaml                 # all published routes + metrics (from review + primaries)
    │   ├── route6_steps.yaml           # per-step conditions/yields of the 6-step route
    │   └── strategy_notes.md
    ├── runs/
    │   ├── retro/  forward/  condition/  impurity/
    │   └── dossier/                   # final assembled dossier per run
    └── scores/
```

Pipeline interface (adapt per tool):

```
pipeline_run --target input/target.smi --corpus-cutoff 2025-12-31 \
             --topk_routes 5 --validate forward --risk_steps 3 --out runs/
```

## 6. Expected Results & Scoring

| # | Metric | Expected / pass threshold |
|---|---|---|
| 1 | Route quality | Best pipeline route ≤ 10 steps (literature best: 6; first-generation literature routes were longer) |
| 2 | Strategy overlap | Selected route shares ≥ 1 key disconnection with a published route (e.g., convergent fragment coupling or cycloaddition-based assembly) |
| 3 | Forward consistency | 100% of final-route steps pass forward validation (self-consistency between planner and predictor) |
| 4 | Condition hit rate | For ≥ 1 of the 3 risk steps, recommended conditions are compatible with the corresponding literature step's condition class (within tolerance: same reagent family, ΔT ≤ 20 °C) |
| 5 | Yield realism | Sum/chain of predicted step yields gives overall estimate within 3× of a comparable literature route's overall yield |
| 6 | Impurity relevance | Predicted impurity register for the final steps contains ≥ 1 chemically plausible member of the families that polyene/enone + thio-/nitrogen-intermediate chemistry is known to produce (E/Z isomers, over-addition products, oxidation) — judged by `retro_check`-style chemistry audit |
| 7 | Dossier completeness | Uncertainty annotated per step; no fabricated precedents (every claimed literature step verifiable or marked "novel proposal") |

**Expected result profile:** this is the hardest task in the suite. A realistic "pass" is a coherent, self-consistent, chemistry-valid dossier at ≤ 10 steps whose risk analysis would survive a process-chemist read — not necessarily matching the 6-step nitrone route (a genuinely creative human solution).

## 7. Sources

- [Chemistry Europe review](https://chemistry-europe.onlinelibrary.wiley.com/doi/10.1002/chem.202503396)
- [PubMed 41543150](https://pubmed.ncbi.nlm.nih.gov/41543150)
- [Kusakabe 2013, PubMed 24066736](https://pubmed.ncbi.nlm.nih.gov/24066736)
- [Brückner 2012 gregatins A–D record](https://www.semanticscholar.org/paper/Total-Syntheses-of-the-Gregatins-A%E2%80%93D-and-A%3A-of-and-Burghart-Stoll-Br%C3%BCckner/76e45c4bc1cde8c2f849c5ab02112dc5ccf5fca2)
