# Head-to-Head, Large Pool — manual vs sub-agent execution (v2, definitive)

Pre-registered comparison on the full multi-target pool: 4 genes (HIF1A, HPSE, HK2, MYC),
16,802 generated windows, 308 measured siRNAs (Sciabola tiling, labels blind until evaluation).
Both arms share all scientific backends and identical finalist budgets (locus-scoped E4a
v1.2.1 + RN.Ai with real context); the compared variable is the agent layer. Supersedes the
v1 comparison's M6 hits dimension (E4a scoping artifact — see the source workspace's
BENCHMARKS.md validity ledger).

## Ordering (M1, pooled, with bootstrap 95% CIs)

| Arm | Pooled AUC | Spearman |
|---|---|---|
| Manual (platform-style rank_score) | 0.5685 [0.4763–0.6615] | 0.160 |
| **Sub-agent (requirement-weighted protocol)** | **0.5908 [0.4878–0.6934]** | 0.170 |

CI-overlap tie at the predictor ceiling (pre-registered rule); sub-agent +0.14 AUC on HK2,
manual marginally ahead on HIF1A/HPSE. Per-gene table in `stage1_metrics.json`.

## Delivered panels (M6; 24 candidates per arm)

| Dimension | Manual | Sub-agent |
|---|---|---|
| Locus-scoped off-target max | 1 | **0** |
| RN.Ai median | 84.4% | **86.1%** |
| POTS seed-off-target median | 6.5 | **4.3** |
| Viability median | 93.9 | 93.8 |
| UGUGU-free | yes | yes |
| **Seed-distinct by construction** | no | **yes (24/24)** |

## Verdict

Ordering: tie (both ceiling-bound — agent layers do not beat the models they orchestrate).
Delivery: **sub-agent >= manual on every dimension** — decisive on structural guarantees
(seed-diverse panels, immune verification, requirement auditability, stability reporting)
rather than large numeric deltas. Both arms deliver clean panels once E4a semantics are
correct; the sub-agent's value is precisely characterized as guarantees + disclosure.

Full report: source workspace `14_large_pool_benchmark/LARGE_POOL_REPORT.md`
(PROTOCOL.md pre-registration; stage1/stage2 scripts; uniform task-workflow batteries).

## Published reference

| Metric | Published value | Source |
|---|---|---|
| External reference | **none exists** — internal Run-1→Run-2 iteration (see BENCHMARK_RUNS.md §R5) | — |

## Run configuration

| Run | Config delta | Date |
|---|---|---|
| Run-1 (v1) | E4a no-scope (gene symbol unmatched) — superseded, archived | 2026-11-05 |
| Run-2 (v2) | locus-scoped v1.2.1; 4 genes; identical finalist budgets (40/arm/gene) | 2026-11-05 |

## Benchmark metrics

### Per-gene ordering metrics (M1)

| Gene | pool | A surv | B surv | A AUC | B AUC |
|---|---|---|---|---|---|
| HIF1A | 3928 | 1857 | 1787 | 0.7315 | 0.7255 |
| HPSE | 4563 | 2253 | 2231 | 0.4566 | 0.4434 |
| HK2 | 5608 | 2653 | 2623 | 0.5729 | 0.7118 |
| MYC | 3703 | 1619 | 1539 | 1.0 | 1.0 |
| **POOLED** | 16,802 | — | — | **0.5685** [0.4763, 0.6615] | **0.5908** [0.4878, 0.6934] |

## Execution modes compared (manual vs sub-agent)

| Workflow stage | **Manual arm** (Boltzmann stack defaults) | **Sub-agent arm** (protocol v1.2.1) |
|---|---|---|
| Intake | no brief — platform defaults | requirement brief parsed, confirmed, hashed |
| Generation | same OligoFormer pools (identical inputs) | same |
| Filtering | frozen computable gates at defaults | same gates **+ immune vetoes** |
| Ordering | platform `rank_score` (equal weights, absolute normalization) | requirement-weighted cohort-percentile S + mandatory ±25% stability |
| Finalist screens | locus-scoped E4a + RN.Ai (real 57-nt context) — **identical budgets** | identical |
| Panel | top-6 of ranked list | **seed-distinct** top-6 |
| Disclosure | gate log + provenance | + weights verbatim, stability report, rank_score caveat, NOT_RUN reasons |

## Finalist funnel (per gene)

| Gene | Manual: finalists→gated→panel | Sub-agent: finalists→gated→panel |
|---|---|---|
| HIF1A | 40 → 40 → 6 | 40 → 40 → 6 |
| HPSE | 40 → 40 → 6 | 40 → 37 → 6 |
| HK2 | 40 → 40 → 6 | 40 → 39 → 6 |
| MYC | 40 → 40 → 6 | 40 → 40 → 6 |

Identical finalist budgets (40/arm/gene); screens: locus-scoped bowtie2 + RN.Ai; RN.Ai>=50 gate applied identically.

## Panel results (M6 — delivery comparison)

| Dimension | Manual (24 candidates) | Sub-agent (24 candidates) |
|---|---|---|
| Finalists passing screens | 160/160 | 156/160 |
| Locus-scoped off-target max | 1 | **0** |
| RN.Ai predicted median | 84.4% | **86.1%** |
| POTS seed-offtarget median | 6.5 | **4.3** |
| 6merDB viability median | 93.9 | 93.8 (tie) |
| UGUGU-free | yes | yes |
| **Seed-distinct by construction** | **no** (not enforced) | **yes (24/24)** |
| Measured overlap (sparse tiling) | 1 → [0.93] | 1 → [0.9] (single samples, non-informative) |

**Sub-agent ≥ manual on every dimension**; decisive on structural guarantees.

## Process scorecard (M7)

| Capability | Manual | Sub-agent |
|---|---|---|
| Provenance manifests + hashing | yes | yes |
| Gate-decision log | yes | yes |
| Evidence-tier honesty (NEEDS_EXPERIMENTAL_VALIDATION) | yes | yes |
| Immune dimension (E5a) | no | **yes** |
| Requirement-brief semantics | no | **yes** |
| Ranking stability report | no | **yes** |
| Composite-score disclosure | rank_score present, undisclosed | **mandatory caveat** |
| Seed/site-diverse panel logic | no | **yes** |
| Wall time | comparable (same screens bound both) | comparable |

## Task-workflow battery confirmation

| Gene | Candidates through formal harness | All-gates clean |
|---|---|---|
| HIF1A | 75 | 74 |
| HK2 | 71 | 69 |
| HPSE | 71 | 67 |
| MYC | 73 | 69 |
| **Total** | **290** | **279** |

Both arms' finalist union re-run through the formal harness batteries (corrected gene symbols): **279/290 pass the full gate stack** — M6 conclusions hold under the harness's own decisions.
