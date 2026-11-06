# Oncology — HPSE and HK2 end-to-end case studies (public measured data)

Two clean-cohort DESIGN runs in the oncology frame, replicating the case-study pattern on
Sciabola/Simone Hep3B measured siRNAs (labels joined post-hoc; frozen engine, no tuning).

| Gene (application relevance) | n joined / pos | OligoFormer AUC/P | RN.Ai AUC/P | measured-top-10 median pct |
|---|---|---|---|---|
| HPSE NM_001098540.3 (heparanase; invasion) | 106 / 76 | 0.5838 / 0.2981 | 0.6366 / 0.4741 | **94.5th** |
| HK2 NM_000189.5 (hexokinase-2; tumor glycolysis) | 95 / 73 | 0.6445 / 0.3079 | 0.7176 / 0.4319 | **95.1st** |

Cross-target reading (with HIF1A, TTR): **rank-recovery (92–98th pct) is the robust
capability**; per-sequence AUC is target-dependent (0.58–0.78). For oncology panels this
argues for deep review windows (>=100) over single-sequence discrimination. EZH2 (n=9) and
CTNNB1 (n=5) measured cohorts exist locally and remain in reserve. Generation pools:
`~/IMRAN/NOV26/siRNA-Design-Task-Specific/11_app_benchmarks/{hpse,hk2}/` (external, indexed).

## Published reference

| Metric | Published value | Source |
|---|---|---|
| Per-gene (HPSE/HK2) reference | **none exists** — Run-1 sets references | — |
| OligoFormer paper (cross-protocol context only) | 0.8163 | PMID 39321261 |

## Run configuration

| Run | Config | Date |
|---|---|---|
| Run-1 | same engine; full pools 4,563/5,608 windows; oncology weights .35/.35/.15/.10/.05; blind post-hoc joins; bootstrap CIs | 2026-11-05 |

## Benchmark metrics

| Gene | n / pos | OligoFormer AUC [95% CI] | RN.Ai AUC [95% CI] | top-10 recovery |
|---|---|---|---|---|
| HPSE | 106 / 76 | 0.5838  | 0.6366  | 94.5th |
| HK2 | 95 / 73 | 0.6445  | 0.7176  | 95.1th |

Reading: rank-recovery robust (94.5th/95.1st); per-sequence AUC target-dependent — HPSE CI includes 0.5 (disclosed).
