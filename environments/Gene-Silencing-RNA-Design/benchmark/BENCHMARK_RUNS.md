# Benchmark Runs — published references, run configs, and iterative comparison

This file structures every benchmark the way runs are actually iterated:

```
1. PUBLISHED REFERENCE  — actual published metrics + values, with sources (or an explicit
                          "no published reference exists" — never fabricated)
2. RUN CONFIG           — the input config for the task (engine/gates/weights/scope), keyed Run-1, Run-2, ...
3. RESULTS TABLE        — Published | Run-1 | Δ | Run-2 | Δ vs published | Δ vs Run-1
                          (Run-2+ slots are future configs; the point is that a config change
                          must beat BOTH the published reference AND the prior run to count)
```

**Standing rule (the iteration contract):** a future Run-N is only claimable if (a) its config delta vs Run-(N−1) is stated in one line, (b) it is compared against the published reference and every prior run, (c) the freeze/version rules are respected, and (d) labels stay blind to selection.

## R1 — Efficacy predictor (RN.Ai-Predict)

**1. Published reference** *(values as published; protocols differ — never like-for-like)*

| Metric | Published value | Source |
|---|---|---|
| AUC (Mixset test, N-padded lower bound) | 0.808 | RN.Ai-predict repo/model registry (Roco-scientist; DOI 10.1101/2025.08.12.669916) |
| Spearman (Mixset test) | 0.596 | same |
| AUC (RNAiSpline, same cohort — cross-model context) | 0.818 | RNAiSpline registry validation |
| AUC (OligoFormer paper, Huesken→Mixset protocol) | 0.8163 / PCC 0.5879 | Bai et al., Bioinformatics 2024, PMID 39321261 |

**2. Run configs**

| Run | Config | Date |
|---|---|---|
| **Run-1a** (Mix replay) | frozen engine v1.0 gates; Mix-469 eligibility; no refit; fixed seeds | 2026-11-03 |
| **Run-1b** (Simone clean) | same engine; real 57-nt context from dataset transcripts; cutoff 0.7 | 2026-11-03 |

**3. Results**

| Metric | Published | Run-1a (Mix-469) | Δ | Run-1b (Simone-322, clean) | Run-2 (FUTURE) |
|---|---|---|---|---|---|
| AUC | 0.808 (registry) | **0.8195** | +0.012 | **0.7021** | slot: e.g. context-ablated config |
| Spearman | 0.596 (registry) | 0.6226 | +0.027 | 0.3930 | — |
| Reading | — | exposed cohort, descriptive | not like-for-like | **first clean independent number**; gap ≈ 0.12 AUC | must beat published AND both runs |

*No published RN.Ai number exists for Simone — Run-1b is the reference-setter for that cohort.*

## R2 — Generator (OligoFormer)

**1. Published reference**

| Metric | Published value | Source |
|---|---|---|
| AUC / PCC (Huesken→Mixset) | 0.8163 / 0.5879 | Bai et al. 2024 (PMID 39321261) |

**2. Run configs**

| Run | Config | Date |
|---|---|---|
| Run-1a | native inference mode (train-flag + no_grad, seed 42); Mix-469 | 2026-11-03 |
| Run-1b–e | same; HIF1A / HPSE / HK2 / MYC full-transcript pools; labels joined post-hoc | 2026-11-04/05 |

**3. Results**

| Cohort | Published | Run-1 | Δ / note |
|---|---|---|---|
| Mix-469 (exposed) | 0.8163 / 0.5879 | **0.8437 / 0.6670** | above paper; cohort/recipe differ — not claimed as superiority |
| HIF1A n=100 (clean) | none exists | **0.760 [0.615–0.877]** | reference-setter; top-10 recovery median 97.5th pct |
| HPSE n=106 | none | 0.584 [0.465–0.703] | CI includes 0.5 — weak target, published as-is |
| HK2 n=95 | none | 0.645 [0.498–0.783] | borderline |
| MYC n=7 | none | degenerate | percentile-only |
| **Cross-target finding** | — | **rank-recovery 92.6–97.5th pct robust; AUC target-dependent** | deep review windows (≥100) |
| Run-2 (FUTURE) | — | slot: e.g. seed-ensemble or context-length config | must beat paper on Mix AND prior runs on ≥3 genes |

## R3 — Approved-drug anchors (TTR)

**1. Published reference:** clinical approval of patisiran/vutrisiran (descriptive anchor, not per-sequence labels; sequences: FDA GINAS + EMA EPAR, decoded modification maps).

**2. Run config:** frozen v1.0 gates; TTR ENST00000237014.8; 598-window pool; site-rank audit.

**3. Results:** vutrisiran site **#62/598 (89.6th pct)**, patisiran **#107/598 (82.1st)**; efficacy bands coincide (RN.Ai median 84.5 drugs vs 84.3 ours); all 7 UGUGU-free. **Run-2 slot:** second anchor target when a verified published-design cohort exists.

## R4 — Application cohorts (scanner / allele / neuro)

**1. Published reference:** qualitative biology only (UGUGU⇒TLR7/8 IFN: PMIDs 15723075/15778705; mismatch-position discrimination: Schwarz/Sibley/Miller tables). **No published sensitivity/specificity or ΔΔG numbers exist** — Run-1 sets the references.

