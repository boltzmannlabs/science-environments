# 001 — Xiang-2021 clean-cohort on-target evaluation (Run-1, executed 2026-11-10)

First executed computational benchmark of the CRISPR-Design environment. Frozen local
endpoints, blind label join (labels fetched and joined only after all scores were
computed), bootstrap CIs, no tuning of any threshold or weight.

## Published reference

| Item | Value | Source |
| --- | --- | --- |
| Cohort | Xiang et al. 2021 *Nat Commun* 12:3238, TRAP12K surrogate library, HEK293T SpCas9, **Day10 +dox** measured `total_indel_eff` | paper supplementary 41467_2021_23576_MOESM4_ESM.xlsx (`spCas9_eff_D10+dox`, n=11,578) |
| CRISPRon published | internal independent-test Spearman **0.80**; external sets 0.46–0.68 | paper (own split) |
| Cross-tool context | non-training scores 0.34–0.44 (CRISPOR/Haeussler 2016); independent-data envelope 0.4–0.7 (Konstantakos 2022) | published benchmarks |
| Position in literature | Xiang-2021 is one of Konstantakos's 6 training-disjoint evaluation sets | NAR 50:3616 |

## Run configuration

- **Labels:** paper-supplementary `total_indel_eff` (Day10+dox), authoritative — NOT the
  GEO GSM read-count columns (a first-pass attempt using `1 − filter/raw` from the GEO
  xlsx produced |ρ|≈0.09 for every endpoint including CRISPRon, exposing the
  misinterpretation; the count columns are QC statistics, not editing rates — recorded
  here as a disclosed methodology correction).
- **Cohort:** n=11,461 after joining labels ↔ endpoints (NGG-only, raw-clean-reads as
  shipped in the sheet; 265 unjoined, all missingness disclosed).
- **Endpoints (local, frozen):** CRISPRon v1.0 (Zenodo, AGPL-3.0; TF 2.14 env;
  regression `TEST ok` before use) · RuleSet3-Sequence Hsu2013 (crisprScore 1.17.2,
  rs3-env pins) · RuleSet1 (crisprScore) · CRISPRater (crisprScore).
- **Exposure disclosure:** CRISPRon = **exposed** (this library is in its training data;
  we score the full set, not their held-out split). RS3 = **possibly-exposed** (2022
  model over pooled public corpora). RS1 (2014) / CRISPRater (2016) = **clean** (predate
  all cohorts).
- **Assay-noise ceiling (measured, not assumed):** Day8+dox vs Day10+dox
  `total_indel_eff` Spearman = **0.6149** (n=11,559) — the honest upper envelope for any
  predictor on this assay.

## Benchmark metrics

| Endpoint | Spearman ρ vs Day10+dox indel efficiency | 95% CI (bootstrap 1000×) | nDCG@20 | Exposure |
| --- | --- | --- | --- | --- |
| RS3-Sequence (Hsu2013) | **0.5157** | [0.5003–0.5303] | 0.0000* | possibly-exposed |
| CRISPRon | 0.5039 | [0.4887–0.5189] | 0.0000* | exposed (training library) |
| RuleSet1 | 0.2224 | [0.2044–0.2395] | 0.0000* | clean |
| CRISPRater | 0.0913 | [0.0724–0.1116] | 0.0000* | clean |
| *(ceiling)* replicate D8 vs D10 | 0.6149 | — | — | measured label noise |

\* nDCG@20 is degenerate at this cohort size (top-20 of 11.5k = 0.17% of the cohort;
even the replicate arm does not recover it). Konstantakos-style nDCG@20 needs
smaller cohorts (their HEL set: n=424) — queued for Run-2 with the remaining
Konstantakos sets.

## Interpretation (honest)

- The two modern models land at ~0.50–0.52, **83–84% of the measured assay-noise
  ceiling (0.615)** — consistent with CRISPRon's published external range (0.46–0.68)
  and with the field's independent-data envelope (0.4–0.7). Nothing here beats its
  training-informed published internal number (0.80), as expected: that figure uses the
  authors' own held-out split, not a full-set evaluation.
- Classical rules degrade sharply on this surrogate-library assay context (RS1 0.22;
  CRISPRater 0.09) — consistent with the CRISPOR finding that score transfer is
  assay- and expression-system-dependent (U6-trained rules vs TRAP library context).
- **Practical consequence for our environment:** CRISPRon and RS3 are the two
  load-bearing on-target endpoints for task 002 (both now local); RS1/CRISPRater
  remain reported as comparator columns, never as primary evidence in this assay class.

## Workflow

[WORKFLOW.py](WORKFLOW.py) — cohort build, endpoint join (by exact 30-mer string:
CRISPRon enumerates every NGG window per record), Spearman + bootstrap CI + nDCG@20.
Raw artifacts: [benchmark_joined_authoritative.csv](benchmark_joined_authoritative.csv),
[benchmark_metrics.json](benchmark_metrics.json). Source data retained in the curation
workspace (`~/IMRAN/NOV26/cirspr-sci-env/02_benchmarks/{datasets,runs}/xiang2021*`,
`datasets/crispron_paper/supp4.xlsx`); GEO GSE173708 RAW tar + paper supplement URLs in
provenance below.

## Provenance

- Labels: 41467_2021_23576_MOESM4_ESM.xlsx (springer static-content, fetched 2026-11-10)
- Cohort cross-check: GEO GSE173708 GSM5277230 (RAW tar, fetched 2026-11-10)
- CRISPRon: Zenodo 10.5281/zenodo.4725572 (v1.0, AGPL-3.0) + github.com/RTH-tools/crispron
  (regression test `TEST ok` 2026-11-10); CRISPRoff features via
  github.com/RTH-tools-admin/crisproff (GPL-3.0)
- RS1/RS3/CRISPRater: crisprScore 1.17.2 (Bioconductor), rs3-env exact pins
- No threshold, weight or endpoint was tuned against these labels at any point
  (labels joined after scoring; metrics code fixed before join).
