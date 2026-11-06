# Status

**Lifecycle:** In Progress. **Protocol:** v1.2 (engine freeze `engine-v1.2.0_protocol-v1.2` + v1.2.1 scope-explicit E4a patch; gates frozen at v1.0). **Contribution status:** owner/reviewers/issue pending; root-repo registration done (canonical repo trees + status paragraph; NOV26 clone research-index row).

## Implemented and evidenced

- **Protocol stack:** 5 modes (DESIGN / EVALUATE / EXPLORATORY / BENCHMARK / AUDIT) · 10 active application profiles (antiviral review-only; plant/pest inactive) · requirement-brief contract (confirmed, hashed; tighten-only floors) · staged requirement-aware ranking with mandatory ±25% stability · explorer loop (X1–X5) with PROPOSED constraint re-anchoring · scope-explicit E4a (v1.2.1: `--target-gene` + loud warning).
- **Tasks:** 11 task documents (general + 10 applications), each with application-specific stages/vetoes/weights, complete example request briefs (real transcript accessions, substantive success criteria, illustrative-only markers), and stated benchmark status.
- **Component validation:** liveness audit — every model/tool proven non-dummy (mutation tests, label separation, positive/negative controls, live-API round-trip); cross-path exact agreement; e2e component checks 11/12 + integration micro-run reproducing known values; **E4e RNAhybrid quarantined** (`NOT_RUN(broken-binary)`).
- **Executed benchmarks** (all clean-cohort or curated-public; frozen engines; blind label joins; bootstrap CIs; see [BENCHMARK_RUNS.md](benchmark/BENCHMARK_RUNS.md) for the published-vs-run-iteration structure):
  - Predictor: clean Simone-322 **AUC 0.7021** (vs registry 0.808 exposed; Mix replay 0.8195).
  - Generator: Mix 0.8437 vs paper 0.8163; clean HIF1A **0.760 [0.615–0.877]**; cross-target **rank-recovery 92.6–97.5th pct robust, AUC target-dependent**.
  - Approved-drug anchors: **#62/#107 of 598**; same-side bands coincide; 7/7 UGUGU-free.
  - Application cohorts: scanner spec 1.00/sens 0.10 (not tuned); allele ΔΔG 6.7 vs 4.7; HTT ρ 0.296.
  - **Head-to-head v2 (definitive):** ordering CI-overlap tie at predictor ceiling (A 0.569 vs B 0.591); delivery **sub-agent ≥ manual on every dimension** (seed-distinct 24/24, locus off-target max 0 vs 1, RN.Ai 86.1 vs 84.4, POTS 4.3 vs 6.5); harness confirmation 279/290 gate-clean.
- **Benchmark governance:** validity ledger (valid B1–B7 / superseded), scoping-artifact archive with dated supersession, per-case metrics tables, [WORKFLOWS_AND_VALIDATION.md](benchmark/WORKFLOWS_AND_VALIDATION.md) (per-benchmark workflows → tools → validation → execution modes), run-iteration contract (published | Run-N | Δ tables).

## Not established

No wet-lab validation of any candidate; no delivery/chemistry prediction (none exists publicly); plant/pest and antiviral execution remain gated; ASO models excluded from siRNA scoring; ordering performance is bounded by the underlying models (ceiling finding) — agent value is guarantees + disclosure.

## Open backlog

1. Overhang-tolerant input gate (clinical-format duplexes reject at intake).
2. 6merDB viability-threshold evidence review (removes 12.4% of measured-effectives).
3. Per-target off-target gate calibration (scope now pinned by v1.2.1; threshold calibration open).
4. E4e RNAhybrid adapter/build fix (quarantined).
5. ~~Scope must fail loud~~ **shipped in v1.2.1** (remaining: harness-side warning on unmatched symbols).

## Source workspace

`~/IMRAN/NOV26/siRNA-Design-Task-Specific` — curation, freezes, validation program, case studies, liveness audit, head-to-head v1/v2, master validity ledger (`BENCHMARKS.md`). Both repo copies (canonical `~/IMRAN/science-environments` and `~/IMRAN/NOV26/science-environments`) are kept in sync.
