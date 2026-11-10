# BENCHMARK_RUNS — published references vs Run-N iteration registry

Iteration structure: every benchmark row carries **published reference | Run-N
configuration | results**, with future Run slots explicit. **As of 2026-11-10 no Run
exists** — all slots are `NOT_EXECUTED`; rows become live only when the runtime +
calibration phases deliver executed artifacts (frozen engine version, blind label join,
no-tuning attestation, bootstrap CIs).

## 1. KO on-target clean evaluation (protocol: Konstantakos-2022 replication)

| Stage | Content |
| --- | --- |
| Published reference | CRISPRon internal ρ 0.80 vs Azimuth 0.56 / DeepSpCas9 0.73 / DeepHF 0.74 (Xiang 2021); Konstantakos 2022 independent ranking (DeepHF/DeepSpCas9 top; ceiling ρ≈0.7) |
| Run-1 configuration | `NOT_EXECUTED` — planned: local endpoints {DeepSpCas9, RS2 via crisprScore; CRISPRon} on Kim-2019 held-out + Konstantakos 6-disjoint-set protocol; Spearman + nDCG@20; bootstrap CIs; frozen engine stamp |
| Run-1 results | `NOT_EXECUTED` |
| FUTURE slots | Run-2: RS3 addition after install · Run-3: DeepHF variant arm |

## 2. Off-target pair-scoring (protocol: Kaufmann-2026-style recall@K)

| Stage | Content |
| --- | --- |
| Published reference | Kaufmann 2026: recall ≈77% @ top-500, ≈83% @ top-1,250; weak score↔indel correlation (14 tools) |
| Run-1 configuration | `NOT_EXECUTED` — planned: CFD + Elevation (CRISOT optional, research-internal) on CHANGE-seq 110-guide set; recall@K + PR-AUC; GUIDE-seq as cell-based truth layer |
| Run-1 results | `NOT_EXECUTED` |
| FUTURE slots | Run-2: CRISPRitz bulge-aware arm · Run-3: CRISPRme variant layer |

## 3. Base-editing outcome prediction

| Stage | Content |
| --- | --- |
| Published reference | BE-Hive outcome R≈0.9 / efficiency R≈0.7 (Arbab 2020); BEDICT2.0 R 0.60–0.94 (2025); DeepBE editor-choice gains 2.9–20× (2024) |
| Run-1 configuration | `NOT_EXECUTED` — planned: BEDICT2.0 + DeepBE on BE-dataHIVE held-out editors; intended-fraction + purity metrics |
| Run-1 results | `NOT_EXECUTED` |
| FUTURE slots | Run-2: bystander-model arm (BE-Hive CLI) |

## 4. Prime-editing intended-edit prediction

| Stage | Content |
| --- | --- |
| Published reference | PRIDICT2.0 ρ 0.85 intended / 0.78 purity on 92,423 pegRNAs (Mathis 2023) |
| Run-1 configuration | `NOT_EXECUTED` — planned: self-hosted PRIDICT2.0 CLI on Mathis held-out split; DeepPrime cross-check on shared PE systems (license check first) |
| Run-1 results | `NOT_EXECUTED` |
| FUTURE slots | Run-2: pegRNA design-vs-prediction round trip |

## 5. Application-layer anchors (same-side, later phases)

| Stage | Content |
| --- | --- |
| Published reference | Horlbeck 2016 γ-scores (CRISPRi) · Nuñez 2021 GSE168012 rules (CRISPRoff) · TIGER corpus (Cas13) · EasyDesign ρ 0.812 (diagnostics, contrived targets only) · RS3 tiling 84,609 (libraries) |
| Run-1 configuration | `NOT_EXECUTED` — planned per task after P0/P1 installs |
| Run-1 results | `NOT_EXECUTED` |

## No-tuning attestation (to be recorded at first freeze)

Thresholds, weights and rules will be frozen before evaluation (see
[config/thresholds.v0.1.draft.json](../config/thresholds.v0.1.draft.json)
`no_freeze_without` list); no retrospective outcome may influence any parameter. Until
then, every deliverable carries the DRAFT-gates disclosure.