**2. Run config:** frozen scanner rules (no tuning after seeing outcomes); RNAduplex 37 °C weakest-of-3 mismatch; context-free RN.Ai for HTT.

**3. Results (Run-1):** scanner **spec 1.00 / sens 0.10** (n=13); allele ΔΔG **selective 6.7 vs weak 4.7** kcal/mol (Pearson 0.42, n=5 subset); HTT ρ **0.296** (n=26). **Run-2 slots:** e.g. GU-fraction threshold config for the scanner (must beat 0.10 sens at ≥0.9 spec, vs both the qualitative literature and Run-1).

## R5 — Manual vs sub-agent execution (head-to-head)

No external published reference exists — this benchmark is defined by internal iteration, and **v1→v2 already demonstrates the iteration contract**:

| Run | Config delta vs prior | Ordering (pooled AUC) | Delivery verdict |
|---|---|---|---|
| **Run-1** (v1) | initial: E4a **no-scope** (gene symbol unmatched) | A 0.569 / B 0.591 (HPSE only) | flawed M6 hits dimension (same-gene noise) — superseded, archived |
| **Run-2** (v2, definitive) | E4a **locus-scoped v1.2.1**; 4 genes; identical finalist budgets | A 0.569 [0.476–0.662] / B 0.591 [0.488–0.693] — CI-overlap tie | **sub-agent ≥ manual on every dimension** (seed-distinct 24/24, off-target max 0 vs 1, RN.Ai 86.1 vs 84.4) |
| Run-3 (FUTURE) | slot: e.g. RN.Ai-in-loop ordering config | must beat Run-2 numbers | compared against Run-2, Run-1 and the ceiling finding |

**Ceiling finding (standing):** neither execution layer beats the models it orchestrates on ordering; the agent layer's measurable value is guarantees + disclosure.

## R6 — Gate stack

Published reference: none (thresholds are provenance-tagged `user_operational`; GC band `literature_supported`). Run-1: conjunction keeps 75.9% of measured-effectives on Simone; viability gate most aggressive (12.4% cost). Run-2 slot: per-target calibrated thresholds (backlog #2/#3) — must show retained effectives ↑ without specificity loss.

---

*Config provenance: every run's thresholds = `config/thresholds.v1.0.frozen.json` unless a delta is stated; weights/vetoes per application = `tasks/*.request.example.json`; engine freezes v1.0–v1.2.1 in the source workspace. Add new runs as new rows — never overwrite a prior run's numbers.*

## R7 — Run-3 campaign reproduction (2026-11-11)

**PUBLISHED REFERENCE:** [Primary-paper curation and comparability report](011_Campaign-reproduction/Run-3_2026-11-11/REPORT.md). OligoFormer Mixset AUC 0.8163 is not the same endpoint/cohort as the RN.Ai Simone replay. Clinical outcomes are context, never per-sequence prediction ground truth.

**RUN CONFIG:** `Run-3_2026-11-11`: user-approved local fallback after one confirmed failed Boltzmann generation attempt; unchanged frozen gates; single-reference TTR/HK2/MYC/PCSK9/TNF; top-100 review and 24-candidate fresh battery per target; explicit both-strand screen and fail-closed application vetoes before requirement ranking. TTR/PCSK9/TNF generation is fresh; HK2/MYC full generation pools are reused with hashes. Panels are shared-target application frames, not independent biological validations.

**RESULTS TABLE:**

| Endpoint | Published | Prior run | Run-3 | Comparison |
|---|---|---|---|---|
| RN.Ai Simone AUC (n=322) | No matched published RN.Ai value verified | 0.7021 | 0.7021 | All 322 fresh predictions exactly reproduce prior scores |
| TTR projected drug-core ranks | Clinical anchors, no rank reference | 107 / 62 of 598 | 107 / 62 of 598 | Fresh full-pool generation reproduces ranks |
| HK2 OligoFormer AUC (n=95) | 0.8163 on different Mixset protocol | 0.6445 | 0.6445 | Historical OligoFormer pool; fresh RN.Ai AUC 0.7176 |
| HTT reporter RN.Ai Spearman (n=26) | IC50 outcomes, not predictor correlation | 0.296 | 0.2630 | Context recipe differs; no like-for-like improvement claim |
| HTT exact-mismatch ΔΔG vs log DR (21 uncensored) | No quantitative RNAduplex reference | Different weakest-of-three/KD% proxy | -0.3080 | Exact primary and secondary paper mismatch pairs; not a cellular selectivity claim |
| UGUGU sensitivity/specificity | Qualitative mechanism | 0.10 / 1.00 on different subset | 0.1429 / 1.00 (n=8) | Changed exclusions and deduplication; not tuned improvement |

Execution accounting: 11 task records; 9 partial application-panel bundles; 2 published-reporter EVALUATE tasks; 120 unique candidate batteries; 5,877 freshly generated and 9,311 reused windows. Panels contain 51 rows / 31 unique guides. No complete application task or biological validation is claimed: context/annotation stages remain unrun; allele/CNS DESIGN branches remain gated. See [task ledger](011_Campaign-reproduction/Run-3_2026-11-11/task_execution_status.csv), [counts](011_Campaign-reproduction/Run-3_2026-11-11/campaign_counts.json), and per-application `results/*/Run-3_2026-11-11/`.

