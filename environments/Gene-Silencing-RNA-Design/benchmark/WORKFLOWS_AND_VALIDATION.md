# Workflows, Tools & Validation — how each benchmark was produced

Structural companion to the case folders: for every **valid** benchmark (see the source workspace's `BENCHMARKS.md` validity ledger), this file records (a) the workflow executed, (b) the exact tools and their tiers, (c) the validation steps undergone, and (d) the execution mode — **manual** (tool-default operation, pre-existing Boltzmann stack) vs **sub-agent** (`sirna-design-specialist` protocol v1.2.1). Nothing here re-runs science; it documents provenance.

## Shared toolchain (all benchmarks; verified live 2026-11-05 — liveness report in source workspace `13_liveness/`)

| Tool | Version / pin | License tier | Verification undergone |
|---|---|---|---|
| OligoFormer + RNA-FM (generation) | ckpt SHA-256 pinned in freeze manifests | proprietary (research use; no redistribution) | mutation test (232/283 windows re-scored); clean label-tracking AUC 0.58–0.76 |
| RN.Ai-Predict (E2a) | Apache-2.0 keras ckpt | green | top/bottom-20 measured separation AUC 0.810; exact cross-path agreement |
| RNAiSpline (E2c) | no license | restricted — internal values only | separation AUC 0.769 (narrow range, documented) |
| ViennaRNA 2.7.2 (E3) | bioconda biotools env | permissive | deterministic; two-code-path exact agreement (50/50 guides) |
| bowtie2 2.5.5 + GENCODE v50 index (E4a, **locus-scoped v1.2.1**) | index pinned + hashed | GPLv3 binary-call | positive control (TTR guide → 20 TTR transcripts @0 mm); negative control (sense strand → 0); counts reproduce exactly |
| siSPOTR POTS (E4c) / 6merDB (E4d) / seed7 table (E4b) | frozen tables, pinned | Apache-2.0 / MIT | seed-dependent variation + cross-path exact |
| immune_scan.py (E5a, ours) | v1.2.1 in runtime/ | MIT | unit tests + cohort deciles; classification measured vs published IFN set (B4) |
| ToolUniverse 1.5.7 (E5b/d context) | uv venv py3.14 | Apache-2.0 | live Ensembl round-trip identical to local GENCODE transcript |
| RNAhybrid (E4e) | bioconda | — | **broken for SIREN flags; NOT_RUN(broken-binary), quarantined (backlog #4)** |

**Standing validation rules** (binding; from the validity ledger): pre-registered metrics before label join · locus-scoped E4a with stated scope · bootstrap CIs on every AUC · negative results published · supersession requires dated note + corrected re-run.

## B1 — Predictor validation (Simone-322, clean)

- **Workflow (sub-agent, EVALUATE mode):** parse Sciabola cohort → locate each guide's site on its transcript → extract real 57-nt context → RN.Ai via harness adapter → join labels post-hoc → AUC/Pearson/Spearman (cutoff 0.7).
- **Validation:** clean-cohort status per published training compositions; context quality logged (320 in-domain / 2 N-padded); no tuning; per-record predictions retained.
- **Result:** RN.Ai **AUC 0.7021 / P 0.507 / ρ 0.393** — independence gate lifted for the efficacy endpoint.

## B2 — Generator multi-target (HIF1A/HPSE/HK2/MYC, clean)

- **Workflow (both modes share generation; sub-agent adds battery+ranking):** OligoFormer on each transcript (16.8k windows total) → join measured tiling post-hoc → per-gene AUC + rank-recovery + bootstrap CIs.
- **Validation:** blind joins; envelope extension disclosed; degenerate-n (MYC) reported as degenerate; HPSE CI-includes-0.5 published as-is.
- **Result:** OF AUC 0.760/0.584/0.645/degen; measured-top-10 at median 92.6–97.5th pct → **rank-recovery is the robust capability**.

## B3 — Approved-drug anchors (descriptive)

- **Workflow (sub-agent, BENCHMARK mode):** GINAS/EPAR-verified drug sequences → per-gene GENCODE isoform selection by site containment → identical harness battery vs our TTR top-20 → site-rank audit against the 598-window pool.
- **Validation:** sequences triple-sourced (GINAS + EPAR + patent); intake-gate artifact documented (overhang format, backlog #1); same-side fairness (identical thresholds).
- **Result:** drug sites **#62/#107 of 598**; efficacy bands coincide (84.5 vs 84.3); all UGUGU-free.

## B4 — Application cohorts (curated: inflammation / allele / neuro)

- **Workflow (EVALUATE mode):** curated published sets (per-row verification flags) → immune scanner classification; RNAduplex ΔΔG (perfect vs weakest mismatch at published position); context-free RN.Ai vs −log10 IC50.
- **Validation:** image/paywalled rows excluded or flagged; scanner deliberately NOT tuned after seeing its low sensitivity.
- **Results:** UGUGU rule spec **1.00** / sens **0.10**; ΔΔG selective 6.7 vs weak 4.7 kcal/mol; HTT ρ **0.296** (degraded-input lower bound).

## B5 — Head-to-head (v1 amended + v2 definitive; manual vs sub-agent)

### Execution modes compared (the core of this file)

| Stage | **Manual arm** (what a Boltzmann-stack operator runs today) | **Sub-agent arm** (protocol v1.2.1) |
|---|---|---|
| Intake | no brief — platform defaults | requirement brief parsed, echoed, confirmed, hashed |
| Generation | same OligoFormer pools (identical inputs) | same |
| Filtering | frozen computable gates at defaults | same gates **+ immune vetoes** |
| Ordering | platform `rank_score` (equal weights, absolute normalization) | requirement-weighted **cohort-percentile S** (application weights) + mandatory ±25% stability |
| Finalist screens (equal budgets) | locus-scoped E4a + RN.Ai (real 57-nt context) | identical |
| Panel | top-6 of ranked list | **seed-distinct** top-6 |
| Disclosure | gate log + provenance (no composite caveat, no stability) | full contract: weights verbatim, stability, rank_score caveat, NOT_RUN reasons |

### Workflow executed (v2, large pool)

1. Pre-register protocol (metrics frozen before label join) → 2. compute shared pool dims (GC/immune/POTS/viability/seed-fold/duplex/accessibility — cross-path-validated) → 3. both arms filter + order the same 16,802-window pool → 4. top-40 finalists/gene/arm → 5. identical screens (320 bowtie2 + 320 RN.Ai) → 6. panels → 7. blind label join → 8. M1–M7 with bootstrap CIs → 9. confirmation layer: 290 finalists re-run through formal harness batteries (`runs_wf_*`, corrected gene symbols; 279/290 pass full gate stack).

### Validation steps undergone (v2)

- Scope A/B tests established locus semantics (v1's "hits at cap" was same-gene noise → superseded; archived).
- Cross-path exactness: pool dims vs platform battery (50/50 guides; viability/duplex exact, POTS ≤0.005).
- Blindness: selection fixed by stage-1 scores before any label access.
- CI overlap rule applied honestly → pooled ordering declared a tie.

### Result

Ordering: A 0.569 [0.476–0.662] vs B 0.591 [0.488–0.693] (tie). Delivery: **sub-agent ≥ manual on every dimension** — off-target max 0 vs 1, RN.Ai 86.1 vs 84.4, POTS 4.3 vs 6.5, seed-distinct 24/24 vs unenforced. Value = guarantees + disclosure.

## B6 — Gate-stack performance

- **Workflow:** frozen thresholds applied to the labeled Simone cohort + TTR decision matrices; conjunction and per-gate contingencies.
- **Validation:** thresholds provenance-tagged and untouched; gate-count correction (2/20→6/20) published.
- **Result:** full stack keeps 75.9% of measured-effectives; viability gate most aggressive (backlog #2).

## B7 — Explorer blind post-hoc

- **Workflow (EXPLORATORY mode):** multi-strategy partition → cheap funnel → tiered descent → brief-variant ranking → consensus panel; labels joined post-hoc only.
- **Validation:** blind selection verified; X3b re-anchoring trigger later shown to be scope-artifact → **retained as mechanism demonstration only** (superseded as benchmark evidence; archived).
- **Result:** 3/18 clean candidates measured **0.92/0.92/0.87** (base 0.785).
